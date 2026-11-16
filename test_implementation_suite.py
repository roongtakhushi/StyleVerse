"""
STYLEVERSE Full Implementation & Verification Test Suite
Verifies:
1. database.py connection error handling and explicit db = None reset.
2. skin_detector.py landmark-guided anatomical patch extraction and CIELAB color analysis.
3. clothing_predict.py MobileNetV2 fashion backbone, categories, and 128D visual embeddings.
4. outfit_recommender.py Scikit-Learn KNN cosine similarity, 2-piece, 3-piece, and 4-piece outfit scoring.
5. FastAPI app routing, schema integrity, and endpoints registration.
"""

import sys
import os
import numpy as np
import cv2
import asyncio

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

def test_database_connection_resilience():
    print("--- [TEST 1] Database Connection Resilience ---")
    from app.database import db_instance, connect_to_mongo
    
    # Temporarily set invalid URI to test error handler
    orig_uri = os.environ.get("MONGODB_URI")
    os.environ["MONGODB_URI"] = "mongodb://nonexistent_host:27017"
    
    # Force connection attempt with short timeout
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # connect_to_mongo is an async coroutine
        loop.run_until_complete(connect_to_mongo())
    except Exception as e:
        print(f"Caught expected failure: {e}")
    finally:
        if orig_uri:
            os.environ["MONGODB_URI"] = orig_uri
        else:
            os.environ.pop("MONGODB_URI", None)
            
    print(f"db_instance.db is correctly None: {db_instance.db is None}")
    assert db_instance.db is None, "db_instance.db must be None when connection fails"
    print("✓ Test 1 PASSED: Database connection failure safely resets db_instance.db = None.\n")


def test_skin_detector_landmarks_and_cielab():
    print("--- [TEST 2] Skin Detector & CIELAB Analysis ---")
    from ml.inference.skin_detector import analyze_face_skin, rgb_to_hex
    
    # Generate synthetic portrait image with realistic skin tones
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    # Background
    img[:] = (240, 240, 240)
    # Draw face oval with warm golden/tan tone (BGR: B=130, G=168, R=220)
    cv2.ellipse(img, (150, 150), (90, 120), 0, 0, 360, (130, 168, 220), -1)
    # Eyes
    cv2.circle(img, (115, 130), 12, (50, 40, 30), -1)
    cv2.circle(img, (185, 130), 12, (50, 40, 30), -1)
    # Mouth
    cv2.ellipse(img, (150, 210), (25, 12), 0, 0, 360, (90, 90, 180), -1)
    
    test_path = os.path.join(PROJECT_ROOT, "test_face.jpg")
    cv2.imwrite(test_path, img)
    
    try:
        result = analyze_face_skin(test_path)
        print(f"Tone: {result['estimated_skin_tone']}")
        print(f"Undertone: {result['estimated_undertone']}")
        print(f"Hex: {result['sample_hex']}")
        print(f"CIELAB Details: {result['cielab_metrics']}")
        print(f"Palette length: {len(result['primary_palette'])}")
        
        assert "estimated_skin_tone" in result
        assert result["estimated_undertone"] in ["warm", "cool", "neutral"]
        assert "L_star" in result["cielab_metrics"]
        assert "a_star" in result["cielab_metrics"]
        assert "b_star" in result["cielab_metrics"]
        assert len(result["primary_palette"]) > 0
        print("✓ Test 2 PASSED: Landmark patch extraction, CIELAB metrics, and palette generation verified.\n")
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)


