from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.utils.auth import get_current_user
from app.schemas.all_schemas import UserResponse, StylePreferencesUpdate, StyleProfileResponse
from bson import ObjectId

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user.get("_id", current_user.get("id"))),
        "name": current_user.get("name", "User"),
        "email": current_user.get("email", ""),
        "gender_preference": current_user.get("gender_preference", "unisex"),
        "created_at": current_user.get("created_at")
    }

@router.put("/preferences")
async def update_preferences(prefs: StylePreferencesUpdate, current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user.get("_id", current_user.get("id")))
    
    update_data = {}
    if prefs.preferred_styles is not None:
        update_data["preferred_styles"] = prefs.preferred_styles
    if prefs.preferred_occasions is not None:
        update_data["preferred_occasions"] = prefs.preferred_occasions
    if prefs.favourite_colors is not None:
        update_data["favourite_colors"] = prefs.favourite_colors
        
    if db is not None:
        if prefs.gender_preference:
            await db.users.update_one({"_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id}, {"$set": {"gender_preference": prefs.gender_preference}})
        if update_data:
            await db.style_profiles.update_one({"user_id": user_id}, {"$set": update_data}, upsert=True)
            
    return {"message": "Preferences updated successfully", "preferences": update_data}

@router.get("/profile", response_model=StyleProfileResponse)
async def get_style_profile(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = str(current_user.get("_id", current_user.get("id")))
    if db is not None:
        profile = await db.style_profiles.find_one({"user_id": user_id})
        if profile:
            return {
                "user_id": user_id,
                "skin_tone_estimate": profile.get("skin_tone_estimate", "medium"),
                "undertone": profile.get("undertone", "neutral"),
                "undertone_confirmed": profile.get("undertone_confirmed", False),
                "preferred_styles": profile.get("preferred_styles", ["casual", "streetwear"]),
                "preferred_occasions": profile.get("preferred_occasions", ["college", "daily"]),
                "colour_palette": profile.get("colour_palette", ["#263F36", "#B47A57", "#E4CDA5", "#8C5835"]),
                "favourite_colors": profile.get("favourite_colors", [])
            }
    return {
        "user_id": user_id,
        "skin_tone_estimate": "medium",
        "undertone": "neutral",
        "undertone_confirmed": False,
        "preferred_styles": ["casual", "streetwear"],
        "preferred_occasions": ["college", "daily"],
        "colour_palette": ["#263F36", "#B47A57", "#E4CDA5", "#8C5835"],
        "favourite_colors": []
    }

