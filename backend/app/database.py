import os
import shutil
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config import settings

class Database:
    client = None
    db = None
    is_fallback: bool = False

db_instance = Database()

COLLECTIONS = [
    "users",
    "style_profiles",
    "wardrobe_items",
    "outfit_recommendations",
    "saved_outfits",
    "outfit_plans"
]

FALLBACK_GARMENTS = [
    {
        "name": "White Crewneck T-Shirt",
        "filename": "white_crewneck_tshirt.jpg",
        "category": "top",
        "subcategory": "t-shirt",
        "gender_category": "unisex",
        "style": "casual",
        "dominant_colors": ["#FFFFFF", "#E2E8F0", "#CBD5E1"],
        "occasions": ["daily", "casual", "college"]
    },
    {
        "name": "Navy Oxford Button-Up",
        "filename": "navy_oxford_shirt.jpg",
        "category": "top",
        "subcategory": "shirt",
        "gender_category": "unisex",
        "style": "smart_casual",
        "dominant_colors": ["#1E293B", "#334155", "#0F172A"],
        "occasions": ["formal", "office", "casual"]
    },
    {
        "name": "Blue Selvedge Denim Jeans",
        "filename": "blue_selvedge_jeans.jpg",
        "category": "bottom",
        "subcategory": "jeans",
        "gender_category": "unisex",
        "style": "casual",
        "dominant_colors": ["#1D4ED8", "#1E40AF", "#3B82F6"],
        "occasions": ["daily", "casual", "college"]
    },
    {
        "name": "Black Tailored Slim Trousers",
        "filename": "black_tailored_trousers.jpg",
        "category": "bottom",
        "subcategory": "trousers",
        "gender_category": "unisex",
        "style": "formal",
        "dominant_colors": ["#000000", "#18181B", "#27272A"],
        "occasions": ["formal", "business", "college"]
    },
    {
        "name": "White Leather Court Sneakers",
        "filename": "white_leather_sneakers.jpg",
        "category": "footwear",
        "subcategory": "sneakers",
        "gender_category": "unisex",
        "style": "casual",
        "dominant_colors": ["#F8FAFC", "#E2E8F0", "#94A3B8"],
        "occasions": ["daily", "casual", "college", "streetwear"]
    },
    {
        "name": "Classic Brown Leather Oxfords",
        "filename": "brown_leather_oxfords.jpg",
        "category": "footwear",
        "subcategory": "shoes",
        "gender_category": "unisex",
        "style": "formal",
        "dominant_colors": ["#78350F", "#92400E", "#B45309"],
        "occasions": ["formal", "business"]
    },
    {
        "name": "Black Biker Leather Jacket",
        "filename": "black_leather_jacket.jpg",
        "category": "outerwear",
        "subcategory": "jacket",
        "gender_category": "unisex",
        "style": "streetwear",
        "dominant_colors": ["#09090B", "#18181B", "#27272A"],
        "occasions": ["casual", "night_out", "party"]
    },
    {
        "name": "Tailored Camel Coat",
        "filename": "camel_trench_coat.jpg",
        "category": "outerwear",
        "subcategory": "coat",
        "gender_category": "unisex",
        "style": "formal",
        "dominant_colors": ["#b06c52", "#613424", "#e0b99d"],
        "occasions": ["formal", "business", "casual"]
    },
    {
        "name": "Red Floral Summer Wrap Dress",
        "filename": "red_summer_wrap_dress.jpg",
        "category": "dress",
        "subcategory": "dress",
        "gender_category": "women",
        "style": "casual",
        "dominant_colors": ["#d7a15c", "#c41428", "#65251e"],
        "occasions": ["daily", "casual", "brunch", "vacation"]
    },
    {
        "name": "Purple Off-Shoulder Gown",
        "filename": "emerald_midi_dress.jpg",
        "category": "dress",
        "subcategory": "gown",
        "gender_category": "women",
        "style": "formal",
        "dominant_colors": ["#7b6fb4", "#350c24", "#e6c7b5"],
        "occasions": ["party", "formal", "evening"]
    }
]

