from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.database import get_db
from app.utils.auth import get_current_user
from app.schemas.all_schemas import OutfitPlanRequest

router = APIRouter(tags=["Planner & Dashboard"])

@router.post("/planner")
async def schedule_outfit(plan_in: OutfitPlanRequest, current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user.get("_id", current_user.get("id")))
    
    plan_doc = {
        "user_id": user_id,
        "date": plan_in.date,
        "occasion": plan_in.occasion,
        "outfit_id": plan_in.outfit_id,
        "status": plan_in.status or "planned",
        "updated_at": datetime.utcnow()
    }
    
    if db is not None:
        await db.outfit_plans.update_one(
            {"user_id": user_id, "date": plan_in.date},
            {"$set": plan_doc},
            upsert=True
        )
        
    return {"message": "Outfit scheduled successfully", "plan": plan_doc}

@router.get("/planner/weekly")
async def get_weekly_planner(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user.get("_id", current_user.get("id")))
    
    plans = []
    if db is not None:
        cursor = db.outfit_plans.find({"user_id": user_id}).sort("date", 1).limit(14)
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            if isinstance(doc.get("updated_at"), datetime):
                doc["updated_at"] = doc["updated_at"].isoformat()
            plans.append(doc)
    return {"plans": plans}

@router.get("/dashboard")
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user.get("_id", current_user.get("id")))
    
    wardrobe_count = 0
    saved_count = 0
    recent_items = []
    profile_data = {}
    
    if db is not None:
        wardrobe_count = await db.wardrobe_items.count_documents({"user_id": user_id})
        saved_count = await db.saved_outfits.count_documents({"user_id": user_id})
        
        cursor = db.wardrobe_items.find({"user_id": user_id}).sort("created_at", -1).limit(4)
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            if isinstance(doc.get("created_at"), datetime):
                doc["created_at"] = doc["created_at"].isoformat()
            recent_items.append(doc)
            
        profile = await db.style_profiles.find_one({"user_id": user_id})
        if profile:
            profile_data = {
                "skin_tone": profile.get("skin_tone_estimate", "medium"),
                "undertone": profile.get("undertone", "neutral"),
                "colour_palette": profile.get("colour_palette", ["#263F36", "#B47A57", "#E4CDA5", "#8C5835"]),
                "undertone_confirmed": profile.get("undertone_confirmed", False)
            }
            
    if not profile_data:
        profile_data = {
            "skin_tone": "medium",
            "undertone": "neutral",
            "colour_palette": ["#263F36", "#B47A57", "#E4CDA5", "#8C5835"],
            "undertone_confirmed": False
        }
        
    return {
        "user": {
            "name": current_user.get("name", "Fashion Enthusiast"),
            "email": current_user.get("email", "")
        },
        "stats": {
            "wardrobe_count": wardrobe_count,
            "saved_outfits_count": saved_count,
            "palettes_active": len(profile_data.get("colour_palette", []))
        },
        "profile": profile_data,
        "recent_uploads": recent_items
    }

