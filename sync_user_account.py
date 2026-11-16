import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys, os
from datetime import datetime
from bson import ObjectId

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from app.utils.auth import get_password_hash, verify_password

uri = "mongodb+srv://khushiroongta0801_db_user:7IyEkLUJ12TSQJxG@styleverse.2kxuscx.mongodb.net/?retryWrites=true&w=majority"

async def main():
    client = AsyncIOMotorClient(uri)
    db = client["styleverse"]
    
    pwd = "Password123!"
    pwd_hash = get_password_hash(pwd)
    
    # 1. Update khushi.test1@styleverse.com
    await db.users.update_one(
        {"email": "khushi.test1@styleverse.com"},
        {"$set": {"password_hash": pwd_hash}}
    )
    print("Updated khushi.test1@styleverse.com with password 'Password123!'")
    
    # 2. Also register khushi@styleverse.com
    u1 = await db.users.find_one({"email": "khushi.test1@styleverse.com"})
    u1_id = str(u1["_id"])
    
    existing = await db.users.find_one({"email": "khushi@styleverse.com"})
    if not existing:
        u_doc = {
            "name": "Khushi Roongta",
            "email": "khushi@styleverse.com",
            "password_hash": pwd_hash,
            "gender_preference": "unisex",
            "created_at": datetime.utcnow()
        }
        res = await db.users.insert_one(u_doc)
        new_uid = str(res.inserted_id)
        print("Created new user khushi@styleverse.com with ID:", new_uid)
        
        # Clone wardrobe items and style profile so this user has all the test clothes too
        async for item in db.wardrobe_items.find({"user_id": u1_id}):
            item_copy = item.copy()
            del item_copy["_id"]
            item_copy["user_id"] = new_uid
            await db.wardrobe_items.insert_one(item_copy)
            
        p = await db.style_profiles.find_one({"user_id": u1_id})
        if p:
            p_copy = p.copy()
            del p_copy["_id"]
            p_copy["user_id"] = new_uid
            await db.style_profiles.insert_one(p_copy)
            
        print("Copied wardrobe and style profile to khushi@styleverse.com successfully!")
    else:
        await db.users.update_one(
            {"email": "khushi@styleverse.com"},
            {"$set": {"password_hash": pwd_hash}}
        )
        print("Updated existing khushi@styleverse.com with password 'Password123!'")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
