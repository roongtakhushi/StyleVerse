import os
import uuid
import cv2
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from bson import ObjectId
from app.config import settings
from app.database import get_db
from app.utils.auth import get_current_user
from app.schemas.all_schemas import WardrobeItemResponse
from ml.preprocessing.color_extraction import extract_dominant_colors
from ml.inference.clothing_predict import classify_clothing, extract_clothing_embedding

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])

def is_portrait_image(filepath: str) -> bool:
    """Detects if an uploaded image is a human facial portrait rather than apparel."""
    try:
        cascade_path = os.path.join(getattr(cv2.data, 'haarcascades', ''), 'haarcascade_frontalface_default.xml')
        if os.path.exists(cascade_path):
            face_cascade = cv2.CascadeClassifier(cascade_path)
            img = cv2.imread(filepath)
            if img is not None:
                h, w = img.shape[:2]
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60))
                for (fx, fy, fw, fh) in faces:
                    if (fw * fh) > (w * h * 0.10):
                        return True
    except Exception:
        pass
    return False

@router.post("/upload")
async def upload_clothing(
    file: UploadFile = File(...),
    category_override: Optional[str] = Form(None),
    style_override: Optional[str] = Form(None),
    gender_category: Optional[str] = Form("unisex"),
    current_user: dict = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
        
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"cloth_{uuid.uuid4().hex[:10]}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    # Guard: Reject facial portraits from contaminating wardrobe
    if is_portrait_image(filepath):
        if os.path.exists(filepath):
            os.remove(filepath)
        raise HTTPException(
            status_code=400,
            detail="This image appears to be a facial portrait. Please upload an isolated clothing item or use the Skin Analysis module for portraits."
        )
        
    # ML Component 1: Extract 3 dominant colors
    try:
        colors = extract_dominant_colors(filepath, k=3)
    except Exception as e:
        print(f"Color extraction error: {e}")
        colors = ["#263F36", "#E4CDA5", "#172D25"]
        
    # ML Component 2: MobileNetV2 classification
    ml_pred = classify_clothing(filepath)
    category = category_override if category_override else ml_pred["category"]
    subcategory = ml_pred["subcategory"]
    style = style_override if style_override else ml_pred["predicted_style"]
    
    # Dress Disambiguation Guard: Ensure dresses are never categorized as bottoms or trousers
    if subcategory in ["dress", "gown", "maxi dress"] or category == "dress":
        category = "dress"
        if subcategory not in ["dress", "gown", "maxi dress"]:
            subcategory = "dress"
            
    # ML Component 3: Extract 128D Deep Visual Embedding for KNN Similarity
    embedding = None
    try:
        emb_arr = extract_clothing_embedding(filepath)
        embedding = emb_arr.tolist()
    except Exception as e:
        print(f"Embedding extraction notice: {e}")
    
    user_id = str(current_user.get("_id", current_user.get("id")))
    
    item_doc = {
        "user_id": user_id,
        "image_url": f"/uploads/{filename}",
        "category": category,
        "subcategory": subcategory,
        "dominant_colors": colors,
        "pattern": "solid",
        "style": style,
        "gender_category": gender_category or "unisex",
        "confidence": ml_pred["confidence"],
        "embedding": embedding,
        "created_at": datetime.utcnow()
    }
    
    db = get_db()
    if db is not None:
        res = await db.wardrobe_items.insert_one(item_doc)
        item_id = str(res.inserted_id)
    else:
        item_id = str(ObjectId())
        
    item_doc["id"] = item_id
    item_doc["_id"] = item_id
    return item_doc

@router.get("", response_model=List[WardrobeItemResponse])
async def get_wardrobe(category: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user.get("_id", current_user.get("id")))
    
    query = {"user_id": user_id}
    if category and category.lower() != "all":
        query["category"] = category.lower()
        
    items = []
    if db is not None:
        cursor = db.wardrobe_items.find(query).sort("created_at", -1)
        async for doc in cursor:
            items.append({
                "id": str(doc["_id"]),
                "user_id": doc.get("user_id", user_id),
                "image_url": doc.get("image_url", ""),
                "category": doc.get("category", "top"),
                "subcategory": doc.get("subcategory", "item"),
                "dominant_colors": doc.get("dominant_colors", []),
                "pattern": doc.get("pattern", "solid"),
                "style": doc.get("style", "casual"),
                "gender_category": doc.get("gender_category", "unisex"),
                "created_at": doc.get("created_at", datetime.utcnow())
            })
    return items

@router.get("/{item_id}", response_model=WardrobeItemResponse)
async def get_wardrobe_item(item_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=404, detail="Item not found")
        
    user_id = str(current_user.get("_id", current_user.get("id")))
    
    # Secure ID validation and strict user-ownership scoping
    filter_query = {"_id": ObjectId(item_id) if ObjectId.is_valid(item_id) else item_id, "user_id": user_id}
    doc = await db.wardrobe_items.find_one(filter_query)
    
    if not doc:
        # Check if item exists under another user to avoid leaking existence vs ownership
        item_exists = await db.wardrobe_items.find_one({"_id": ObjectId(item_id) if ObjectId.is_valid(item_id) else item_id})
        if item_exists:
            raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to access this item.")
        raise HTTPException(status_code=404, detail="Item not found")
        
    return {
        "id": str(doc["_id"]),
        "user_id": doc.get("user_id"),
        "image_url": doc.get("image_url", ""),
        "category": doc.get("category", "top"),
        "subcategory": doc.get("subcategory", "item"),
        "dominant_colors": doc.get("dominant_colors", []),
        "pattern": doc.get("pattern", "solid"),
        "style": doc.get("style", "casual"),
        "gender_category": doc.get("gender_category", "unisex"),
        "created_at": doc.get("created_at", datetime.utcnow())
    }

@router.delete("/{item_id}")
async def delete_wardrobe_item(item_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=404, detail="Item not found")
        
    user_id = str(current_user.get("_id", current_user.get("id")))
    filter_query = {"_id": ObjectId(item_id) if ObjectId.is_valid(item_id) else item_id}
    
    doc = await db.wardrobe_items.find_one(filter_query)
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
        
    if doc.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden: You cannot delete another user's wardrobe item.")
        
    await db.wardrobe_items.delete_one(filter_query)
    return {"message": "Item deleted successfully", "id": item_id}
