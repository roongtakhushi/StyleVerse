import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000/api"

# 1. Health check
print("=== 1. TESTING /api/health PROBE ===")
with urllib.request.urlopen(f"{BASE_URL}/health") as resp:
    data = json.loads(resp.read().decode())
    print("Health Status:", data.get("status"))
    print("Database:", data.get("database"))

# 2. Login as khushi@styleverse.com
print("\n=== 2. LOGGING IN ===")
login_req = urllib.request.Request(
    f"{BASE_URL}/auth/login",
    data=json.dumps({"email": "khushi@styleverse.com", "password": "Password123!"}).encode(),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(login_req) as resp:
    auth_data = json.loads(resp.read().decode())
    token = auth_data["access_token"]
    user_name = auth_data["user"]["name"]
    print(f"Logged in as {user_name} (token length: {len(token)})")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

# 3. Generate Outfits
print("\n=== 3. GENERATING OUTFITS ===")
gen_req = urllib.request.Request(
    f"{BASE_URL}/outfits/generate",
    data=json.dumps({"occasion": "casual", "style": "casual"}).encode(),
    headers=headers
)
with urllib.request.urlopen(gen_req) as resp:
    gen_data = json.loads(resp.read().decode())
    recs = gen_data.get("recommendations", [])
    print(f"Generated {len(recs)} ranked outfits.\n")
    
    for i, r in enumerate(recs, 1):
        score = r["compatibility_score"]
        otype = r.get("outfit_type", "Outfit")
        items = r["items"]
        print(f"--- LOOK #{i} ({otype} - {score}% Match) ---")
        item_keys = list(items.keys())
        item_imgs = [items[k].get("image_url", "") for k in item_keys]
        item_names = [f"{k}: {items[k].get('subcategory')}" for k in item_keys]
        print("  Composition:", ", ".join(item_names))
        print("  Explanation:", r.get("explanation"))
        
        # ASSERTION 1: Self-collision check
        assert len(item_imgs) == len(set(item_imgs)), f"Look #{i} has duplicate garment images!"
        
        # ASSERTION 2: Dress grammar check
        if "dress" in items:
            assert "bottom" not in items, f"Look #{i} illegally combines a dress with a bottom!"
            assert "top" not in items, f"Look #{i} illegally combines a dress with an inner top!"
            
        print("  ✓ Self-collision & Grammar checks PASSED.")

print("\n==================================================")
print("ALL PRODUCTION GRAMMAR & HEALTH CHECKS PASSED!")
print("==================================================")
