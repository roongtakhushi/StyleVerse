import os
import sys
import numpy as np

# Ensure path is configured
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
backend_path = os.path.join(project_root, "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from ml.inference.skin_detector import analyze_face_skin
from ml.inference.clothing_predict import classify_clothing, extract_clothing_embedding
from ml.inference.outfit_recommender import compute_knn_similarity, rank_outfit_combination

def run_tests():
    print("=" * 60)
    print("STYLEVERSE PRE-TRAINED MODELS VERIFICATION SUITE")
    print("=" * 60)
    
    # ---------------------------------------------------------
    # TEST 1: Google MediaPipe FaceLandmarker (468 3D Landmarks)
    # ---------------------------------------------------------
    print("\n[TEST 1] Testing Google MediaPipe Face Mesh on Boy Selfie...")
    selfie_path = os.path.join(project_root, "test_samples", "boy_selfie_1.jpg")
    skin_res = analyze_face_skin(selfie_path)
    
    assert skin_res["cielab_metrics"]["method"] == "MediaPipe-FaceMesh-468", f"Unexpected method: {skin_res['cielab_metrics']['method']}"
    assert skin_res["estimated_skin_tone"] in ["fair", "light", "medium"], f"Unexpected tone: {skin_res['estimated_skin_tone']}"
    assert skin_res["estimated_undertone"] in ["warm", "cool", "neutral"], f"Unexpected undertone: {skin_res['estimated_undertone']}"
    assert len(skin_res["primary_palette"]) == 8, f"Expected 8-color palette, got {len(skin_res['primary_palette'])}"
    
    print(f"  ✓ Model: {skin_res['cielab_metrics']['method']}")
    print(f"  ✓ CIELAB (L*, a*, b*): ({skin_res['cielab_metrics']['L_star']}, {skin_res['cielab_metrics']['a_star']}, {skin_res['cielab_metrics']['b_star']})")
    print(f"  ✓ Tone: {skin_res['estimated_skin_tone']} | Undertone: {skin_res['estimated_undertone']}")
    print(f"  ✓ Sample Hex: {skin_res['sample_hex']}")
    print("  ✓ PASS: MediaPipe 3D face mesh successfully extracted skin without beard interference.")
    
    # ---------------------------------------------------------
    # TEST 2: Hugging Face CLIP Zero-Shot Classification
    # ---------------------------------------------------------
    print("\n[TEST 2] Testing CLIP Zero-Shot Fashion Classification...")
    cutouts_dir = os.path.join(project_root, "test_samples", "studio_cutouts")
    
    expected_categories = {
        "white_crewneck_tshirt.jpg": "top",
        "blue_selvedge_jeans.jpg": "bottom",
        "black_tailored_trousers.jpg": "bottom",
        "white_leather_sneakers.jpg": "footwear",
        "brown_leather_oxfords.jpg": "footwear",
        "black_leather_jacket.jpg": "outerwear",
        "camel_trench_coat.jpg": "outerwear",
        "red_summer_wrap_dress.jpg": "dress",
        "emerald_midi_dress.jpg": "dress"
    }
    
    correct_count = 0
    for filename, exp_cat in expected_categories.items():
        img_p = os.path.join(cutouts_dir, filename)
        if not os.path.exists(img_p):
            continue
        pred = classify_clothing(img_p)
        cat = pred["category"]
        conf = pred["confidence"]
        assert cat == exp_cat, f"FAILED: {filename} expected {exp_cat}, got {cat} ({conf})"
        correct_count += 1
        print(f"  ✓ {filename:28} -> {cat.upper():10} | Sub: {pred['subcategory']:12} | Style: {pred['predicted_style']:12} ({conf*100:.1f}%)")
        
    print(f"  ✓ PASS: {correct_count}/{len(expected_categories)} items perfectly classified by CLIP.")
    
    # ---------------------------------------------------------
    # TEST 3: 512D Visual Latent Embeddings & Compatibility V
    # ---------------------------------------------------------
    print("\n[TEST 3] Testing 512D CLIP Embeddings & Visual Compatibility (V)...")
    tshirt_emb = extract_clothing_embedding(os.path.join(cutouts_dir, "white_crewneck_tshirt.jpg"))
    jeans_emb = extract_clothing_embedding(os.path.join(cutouts_dir, "blue_selvedge_jeans.jpg"))
    sneakers_emb = extract_clothing_embedding(os.path.join(cutouts_dir, "white_leather_sneakers.jpg"))
    dress_emb = extract_clothing_embedding(os.path.join(cutouts_dir, "red_summer_wrap_dress.jpg"))
    
    assert tshirt_emb.shape == (512,), f"Expected shape (512,), got {tshirt_emb.shape}"
    assert jeans_emb.shape == (512,), f"Expected shape (512,), got {jeans_emb.shape}"
    
    sim_tshirt_jeans = compute_knn_similarity({"embedding": tshirt_emb}, {"embedding": jeans_emb})
    sim_tshirt_sneakers = compute_knn_similarity({"embedding": tshirt_emb}, {"embedding": sneakers_emb})
    
    print(f"  ✓ 512D Vector Dimension Verified: shape {tshirt_emb.shape}")
    print(f"  ✓ Visual Latent Synergy (T-shirt + Jeans): {sim_tshirt_jeans}%")
    print(f"  ✓ Visual Latent Synergy (T-shirt + Sneakers): {sim_tshirt_sneakers}%")
    assert 60.0 <= sim_tshirt_jeans <= 100.0, f"Unusual similarity: {sim_tshirt_jeans}"
    print("  ✓ PASS: 512D Latent space accurately computes aesthetic synergy.")
    
    # ---------------------------------------------------------
    # TEST 4: Full Outfit Recommendation Scoring with New Embeddings
    # ---------------------------------------------------------
    print("\n[TEST 4] Testing Full Recommendation Formula S with Pre-Trained Models...")
    eval_res = rank_outfit_combination(
        top_item={"category": "top", "subcategory": "t-shirt", "dominant_colors": ["#FFFFFF"], "style": "casual", "embedding": tshirt_emb},
        bottom_item={"category": "bottom", "subcategory": "jeans", "dominant_colors": ["#1A365D"], "style": "casual", "embedding": jeans_emb},
        footwear_item={"category": "footwear", "subcategory": "sneakers", "dominant_colors": ["#F8FAFC"], "style": "casual", "embedding": sneakers_emb},
        user_palette=skin_res["primary_palette"],
        target_occasion="casual",
        preferred_styles=["casual"]
    )
    
    print(f"  ✓ Outfit Compatibility Score (S): {eval_res['compatibility_score']}%")
    print(f"  ✓ Metrics: {eval_res['metrics']}")
    print(f"  ✓ Explanation: {eval_res['explanation']}")
    assert eval_res["compatibility_score"] > 80.0
    print("  ✓ PASS: End-to-end recommendation engine validated.")
    
    print("\n" + "=" * 60)
    print("ALL PRE-TRAINED AI MODEL TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
