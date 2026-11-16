"""
STYLEVERSE Studio Wardrobe Seeder
Replaces portrait photos with verified, isolated studio e-commerce flat-lay cutouts.
Populates exact categories, subcategories, gender tags, K-Means color palettes,
and 128D MobileNetV2 visual embeddings into MongoDB Atlas.
"""

import os
import shutil
import uuid
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

import sys
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

from ml.preprocessing.color_extraction import extract_dominant_colors
from ml.inference.clothing_predict import extract_clothing_embedding

STUDIO_GARMENTS = [
    {
        "filename": "white_crewneck_tshirt.jpg",
        "category": "top",
        "subcategory": "t-shirt",
        "gender_category": "unisex",
        "style": "casual",
        "occasions": ["daily", "casual", "college"]
    },
    {
        "filename": "navy_oxford_shirt.jpg",
        "category": "top",
        "subcategory": "shirt",
        "gender_category": "unisex",
        "style": "smart_casual",
        "occasions": ["formal", "office", "casual"]
    },
    {
        "filename": "blue_selvedge_jeans.jpg",
        "category": "bottom",
        "subcategory": "jeans",
        "gender_category": "unisex",
        "style": "casual",
        "occasions": ["daily", "casual", "college"]
    },
    {
        "filename": "black_tailored_trousers.jpg",
        "category": "bottom",
        "subcategory": "trousers",
        "gender_category": "unisex",
        "style": "formal",
        "occasions": ["formal", "office", "party"]
    },
    {
        "filename": "white_leather_sneakers.jpg",
        "category": "footwear",
        "subcategory": "sneakers",
        "gender_category": "unisex",
        "style": "casual",
        "occasions": ["daily", "casual", "college"]
    },
    {
        "filename": "brown_leather_oxfords.jpg",
        "category": "footwear",
        "subcategory": "shoes",
        "gender_category": "men",
        "style": "formal",
        "occasions": ["formal", "office"]
    },
    {
        "filename": "black_leather_jacket.jpg",
        "category": "outerwear",
        "subcategory": "jacket",
        "gender_category": "unisex",
        "style": "streetwear",
        "occasions": ["party", "casual", "college"]
    },
    {
        "filename": "camel_trench_coat.jpg",
        "category": "outerwear",
        "subcategory": "coat",
        "gender_category": "unisex",
        "style": "formal",
        "occasions": ["formal", "office", "daily"]
    },
    {
        "filename": "emerald_midi_dress.jpg",
        "category": "dress",
        "subcategory": "dress",
        "gender_category": "women",
        "style": "elegant",
        "occasions": ["party", "formal", "casual"]
    },
    {
        "filename": "red_summer_wrap_dress.jpg",
        "category": "dress",
        "subcategory": "dress",
        "gender_category": "women",
        "style": "casual",
        "occasions": ["daily", "casual", "party"]
    }
]

URI = "mongodb+srv://khushiroongta0801_db_user:7IyEkLUJ12TSQJxG@styleverse.2kxuscx.mongodb.net/?retryWrites=true&w=majority"
CUTOUTS_DIR = os.path.join(PROJECT_ROOT, "test_samples", "studio_cutouts")
UPLOADS_DIR = os.path.join(PROJECT_ROOT, "backend", "uploads")

async def seed():
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    client = AsyncIOMotorClient(URI)
    db = client["styleverse"]
    
    print("Connecting to MongoDB Atlas...")
    await db.client.admin.command('ping')
    print("✓ Connected to MongoDB Atlas styleverse database.")
    
    # Target users
    emails = ["khushi.test1@styleverse.com", "khushi@styleverse.com"]
    target_users = []
    for email in emails:
        user = await db.users.find_one({"email": email})
        if user:
            target_users.append(user)
            print(f"Found user: {email} (ID: {user['_id']})")
            
    if not target_users:
        print("No target users found to seed!")
        client.close()
        return

    # Clean old wardrobe, recommendations, and saved looks for these users
    for u in target_users:
        uid = str(u["_id"])
        del_w = await db.wardrobe_items.delete_many({"user_id": uid})
        del_r = await db.outfit_recommendations.delete_many({"user_id": uid})
        del_s = await db.saved_outfits.delete_many({"user_id": uid})
        print(f"Cleaned user {u['email']}: removed {del_w.deleted_count} wardrobe items, {del_r.deleted_count} recommendations, {del_s.deleted_count} saved outfits.")
        
    print("\nProcessing and digitizing studio garment cutouts...")
    processed_items = []
    
    for g in STUDIO_GARMENTS:
        src = os.path.join(CUTOUTS_DIR, g["filename"])
        if not os.path.exists(src):
            print(f"Warning: source file missing: {src}")
            continue
            
        # Copy to uploads with unique hash
        ext = os.path.splitext(g["filename"])[1]
        dest_filename = f"studio_{uuid.uuid4().hex[:10]}{ext}"
        dest_path = os.path.join(UPLOADS_DIR, dest_filename)
        shutil.copyfile(src, dest_path)
        
        # Color extraction via K-Means
        colors = extract_dominant_colors(dest_path, k=3)
        
        # 128D visual embedding via MobileNetV2
        emb = extract_clothing_embedding(dest_path).tolist()
        
        item_data = {
            "image_url": f"/uploads/{dest_filename}",
            "category": g["category"],
            "subcategory": g["subcategory"],
            "gender_category": g["gender_category"],
            "dominant_colors": colors,
            "pattern": "solid",
            "style": g["style"],
            "occasions": g["occasions"],
            "confidence": 0.95,
            "embedding": emb,
            "created_at": datetime.utcnow()
        }
        processed_items.append(item_data)
        print(f"✓ Digitized {g['filename']:<28} -> {g['category']:<10} ({g['gender_category']}) | Colors: {colors}")
        
    # Insert items for each user
    for u in target_users:
        uid = str(u["_id"])
        user_items = []
        for p in processed_items:
            doc = p.copy()
            doc["user_id"] = uid
            user_items.append(doc)
        if user_items:
            res = await db.wardrobe_items.insert_many(user_items)
            print(f"\nInserted {len(res.inserted_ids)} studio garments for user {u['email']}.")
            
    client.close()
    print("\n==================================================")
    print("STUDIO WARDROBE SEEDING COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(seed())
