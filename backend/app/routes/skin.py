import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.config import settings
from app.database import get_db
from app.utils.auth import get_current_user
from app.schemas.all_schemas import SkinAnalysisResponse, SkinToneConfirm
from ml.inference.skin_detector import analyze_face_skin
from ml.inference.skin_analysis import get_recommended_palettes

router = APIRouter(prefix="/skin", tags=["Skin Analysis"])

@router.post("/analyze", response_model=SkinAnalysisResponse)
async def analyze_skin(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")
    
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"face_{uuid.uuid4().hex[:10]}{file_ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    try:
        result = analyze_face_skin(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skin analysis failure: {str(e)}")
        
    db = get_db()
    if db is not None:
        user_id = str(current_user.get("_id", current_user.get("id")))
        await db.style_profiles.update_one(
            {"user_id": user_id},
            {"$set": {
                "skin_tone_estimate": result["estimated_skin_tone"],
                "undertone": result["estimated_undertone"],
                "sample_hex": result["sample_hex"],
                "colour_palette": result["primary_palette"],
                "undertone_confirmed": False
            }},
            upsert=True
        )
        
    return result

@router.put("/confirm")
async def confirm_undertone(data: SkinToneConfirm, current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user.get("_id", current_user.get("id")))
    
    tone = data.skin_tone or "medium"
    palette_info = get_recommended_palettes(data.undertone, tone)
    
    if db is not None:
        await db.style_profiles.update_one(
            {"user_id": user_id},
            {"$set": {
                "undertone": data.undertone,
                "skin_tone_estimate": tone,
                "undertone_confirmed": True,
                "colour_palette": palette_info["primary_palette"]
            }},
            upsert=True
        )
        
    return {
        "message": "Undertone and personalized palette updated successfully.",
        "undertone": data.undertone,
        "skin_tone": tone,
        "primary_palette": palette_info["primary_palette"],
        "palettes": palette_info["palettes"]
    }

@router.get("/palette")
async def get_user_palette(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user.get("_id", current_user.get("id")))
    
    if db is not None:
        profile = await db.style_profiles.find_one({"user_id": user_id})
        if profile and profile.get("colour_palette"):
            return {
                "undertone": profile.get("undertone", "neutral"),
                "skin_tone": profile.get("skin_tone_estimate", "medium"),
                "primary_palette": profile.get("colour_palette"),
                "palettes": get_recommended_palettes(profile.get("undertone", "neutral"), profile.get("skin_tone_estimate", "medium"))["palettes"]
            }
            
    # Default fallback
    info = get_recommended_palettes("neutral", "medium")
    return info