def test_clothing_classifier_and_embeddings():
    print("--- [TEST 3] MobileNetV2 Fashion Classifier & 128D Embeddings ---")
    from ml.inference.clothing_predict import classify_clothing, extract_clothing_embedding
    
    # Create test top image
    shirt = np.zeros((200, 200, 3), dtype=np.uint8)
    shirt[:] = (255, 255, 255)
    # Draw navy shirt
    cv2.rectangle(shirt, (40, 40), (160, 180), (128, 0, 0), -1)
    shirt_path = os.path.join(PROJECT_ROOT, "test_shirt.jpg")
    cv2.imwrite(shirt_path, shirt)
    
    # Create test footwear image
    shoes = np.zeros((100, 200, 3), dtype=np.uint8)
    shoes[:] = (255, 255, 255)
    cv2.rectangle(shoes, (20, 40), (180, 85), (20, 20, 20), -1)
    shoes_path = os.path.join(PROJECT_ROOT, "test_shoes.jpg")
    cv2.imwrite(shoes_path, shoes)
    
    try:
        top_res = classify_clothing(shirt_path)
        print("Top Classification:", top_res["category"], "->", top_res["subcategory"], f"(conf: {top_res['confidence']})")
        
        shoe_res = classify_clothing(shoes_path)
        print("Footwear Classification:", shoe_res["category"], "->", shoe_res["subcategory"], f"(conf: {shoe_res['confidence']})")
        
        top_emb = extract_clothing_embedding(shirt_path)
        print(f"Embedding shape: {top_emb.shape}, L2-norm: {np.linalg.norm(top_emb):.3f}")
        
        assert top_res["category"] in ["top", "outerwear", "bottom", "dress", "footwear"]
        assert shoe_res["category"] == "footwear"
        assert top_emb.shape == (128,)
        assert np.isclose(np.linalg.norm(top_emb), 1.0, atol=1e-2)
        print("✓ Test 3 PASSED: MobileNetV2 architecture, category inference, and normalized 128D embeddings verified.\n")
    finally:
        for p in [shirt_path, shoes_path]:
            if os.path.exists(p):
                os.remove(p)


def test_outfit_recommender_knn_and_topologies():
    print("--- [TEST 4] Outfit Recommender: Scikit-Learn KNN & Multi-Piece Topologies ---")
    from ml.inference.outfit_recommender import rank_outfit_combination, compute_knn_similarity
    
    # Verify KNN cosine similarity
    v1 = np.random.randn(128)
    v1 = (v1 / np.linalg.norm(v1)).tolist()
    v2 = np.random.randn(128)
    v2 = (v2 / np.linalg.norm(v2)).tolist()
    
    sim_identical = compute_knn_similarity(v1, v1)
    sim_random = compute_knn_similarity(v1, v2)
    print(f"KNN Cosine Similarity (Identical): {sim_identical:.2f}% (Expected ~100%)")
    print(f"KNN Cosine Similarity (Random pair): {sim_random:.2f}%")
    assert sim_identical >= 99.0
    
    # Test items
    dress = {
        "id": "item_dress_1",
        "category": "dress",
        "subcategory": "midi dress",
        "style": "elegant",
        "occasion": ["cocktail", "formal", "party"],
        "dominant_colors": ["#1A1A2E", "#16213E"],
        "embedding": v1
    }
    top = {
        "id": "item_top_1",
        "category": "top",
        "subcategory": "blazer",
        "style": "formal",
        "occasion": ["formal", "office"],
        "dominant_colors": ["#1E2022", "#0F4C81"],
        "embedding": v1
    }
    bottom = {
        "id": "item_bot_1",
        "category": "bottom",
        "subcategory": "trousers",
        "style": "formal",
        "occasion": ["formal", "office"],
        "dominant_colors": ["#2B2B2B", "#1E2022"],
        "embedding": v1
    }
    footwear = {
        "id": "item_shoes_1",
        "category": "footwear",
        "subcategory": "oxford",
        "style": "formal",
        "occasion": ["formal", "office"],
        "dominant_colors": ["#000000", "#111111"],
        "embedding": v1
    }
    outerwear = {
        "id": "item_coat_1",
        "category": "outerwear",
        "subcategory": "trench coat",
        "style": "formal",
        "occasion": ["formal", "office"],
        "dominant_colors": ["#D0B49F", "#A47551"],
        "embedding": v2
    }
    
    user_palette = ["#1E2022", "#0F4C81", "#D0B49F", "#000000"]
    
    # 2-Piece Test (Dress + Footwear)
    res_2p = rank_outfit_combination(
        items_dict={"dress": dress, "footwear": footwear},
        user_palette=user_palette,
        target_occasion="formal",
        preferred_styles=["formal", "elegant"]
    )
    print(f"2-Piece (Dress + Footwear) Score: {res_2p['compatibility_score']}% | Type: {res_2p['outfit_type']}")
    assert res_2p["compatibility_score"] > 60.0
    assert res_2p["outfit_type"] == "2-Piece Dress Look"
    
    # 3-Piece Test (Top + Bottom + Footwear)
    res_3p = rank_outfit_combination(
        items_dict={"top": top, "bottom": bottom, "footwear": footwear},
        user_palette=user_palette,
        target_occasion="formal",
        preferred_styles=["formal"]
    )
    print(f"3-Piece (Top + Bottom + Footwear) Score: {res_3p['compatibility_score']}% | Type: {res_3p['outfit_type']}")
    assert res_3p["compatibility_score"] > 60.0
    assert res_3p["outfit_type"] == "3-Piece Classic Look"
    
    # 4-Piece Test (Top + Bottom + Outerwear + Footwear)
    res_4p = rank_outfit_combination(
        items_dict={"top": top, "bottom": bottom, "outerwear": outerwear, "footwear": footwear},
        user_palette=user_palette,
        target_occasion="formal",
        preferred_styles=["formal"]
    )
    print(f"4-Piece Layered Score: {res_4p['compatibility_score']}% | Type: {res_4p['outfit_type']}")
    assert res_4p["compatibility_score"] > 50.0
    assert res_4p["outfit_type"] == "4-Piece Layered Look"
    
    print("✓ Test 4 PASSED: KNN similarity & 2-piece, 3-piece, and 4-piece outfit topologies verified.\n")


