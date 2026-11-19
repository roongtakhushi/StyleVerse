from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.database import get_db
from app.utils.auth import get_current_user
from app.schemas.all_schemas import (
    OutfitGenerateRequest,
    OutfitRecommendationResponse,
    OutfitSaveRequest,
    SavedOutfitResponse
)
from ml.inference.outfit_recommender import rank_outfit_combination

router = APIRouter(prefix="/outfits", tags=["Outfits"])

def uuid_short():
    import uuid
    return uuid.uuid4().hex[:8]

def format_item_summary(item: dict) -> dict:
    """Helper to format a concise summary for an outfit piece."""
    return {
        "id": str(item.get("_id", item.get("id", ""))),
        "category": item.get("category", "garment"),
        "subcategory": item.get("subcategory", item.get("category", "Item")),
        "image_url": item.get("image_url", ""),
        "dominant_colors": item.get("dominant_colors", []),
        "style": item.get("style", "casual")
    }

@router.post("/generate")
async def generate_outfits(req: OutfitGenerateRequest, current_user: dict = Depends(get_current_user)):
    """
    Generates personalized outfit combinations from the authenticated user's actual wardrobe.
    Supports:
    - 2-Piece Outfits (Dress + Footwear)
    - 3-Piece Outfits (Top + Bottom + Footwear)
    - 4-Piece Outfits (Top + Bottom + Outerwear + Footwear)
    
    Evaluates every valid combination using formula S with Scikit-Learn KNN embedding similarity:
    S = 0.35*C + 0.25*K + 0.20*O + 0.10*P + 0.10*V
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable")
        
    user_id = str(current_user.get("_id", current_user.get("id")))
    
    # 1. Fetch user's confirmed skin-tone colour palette, gender preference, and style preferences
    user_palette = ["#263F36", "#B47A57", "#E4CDA5", "#8C5835"]
    preferred_styles = ["casual", "streetwear"]
    gender_pref = "unisex"
    
    user_doc = await db.users.find_one({"_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id})
    if user_doc and user_doc.get("gender_preference"):
        gender_pref = user_doc.get("gender_preference").lower()
        
    profile = await db.style_profiles.find_one({"user_id": user_id})
    if profile:
        if profile.get("colour_palette"):
            user_palette = profile.get("colour_palette")
        if profile.get("preferred_styles"):
            preferred_styles = profile.get("preferred_styles")
        if profile.get("gender_preference"):
            gender_pref = profile.get("gender_preference").lower()
            
    # 2. Retrieve user's actual wardrobe items from MongoDB with Gender Partitioning
    wardrobe_items = []
    cursor = db.wardrobe_items.find({"user_id": user_id})
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        
        # Gender Compatibility Guard
        g_cat = (doc.get("gender_category") or "unisex").lower()
        item_cat = (doc.get("category") or "").lower()
        item_sub = (doc.get("subcategory") or "").lower()
        
        # If user preference is 'men', strictly exclude women's dresses, skirts, gowns, and items tagged 'women'
        if gender_pref == "men":
            if g_cat == "women" or item_cat == "dress" or item_sub in ["dress", "gown", "skirt", "heels"]:
                continue
        # If user preference is 'women', exclude items tagged explicitly 'men'
        elif gender_pref == "women":
            if g_cat == "men":
                continue
                
        wardrobe_items.append(doc)
        
    # Categorical Disambiguation: Dresses are 1-piece garments, never bottoms or tops
    dresses = [
        item for item in wardrobe_items 
        if item.get("category") == "dress" or item.get("subcategory") in ["dress", "gown", "maxi dress"]
    ]
    tops = [
        item for item in wardrobe_items 
        if item.get("category") == "top" and item not in dresses
    ]
    bottoms = [
        item for item in wardrobe_items 
        if item.get("category") == "bottom" and item not in dresses and item.get("subcategory") not in ["dress", "gown"]
    ]
    footwear = [
        item for item in wardrobe_items 
        if item.get("category") == "footwear"
    ]
    outerwear = [
        item for item in wardrobe_items 
        if item.get("category") == "outerwear" and item not in dresses
    ]
    
    can_make_standard = bool(tops and bottoms and footwear)
    can_make_dress = bool(dresses and footwear)
    
    if not can_make_standard and not can_make_dress:
        missing = []
        if not footwear:
            missing.append("footwear (shoes/sneakers)")
        if not tops and not dresses:
            missing.append("tops (shirts/t-shirts) or dresses")
        if not bottoms and not dresses:
            missing.append("bottoms (trousers/jeans) or dresses")
        detail_msg = f"Insufficient wardrobe items to generate an outfit. Please upload either (Tops + Bottoms + Footwear) or (Dress + Footwear). Missing: {', '.join(missing)}."
        raise HTTPException(status_code=400, detail=detail_msg)

    # 2b. Wear History & Recency Intelligence (Sync with db.outfit_plans and db.saved_outfits)
    worn_item_recency = {} # garment_id -> min_days_ago
    today_date = datetime.utcnow().date()
    if db is not None:
        try:
            recent_plans = []
            p_cursor = db.outfit_plans.find({"user_id": user_id}).sort("date", -1).limit(30)
            async for p in p_cursor:
                recent_plans.append(p)
                
            saved_lookup = {}
            if recent_plans:
                s_cursor = db.saved_outfits.find({"user_id": user_id})
                async for s in s_cursor:
                    s_id = str(s.get("outfit_id", s.get("_id")))
                    saved_lookup[s_id] = s
                    
                for plan in recent_plans:
                    plan_date_str = plan.get("date", "")
                    try:
                        p_date = datetime.strptime(plan_date_str, "%Y-%m-%d").date()
                        diff_days = abs((today_date - p_date).days)
                    except Exception:
                        diff_days = 7
                        
                    p_outfit_id = plan.get("outfit_id")
                    if p_outfit_id and p_outfit_id in saved_lookup:
                        s_doc = saved_lookup[p_outfit_id]
                        for role_key in ["top_id", "bottom_id", "dress_id", "footwear_id", "outerwear_id"]:
                            iid = s_doc.get(role_key)
                            if iid:
                                iid_str = str(iid)
                                if iid_str not in worn_item_recency or diff_days < worn_item_recency[iid_str]:
                                    worn_item_recency[iid_str] = diff_days
        except Exception as e:
            logger.warning(f"Could not load wear history for user {user_id}: {e}")

    def get_outfit_wear_info(garment_ids: list[str]):
        """Returns wear_penalty (float), wear_status (str), and wear_badge (str)"""
        min_diff = None
        for gid in garment_ids:
            if gid in worn_item_recency:
                d = worn_item_recency[gid]
                if min_diff is None or d < min_diff:
                    min_diff = d
                    
        if min_diff is None:
            return 0.0, "✨ Fresh Pick (Not worn recently)", "fresh"
        elif min_diff <= 1:
            return 18.0, "⏱️ Worn recently (Yesterday / Today)", "worn_recent"
        elif min_diff <= 3:
            return 8.0, f"⏱️ Worn {min_diff} days ago", "worn_recent"
        elif min_diff <= 6:
            return 3.0, f"🔄 In rotation ({min_diff} days ago)", "in_rotation"
        else:
            return 0.0, "✨ Fresh Pick (Past 7+ days)", "fresh"
        
    # 3. Generate candidate combinations with strict self-collision and grammar checks
    combinations = []
    
    # 3a. Standard 3-Piece combinations (Top + Bottom + Footwear)
    if can_make_standard:
        for t in tops:
            for b in bottoms:
                t_id = str(t.get("_id", t.get("id")))
                b_id = str(b.get("_id", b.get("id")))
                t_img = t.get("image_url", "").strip()
                b_img = b.get("image_url", "").strip()
                if t_id == b_id or (t_img and t_img == b_img):
                    continue
                for f in footwear:
                    f_id = str(f.get("_id", f.get("id")))
                    w_pen, w_status, w_badge = get_outfit_wear_info([t_id, b_id, f_id])
                    eval_res = rank_outfit_combination(
                        top_item=t,
                        bottom_item=b,
                        footwear_item=f,
                        user_palette=user_palette,
                        target_occasion=req.occasion,
                        target_style=req.style or "casual",
                        preferred_styles=preferred_styles,
                        wear_penalty=w_pen
                    )
                    comb_id = f"outfit_{uuid_short()}"
                    combinations.append({
                        "id": comb_id,
                        "user_id": user_id,
                        "occasion": req.occasion,
                        "style": req.style or "casual",
                        "compatibility_score": eval_res["compatibility_score"],
                        "explanation": eval_res["explanation"],
                        "outfit_type": eval_res.get("outfit_type", "3-Piece Classic Look"),
                        "wear_status": w_status,
                        "wear_badge": w_badge,
                        "items": {
                            "top": format_item_summary(t),
                            "bottom": format_item_summary(b),
                            "footwear": format_item_summary(f)
                        },
                        "metrics": eval_res["metrics"],
                        "created_at": datetime.utcnow().isoformat()
                    })
                    
        # 3b. 4-Piece combinations (Top + Bottom + Outerwear + Footwear)
        # STRICT SELF-COLLISION GUARD: top and outerwear must NOT share the same ID or image
        if outerwear:
            for t in tops:
                for b in bottoms:
                    for o in outerwear:
                        t_id = str(t.get("_id", t.get("id")))
                        b_id = str(b.get("_id", b.get("id")))
                        o_id = str(o.get("_id", o.get("id")))
                        t_img = t.get("image_url", "").strip()
                        o_img = o.get("image_url", "").strip()
                        b_img = b.get("image_url", "").strip()
                        
                        # Self-collision rejection
                        if t_id == o_id or t_id == b_id or o_id == b_id:
                            continue
                        if t_img and o_img and t_img == o_img:
                            continue
                        if t_img and b_img and t_img == b_img:
                            continue
                            
                        for f in footwear:
                            f_id = str(f.get("_id", f.get("id")))
                            w_pen, w_status, w_badge = get_outfit_wear_info([t_id, b_id, o_id, f_id])
                            eval_res = rank_outfit_combination(
                                items_dict={"top": t, "bottom": b, "outerwear": o, "footwear": f},
                                user_palette=user_palette,
                                target_occasion=req.occasion,
                                target_style=req.style or "smart_casual",
                                preferred_styles=preferred_styles,
                                wear_penalty=w_pen
                            )
                            comb_id = f"outfit_{uuid_short()}"
                            combinations.append({
                                "id": comb_id,
                                "user_id": user_id,
                                "occasion": req.occasion,
                                "style": req.style or "smart_casual",
                                "compatibility_score": eval_res["compatibility_score"],
                                "explanation": eval_res["explanation"],
                                "outfit_type": eval_res.get("outfit_type", "4-Piece Layered Look"),
                                "wear_status": w_status,
                                "wear_badge": w_badge,
                                "items": {
                                    "top": format_item_summary(t),
                                    "bottom": format_item_summary(b),
                                    "outerwear": format_item_summary(o),
                                    "footwear": format_item_summary(f)
                                },
                                "metrics": eval_res["metrics"],
                                "created_at": datetime.utcnow().isoformat()
                            })
                            
    # 3c. One-Piece Dress Ensembles: 2-Piece (Dress + Footwear) and 3-Piece Layered (Dress + Outerwear + Footwear)
    if can_make_dress:
        for d in dresses:
            d_id = str(d.get("_id", d.get("id")))
            d_img = d.get("image_url", "").strip()
            
            for f in footwear:
                f_id = str(f.get("_id", f.get("id")))
                w_pen, w_status, w_badge = get_outfit_wear_info([d_id, f_id])
                eval_res = rank_outfit_combination(
                    items_dict={"dress": d, "footwear": f},
                    user_palette=user_palette,
                    target_occasion=req.occasion,
                    target_style=req.style or "casual",
                    preferred_styles=preferred_styles,
                    wear_penalty=w_pen
                )
                comb_id = f"outfit_{uuid_short()}"
                combinations.append({
                    "id": comb_id,
                    "user_id": user_id,
                    "occasion": req.occasion,
                    "style": req.style or "casual",
                    "compatibility_score": eval_res["compatibility_score"],
                    "explanation": eval_res["explanation"],
                    "outfit_type": eval_res.get("outfit_type", "2-Piece Dress Look"),
                    "wear_status": w_status,
                    "wear_badge": w_badge,
                    "items": {
                        "dress": format_item_summary(d),
                        "footwear": format_item_summary(f)
                    },
                    "metrics": eval_res["metrics"],
                    "created_at": datetime.utcnow().isoformat()
                })
                
            # 3d. 3-Piece Layered Dress Look (Dress + Outerwear + Footwear)
            if outerwear:
                for o in outerwear:
                    o_id = str(o.get("_id", o.get("id")))
                    o_img = o.get("image_url", "").strip()
                    if d_id == o_id or (d_img and d_img == o_img):
                        continue
                    for f in footwear:
                        f_id = str(f.get("_id", f.get("id")))
                        w_pen, w_status, w_badge = get_outfit_wear_info([d_id, o_id, f_id])
                        eval_res = rank_outfit_combination(
                            items_dict={"dress": d, "outerwear": o, "footwear": f},
                            user_palette=user_palette,
                            target_occasion=req.occasion,
                            target_style=req.style or "smart_casual",
                            preferred_styles=preferred_styles,
                            wear_penalty=w_pen
                        )
                        comb_id = f"outfit_{uuid_short()}"
                        combinations.append({
                            "id": comb_id,
                            "user_id": user_id,
                            "occasion": req.occasion,
                            "style": req.style or "smart_casual",
                            "compatibility_score": eval_res["compatibility_score"],
                            "explanation": eval_res["explanation"],
                            "outfit_type": eval_res.get("outfit_type", "3-Piece Layered Dress Look"),
                            "wear_status": w_status,
                            "wear_badge": w_badge,
                            "items": {
                                "dress": format_item_summary(d),
                                "outerwear": format_item_summary(o),
                                "footwear": format_item_summary(f)
                            },
                            "metrics": eval_res["metrics"],
                            "created_at": datetime.utcnow().isoformat()
                        })
                
    # 4. Rank descending by compatibility score and filter for visual diversity
    combinations.sort(key=lambda x: x["compatibility_score"], reverse=True)
    
    # Inter-Outfit Diversity: Avoid 5 identical variations that only swap one piece
    seen_combos = set()
    primary_counts = {}
    top_recommendations = []
    
    for c in combinations:
        sig = tuple(sorted([v.get("id", "") for v in c["items"].values()]))
        if sig in seen_combos:
            continue
            
        primary_id = c["items"].get("dress", {}).get("id") or c["items"].get("top", {}).get("id")
        if primary_id:
            count = primary_counts.get(primary_id, 0)
            if count >= 2 and len(combinations) > 6:
                continue
                
        seen_combos.add(sig)
        if primary_id:
            primary_counts[primary_id] = primary_counts.get(primary_id, 0) + 1
        top_recommendations.append(c)
        if len(top_recommendations) >= 5:
            break
            
    if len(top_recommendations) < 3 and combinations:
        for c in combinations:
            sig = tuple(sorted([v.get("id", "") for v in c["items"].values()]))
            if sig not in seen_combos:
                seen_combos.add(sig)
                top_recommendations.append(c)
            if len(top_recommendations) >= 5:
                break
            
    if not top_recommendations and combinations:
        top_recommendations = combinations[:5]
    
    # 5. Persist recommendations into outfit_recommendations collection
    for rec in top_recommendations:
        rec_doc = rec.copy()
        rec_doc["created_at"] = datetime.utcnow()
        await db.outfit_recommendations.insert_one(rec_doc)
        
    return {
        "status": "success",
        "total_combinations_evaluated": len(combinations),
        "recommendations": top_recommendations
    }

@router.get("/recommended")
async def get_recommended_outfits(current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable")
        
    user_id = str(current_user.get("_id", current_user.get("id")))
    items = []
    cursor = db.outfit_recommendations.find({"user_id": user_id}).sort("created_at", -1).limit(5)
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
        if isinstance(doc.get("created_at"), datetime):
            doc["created_at"] = doc["created_at"].isoformat()
        items.append(doc)
    return items

@router.post("/save")
async def save_outfit(save_req: OutfitSaveRequest, current_user: dict = Depends(get_current_user)):
    """
    Saves or favourites an outfit combination to the user's saved_outfits collection.
    Supports multi-piece outfits (tops, bottoms, footwear, dresses, outerwear).
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable")
        
    user_id = str(current_user.get("_id", current_user.get("id")))
    outfit_id = save_req.outfit_id or f"saved_{uuid_short()}"
    
    # Assemble garment items dict if not provided
    items = save_req.items or {}
    if not items:
        # Check referenced IDs and query wardrobe for details
        piece_ids = {
            "top": save_req.top_id,
            "bottom": save_req.bottom_id,
            "footwear": save_req.footwear_id,
            "dress": save_req.dress_id,
            "outerwear": save_req.outerwear_id
        }
        for role, pid in piece_ids.items():
            if pid:
                query_id = ObjectId(pid) if ObjectId.is_valid(pid) else pid
                garment = await db.wardrobe_items.find_one({"_id": query_id, "user_id": user_id})
                if garment:
                    items[role] = format_item_summary(garment)
                    
    doc = {
        "user_id": user_id,
        "outfit_id": outfit_id,
        "occasion": save_req.occasion,
        "style": save_req.style,
        "compatibility_score": save_req.compatibility_score,
        "explanation": save_req.explanation,
        "top_id": save_req.top_id,
        "bottom_id": save_req.bottom_id,
        "footwear_id": save_req.footwear_id,
        "dress_id": save_req.dress_id,
        "outerwear_id": save_req.outerwear_id,
        "items": items,
        "is_favourite": True,
        "rating": save_req.rating or 5,
        "saved_at": datetime.utcnow()
    }
    
    await db.saved_outfits.update_one(
        {"user_id": user_id, "outfit_id": outfit_id},
        {"$set": doc},
        upsert=True
    )
    
    doc["id"] = outfit_id
    if isinstance(doc.get("saved_at"), datetime):
        doc["saved_at"] = doc["saved_at"].isoformat()
        
    return {"message": "Outfit saved to favourites successfully", "outfit": doc}

