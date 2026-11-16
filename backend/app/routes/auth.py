from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from app.database import get_db
from app.schemas.all_schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from app.utils.auth import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(user_in: UserRegister):
    db = get_db()
    email_clean = user_in.email.strip().lower()
    if db is not None:
        existing = await db.users.find_one({"email": {"$regex": f"^{email_clean}$", "$options": "i"}})
        if existing:
            raise HTTPException(status_code=400, detail="An account with this email already exists.")
        
        user_doc = {
            "name": user_in.name.strip(),
            "email": email_clean,
            "password_hash": get_password_hash(user_in.password),
            "gender_preference": user_in.gender_preference or "unisex",
            "created_at": datetime.utcnow()
        }
        res = await db.users.insert_one(user_doc)
        user_id = str(res.inserted_id)
        
        # Initialize default style profile
        await db.style_profiles.insert_one({
            "user_id": user_id,
            "skin_tone_estimate": "medium",
            "undertone": "neutral",
            "undertone_confirmed": False,
            "preferred_styles": ["casual", "streetwear"],
            "preferred_occasions": ["college", "daily"],
            "colour_palette": ["#263F36", "#B47A57", "#E4CDA5", "#8C5835"]
        })
    else:
        user_id = str(ObjectId())
        
    access_token = create_access_token({"sub": user_id, "email": email_clean, "name": user_in.name})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": user_in.name,
            "email": email_clean,
            "gender_preference": user_in.gender_preference or "unisex",
            "created_at": datetime.utcnow()
        }
    }

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    db = get_db()
    email_clean = credentials.email.strip().lower()
    if db is not None:
        user = await db.users.find_one({"email": {"$regex": f"^{email_clean}$", "$options": "i"}})
        if not user or not verify_password(credentials.password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        user_id = str(user["_id"])
        name = user.get("name", "User")
        gender_pref = user.get("gender_preference", "unisex")
        created_at = user.get("created_at", datetime.utcnow())
    else:
        # Fallback offline mode
        user_id = str(ObjectId())
        name = "Fashion User"
        gender_pref = "unisex"
        created_at = datetime.utcnow()
        
    token = create_access_token({"sub": user_id, "email": email_clean, "name": name})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": name,
            "email": email_clean,
            "gender_preference": gender_pref,
            "created_at": created_at
        }
    }