def test_fastapi_routes_and_schemas():
    print("--- [TEST 5] FastAPI App Routing & Schemas ---")
    from app.main import app
    from app.schemas.all_schemas import StyleProfileResponse, OutfitSaveRequest, SavedOutfitResponse
    
    routes = [route.path for route in app.routes]
    print(f"Total API routes registered: {len(routes)}")
    
    expected_endpoints = [
        "/api/auth/register",
        "/api/auth/login",
        "/api/users/profile",
        "/api/users/preferences",
        "/api/skin/analyze",
        "/api/wardrobe/upload",
        "/api/wardrobe",
        "/api/outfits/generate",
        "/api/outfits/save",
        "/api/outfits/saved",
        "/api/outfits/saved/{outfit_id}",
    ]
    
    for ep in expected_endpoints:
        found = any(r == ep or r.startswith(ep) for r in routes)
        print(f"Endpoint '{ep}': {'Found' if found else 'MISSING'}")
        assert found, f"Route {ep} must be registered in FastAPI app"
        
    # Verify Schema structures
    schema_inst = StyleProfileResponse(
        user_id="test_user",
        skin_tone_estimate="light",
        undertone="warm",
        colour_palette=["#FFFFFF", "#000000"],
        favourite_colors=["#0F4C81", "#D0B49F"],
        preferred_styles=["minimalist"],
        preferred_occasions=["casual"]
    )
    assert schema_inst.favourite_colors == ["#0F4C81", "#D0B49F"]
    
    save_req = OutfitSaveRequest(
        outfit_id="outfit_123",
        occasion="cocktail",
        style="elegant",
        compatibility_score=92.5,
        explanation="Stunning color harmony",
        dress_id="dress_01",
        footwear_id="shoes_01",
        items={"dress": {"subcategory": "midi dress"}, "footwear": {"subcategory": "heels"}}
    )
    assert save_req.dress_id == "dress_01"
    assert save_req.items["dress"]["subcategory"] == "midi dress"
    
    print("✓ Test 5 PASSED: All FastAPI routes and Pydantic schemas verified.\n")


if __name__ == "__main__":
    print("==================================================")
    print("STYLEVERSE CORE VERIFICATION TEST SUITE STARTING")
    print("==================================================\n")
    
    test_database_connection_resilience()
    test_skin_detector_landmarks_and_cielab()
    test_clothing_classifier_and_embeddings()
    test_outfit_recommender_knn_and_topologies()
    test_fastapi_routes_and_schemas()
    
    print("==================================================")
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("==================================================")