@router.get("/saved")
async def get_saved_outfits(current_user: dict = Depends(get_current_user)):
    """
    Retrieves all saved looks for the authenticated user, populating garment images and details.
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable")
        
    user_id = str(current_user.get("_id", current_user.get("id")))
    saved_list = []
    
    cursor = db.saved_outfits.find({"user_id": user_id}).sort("saved_at", -1)
    async for doc in cursor:
        doc["id"] = str(doc.get("outfit_id", doc.get("_id")))
        if "_id" in doc:
            del doc["_id"]
        if isinstance(doc.get("saved_at"), datetime):
            doc["saved_at"] = doc["saved_at"].isoformat()
            
        # Ensure items dictionary is populated
        if not doc.get("items"):
            doc["items"] = {}
            for role, key in [("top", "top_id"), ("bottom", "bottom_id"), ("footwear", "footwear_id"), ("dress", "dress_id"), ("outerwear", "outerwear_id")]:
                item_id = doc.get(key)
                if item_id:
                    qid = ObjectId(item_id) if ObjectId.is_valid(item_id) else item_id
                    g = await db.wardrobe_items.find_one({"_id": qid, "user_id": user_id})
                    if g:
                        doc["items"][role] = format_item_summary(g)
                        
        saved_list.append(doc)
        
    return {"saved_outfits": saved_list, "total": len(saved_list)}

@router.delete("/saved/{outfit_id}")
async def delete_saved_outfit(outfit_id: str, current_user: dict = Depends(get_current_user)):
    """
    Deletes a saved look from the user's saved_outfits collection with strict ownership verification.
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection unavailable")
        
    user_id = str(current_user.get("_id", current_user.get("id")))
    
    doc = await db.saved_outfits.find_one({"user_id": user_id, "outfit_id": outfit_id})
    if not doc:
        # Check if exists under another user
        exists_elsewhere = await db.saved_outfits.find_one({"outfit_id": outfit_id})
        if exists_elsewhere:
            raise HTTPException(status_code=403, detail="Forbidden: You cannot delete another user's saved outfit.")
        raise HTTPException(status_code=404, detail="Saved outfit not found")
        
    await db.saved_outfits.delete_one({"user_id": user_id, "outfit_id": outfit_id})
    return {"message": "Saved outfit removed successfully", "outfit_id": outfit_id}

@router.post("/preview")
async def preview_outfit(payload: dict, current_user: dict = Depends(get_current_user)):
    return {
        "status": "success",
        "canvas_composition": payload,
        "preview_mode": "2D-Studio"
    }
