import sys, os
sys.path.insert(0, "Project")

from ml.inference.skin_detector import analyze_face_skin
from ml.inference.clothing_predict import classify_clothing
from ml.preprocessing.color_extraction import extract_dominant_colors

print("==================================================")
print("TESTING ML INFERENCE ON REAL DOWNLOADED SAMPLES")
print("==================================================\n")

print("--- 1. BOY SELFIE SKIN ANALYSIS ---")
for selfie in ["boy_selfie_1.jpg", "boy_selfie_2.jpg"]:
    path = os.path.join(r"Project\test_samples", selfie)
    res = analyze_face_skin(path)
    print(f"{selfie}:")
    print(f"  Tone: {res['estimated_skin_tone']} | Undertone: {res['estimated_undertone']}")
    print(f"  Skin Color Hex: {res['sample_hex']}")
    print(f"  CIELAB: {res['cielab_metrics']}")
    print(f"  Recommended Palette: {res['primary_palette'][:4]}...")
    print()

print("--- 2. WARDROBE SAMPLES CLASSIFICATION & COLOR EXTRACTION ---")
clothes = [
    "white_tshirt.jpg", "blue_shirt.jpg", "blue_jeans.jpg", 
    "black_trousers.jpg", "white_sneakers.jpg", "brown_oxfords.jpg",
    "black_jacket.jpg", "beige_trench_coat.jpg", "summer_dress.jpg"
]

for c in clothes:
    path = os.path.join(r"Project\test_samples", c)
    pred = classify_clothing(path)
    colors = extract_dominant_colors(path, k=3)
    cat = pred['category']
    sub = pred['subcategory']
    conf = int(pred['confidence'] * 100)
    print(f"{c:<20} -> {cat:<10} | {sub:<12} | Conf: {conf}% | Dominant Colors: {colors}")

print("\n==================================================")
print("ALL SAMPLE INFERENCES COMPLETED CLEANLY!")
print("==================================================")