async def seed_resilient_database(db):
    """Pre-seeds test accounts and clean studio wardrobe items into the resilient store."""
    from app.utils.auth import get_password_hash
    
    # 1. Seed users
    users_to_seed = [
        {"name": "Khushi", "email": "khushi@styleverse.com", "gender": "unisex"},
        {"name": "Khushi Test", "email": "khushi.test1@styleverse.com", "gender": "women"}
    ]
    
    seeded_user_ids = []
    for u in users_to_seed:
        user_doc = {
            "name": u["name"],
            "email": u["email"],
            "password_hash": get_password_hash("Password123!"),
            "gender_preference": u["gender"],
            "created_at": datetime.utcnow()
        }
        res = await db.users.insert_one(user_doc)
        uid = str(res.inserted_id)
        seeded_user_ids.append(uid)
        
        # Profile
        await db.style_profiles.insert_one({
            "user_id": uid,
            "skin_tone_estimate": "fair",
            "undertone": "warm",
            "undertone_confirmed": True,
            "preferred_styles": ["casual", "streetwear"],
            "preferred_occasions": ["college", "daily"],
            "colour_palette": ["#263F36", "#B47A57", "#E4CDA5", "#8C5835", "#C49A45", "#80382B", "#C07D38", "#4A5D23"]
        })
        
    # 2. Seed wardrobe items
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cutouts_dir = os.path.join(project_root, "test_samples", "studio_cutouts")
    uploads_dir = os.path.join(project_root, "backend", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    
    for g in FALLBACK_GARMENTS:
        src = os.path.join(cutouts_dir, g["filename"])
        dest_filename = f"studio_live_{g['filename']}"
        dest_path = os.path.join(uploads_dir, dest_filename)
        
        if os.path.exists(src):
            try:
                shutil.copyfile(src, dest_path)
            except Exception:
                pass
                
        emb = None
        colors = g.get("dominant_colors", ["#000000"])
                
        for uid in seeded_user_ids:
            item_doc = {
                "user_id": uid,
                "name": g["name"],
                "image_url": f"/uploads/{dest_filename}",
                "category": g["category"],
                "subcategory": g["subcategory"],
                "gender_category": g["gender_category"],
                "dominant_colors": colors,
                "pattern": "solid",
                "style": g["style"],
                "occasions": g["occasions"],
                "confidence": 0.98,
                "embedding": emb,
                "created_at": datetime.utcnow()
            }
            await db.wardrobe_items.insert_one(item_doc)
            
    print(f"Resilient Database: Seeded {len(seeded_user_ids)} users and {len(FALLBACK_GARMENTS)} studio garments per user.")

async def connect_to_mongo():
    """
    Connects to MongoDB Atlas; if Atlas network access is blocked or down,
    activates the resilient in-memory database with pre-seeded studio pieces.
    """
    try:
        db_instance.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=2000
        )
        db_instance.db = db_instance.client[settings.DATABASE_NAME]
        
        # Test connectivity with ping
        ping_result = await db_instance.client.admin.command('ping')
        print(f"MongoDB Ping Success: {ping_result}")
        print(f"Connected to remote MongoDB database: '{settings.DATABASE_NAME}'")
        
        existing_collections = await db_instance.db.list_collection_names()
        for col in COLLECTIONS:
            if col not in existing_collections:
                await db_instance.db.create_collection(col)
                
        await create_indexes()
        db_instance.is_fallback = False
        return True
    except Exception as e:
        print(f"MongoDB Atlas notice ({e}). Activating Resilient In-Memory Database Fallback...")
        try:
            from mongomock_motor import AsyncMongoMockClient
            db_instance.client = AsyncMongoMockClient()
            db_instance.db = db_instance.client[settings.DATABASE_NAME]
            db_instance.is_fallback = True
            await seed_resilient_database(db_instance.db)
            return True
        except Exception as fe:
            print(f"Fallback activation error: {fe}")
            db_instance.db = None
            db_instance.client = None
            return False

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()

async def create_indexes():
    if db_instance.db is None or db_instance.is_fallback:
        return
    try:
        await db_instance.db.users.create_index("email", unique=True)
        await db_instance.db.style_profiles.create_index("user_id", unique=True)
        await db_instance.db.wardrobe_items.create_index("user_id")
        await db_instance.db.outfit_recommendations.create_index("user_id")
        await db_instance.db.saved_outfits.create_index([("user_id", 1), ("outfit_id", 1)], unique=True)
        await db_instance.db.outfit_plans.create_index([("user_id", 1), ("date", 1)])
    except Exception as e:
        print(f"Index creation note: {e}")

def get_db():
    return db_instance.db
