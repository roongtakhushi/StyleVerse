import numpy as np
from sklearn.cluster import KMeans
from PIL import Image

def hex_to_rgb(hex_str: str) -> tuple:
    hex_str = hex_str.lstrip('#')
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb: tuple) -> str:
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def is_background_color(rgb: np.ndarray, tolerance: int = 15) -> bool:
    """Detects near-white or near-black studio background pixels."""
    r, g, b = rgb[0], rgb[1], rgb[2]
    # Pure or off-white background (e.g. ecommerce studio photography)
    if r > 240 and g > 240 and b > 240:
        return True
    # Pure dark background
    if r < 15 and g < 15 and b < 15:
        return True
    return False

def extract_dominant_colors(image_path: str, k: int = 3) -> list[str]:
    """
    Extracts k dominant clothing colors using K-Means clustering.
    Supports transparent PNG cutouts (RGBA) by strictly sampling non-transparent pixels,
    and filters out solid studio backgrounds (near-white margins).
    """
    raw_img = Image.open(image_path)
    
    # If RGBA, prioritize transparent alpha mask
    if raw_img.mode in ("RGBA", "LA") or (raw_img.mode == "P" and "transparency" in raw_img.info):
        rgba_img = raw_img.convert("RGBA").resize((160, 160))
        arr = np.array(rgba_img)
        rgb_part = arr[:, :, :3].reshape(-1, 3)
        alpha_part = arr[:, :, 3].reshape(-1)
        clothing_pixels = rgb_part[alpha_part > 64]
        if len(clothing_pixels) >= 100:
            target_pixels = clothing_pixels
        else:
            target_pixels = rgb_part
    else:
        img = raw_img.convert("RGB").resize((160, 160))
        pixels = np.array(img).reshape(-1, 3)
        # Filter out near-white background pixels (> 242 across R,G,B)
        non_bg_mask = ~((pixels[:, 0] > 242) & (pixels[:, 1] > 242) & (pixels[:, 2] > 242))
        clothing_pixels = pixels[non_bg_mask]
        
        # If foreground is isolated, cluster clothing pixels; else cluster cropped center
        if len(clothing_pixels) >= 150:
            target_pixels = clothing_pixels
        else:
            w, h = img.size
            center_crop = img.crop((int(w * 0.2), int(h * 0.2), int(w * 0.8), int(h * 0.8)))
            target_pixels = np.array(center_crop).reshape(-1, 3)
        
    num_unique = len(np.unique(target_pixels, axis=0))
    actual_k = min(k, max(1, num_unique))
    
    kmeans = KMeans(n_clusters=actual_k, random_state=42, n_init='auto')
    kmeans.fit(target_pixels)
    
    counts = np.bincount(kmeans.labels_)
    sorted_indices = np.argsort(counts)[::-1]
    
    hex_colors = []
    for idx in sorted_indices:
        center = kmeans.cluster_centers_[idx]
        hex_colors.append(rgb_to_hex(center))
        
    return hex_colors[:k]
