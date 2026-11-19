import numpy as np
from sklearn.neighbors import NearestNeighbors

def hex_to_rgb(hex_str: str) -> np.ndarray:
    hex_str = hex_str.lstrip('#')
    return np.array([int(hex_str[i:i+2], 16) for i in (0, 2, 4)], dtype=np.float32)

def color_distance(c1_hex: str, c2_hex: str) -> float:
    """Euclidean distance in RGB space normalized to 0 - 100."""
    rgb1 = hex_to_rgb(c1_hex)
    rgb2 = hex_to_rgb(c2_hex)
    dist = np.linalg.norm(rgb1 - rgb2)
    # Max Euclidean distance between (0,0,0) and (255,255,255) is ~441.67
    norm_dist = (dist / 441.67) * 100.0
    return float(norm_dist)

def compute_color_compatibility(item_colors: list[str], palette_colors: list[str]) -> float:
    """
    Score how well item's colors complement user's skin-tone palette.
    Higher is better (0 to 100).
    """
    if not item_colors or not palette_colors:
        return 70.0
    
    min_dists = []
    for ic in item_colors:
        dists = [color_distance(ic, pc) for pc in palette_colors]
        min_dists.append(min(dists))
    
    avg_min_dist = float(np.mean(min_dists))
    score = max(0.0, 100.0 - avg_min_dist)
    return float(score)

OCCASION_MATRIX = {
    "college": {"casual": 98, "streetwear": 92, "smart_casual": 82, "formal": 35, "party": 45},
    "casual": {"casual": 100, "streetwear": 92, "smart_casual": 85, "formal": 35, "party": 50},
    "formal": {"formal": 100, "smart_casual": 88, "casual": 20, "party": 40, "streetwear": 10},
    "party": {"party": 100, "streetwear": 82, "smart_casual": 80, "casual": 50, "formal": 55},
    "daily": {"casual": 100, "smart_casual": 90, "streetwear": 85, "formal": 40, "party": 45}
}

STYLE_COMPATIBILITY_MATRIX = {
    "casual": {"casual": 100, "smart_casual": 85, "streetwear": 85, "party": 50, "formal": 25},
    "smart_casual": {"smart_casual": 100, "casual": 85, "formal": 85, "party": 65, "streetwear": 60},
    "streetwear": {"streetwear": 100, "casual": 88, "party": 70, "smart_casual": 60, "formal": 15},
    "formal": {"formal": 100, "smart_casual": 88, "casual": 25, "party": 45, "streetwear": 15},
    "party": {"party": 100, "smart_casual": 75, "streetwear": 70, "casual": 50, "formal": 55}
}

def compute_knn_similarity(item_a, item_b) -> float:
    """
    Computes visual and style embedding cosine similarity between two garments
    using Scikit-Learn NearestNeighbors.
    Accepts item dictionaries or raw embedding vectors.
    Returns similarity score between 0.0 and 100.0.
    """
    emb_a = item_a.get("embedding") if isinstance(item_a, dict) else item_a
    emb_b = item_b.get("embedding") if isinstance(item_b, dict) else item_b
    
    # If explicit embeddings exist (512D CLIP or 128D MobileNet)
    if emb_a is not None and emb_b is not None:
        try:
            va = np.array(emb_a, dtype=np.float32).reshape(1, -1)
            vb = np.array(emb_b, dtype=np.float32).reshape(1, -1)
            # Handle dimension compatibility
            if va.shape[1] != vb.shape[1]:
                common_dim = min(va.shape[1], vb.shape[1])
                va = va[:, :common_dim]
                vb = vb[:, :common_dim]
            # Fit KNN with cosine metric
            knn = NearestNeighbors(n_neighbors=1, metric='cosine')
            knn.fit(vb)
            distances, _ = knn.kneighbors(va)
            cos_dist = float(distances[0][0])
            sim = max(0.0, min(100.0, (1.0 - (cos_dist / 2.0)) * 100.0))
            return round(sim, 1)
        except Exception as e:
            pass
            
    # Attribute & color-space cosine similarity
    c1 = item_a.get("dominant_colors", ["#000000"])[0]
    c2 = item_b.get("dominant_colors", ["#FFFFFF"])[0]
    cd = color_distance(c1, c2)
    style_bonus = 20.0 if item_a.get("style") == item_b.get("style") else 0.0
    return round(min(100.0, max(50.0, (100.0 - cd * 0.5) + style_bonus)), 1)

def rank_outfit_combination(
    top_item: dict = None,
    bottom_item: dict = None,
    footwear_item: dict = None,
    user_palette: list[str] = None,
    target_occasion: str = "casual",
    preferred_styles: list[str] = None,
    items_dict: dict = None,
    dress_item: dict = None,
    outerwear_item: dict = None,
    target_style: str = "casual",
    wear_penalty: float = 0.0
) -> dict:
    """
    Calculates outfit compatibility score S for 2-piece, 3-piece, or 4-piece outfits:
    S = 0.25 * C + 0.20 * K + 0.25 * O + 0.20 * S_target + 0.10 * V - wear_penalty
    
    Topologies supported:
    - 2-Piece: Dress + Footwear
    - 3-Piece: Top + Bottom + Footwear
    - 4-Piece: Top + Bottom + Outerwear + Footwear
    - 3-Piece Layered Dress: Dress + Outerwear + Footwear
    """
    if user_palette is None:
        user_palette = ["#263F36", "#B47A57", "#E4CDA5", "#8C5835"]
    if preferred_styles is None:
        preferred_styles = ["casual", "streetwear"]
        
    # Unpack garments from positional parameters or items_dict
    pieces = {}
    if items_dict:
        pieces = items_dict.copy()
    else:
        if top_item:
            pieces["top"] = top_item
        if bottom_item:
            pieces["bottom"] = bottom_item
        if footwear_item:
            pieces["footwear"] = footwear_item
        if dress_item:
            pieces["dress"] = dress_item
        if outerwear_item:
            pieces["outerwear"] = outerwear_item
            
    # Self-Collision Identity Check: Prevent duplicate garments in single outfit
    piece_ids = [str(p.get("id") or p.get("_id")) for p in pieces.values() if p.get("id") or p.get("_id")]
    if len(piece_ids) != len(set(piece_ids)):
        return {
            "compatibility_score": 0.0,
            "explanation": "Invalid outfit: contains duplicate garments.",
            "outfit_type": "Invalid Self-Collision",
            "metrics": {"C": 0.0, "K": 0.0, "O": 0.0, "P": 0.0, "V": 0.0}
        }
        
    # Negative Fashion Grammar Rule: Dress cannot be worn with trousers/bottoms
    if "dress" in pieces and "bottom" in pieces:
        return {
            "compatibility_score": 15.0,
            "explanation": "Grammar conflict: A dress is a one-piece garment and cannot be layered with trousers or bottoms.",
            "outfit_type": "Invalid Grammar (Dress + Bottom)",
            "metrics": {"C": 30.0, "K": 0.0, "O": 20.0, "P": 15.0, "V": 10.0}
        }

    # Determine outfit topology
    is_dress_two_piece = "dress" in pieces and "footwear" in pieces and "top" not in pieces and "bottom" not in pieces and "outerwear" not in pieces
    is_dress_layered = "dress" in pieces and "outerwear" in pieces and "footwear" in pieces and "top" not in pieces and "bottom" not in pieces
    is_dress_outfit = is_dress_two_piece or is_dress_layered
    is_four_piece = "outerwear" in pieces and "top" in pieces and "bottom" in pieces and "footwear" in pieces
    is_three_piece = "top" in pieces and "bottom" in pieces and "footwear" in pieces and "outerwear" not in pieces
    
    # 1. Color Compatibility (C)
    color_scores = []
    for role, piece in pieces.items():
        score_c = compute_color_compatibility(piece.get("dominant_colors", []), user_palette)
        color_scores.append(score_c)
        
    C = float(np.mean(color_scores)) if color_scores else 70.0
    
    # Inter-layer harmony bonus
    if is_three_piece or is_four_piece:
        t_col = pieces["top"].get("dominant_colors", ["#000000"])[0]
        b_col = pieces["bottom"].get("dominant_colors", ["#FFFFFF"])[0]
        piece_dist = color_distance(t_col, b_col)
        # Moderate contrast is visually harmonic
        if 20 <= piece_dist <= 75:
            C = min(100.0, C + 8.0)
    elif is_dress_outfit:
        d_col = pieces["dress"].get("dominant_colors", ["#000000"])[0]
        f_col = pieces["footwear"].get("dominant_colors", ["#FFFFFF"])[0]
        piece_dist = color_distance(d_col, f_col)
        if 15 <= piece_dist <= 85:
            C = min(100.0, C + 8.0)
            
    # 2. Clothing Category Compatibility (K)
    # Valid grammatical outfit structures receive full 100.0
    if is_four_piece:
        K = 100.0
        outfit_type = "4-Piece Layered Look"
    elif is_three_piece:
        K = 100.0
        outfit_type = "3-Piece Classic Look"
    elif is_dress_two_piece:
        K = 100.0
        outfit_type = "2-Piece Dress Look"
    elif is_dress_layered:
        K = 100.0
        outfit_type = "3-Piece Layered Dress Look"
    else:
        K = 70.0
        outfit_type = "Composite Look"
        
    # 3. Occasion Compatibility (O)
    occ_map = OCCASION_MATRIX.get(target_occasion.lower(), OCCASION_MATRIX["casual"])
    occ_scores = []
    for role, piece in pieces.items():
        st = piece.get("style", "casual").lower()
        occ_scores.append(occ_map.get(st, 75))
    O = float(np.mean(occ_scores)) if occ_scores else 75.0
    
    # 4. Target Style Congruence (S_target)
    style_key = target_style.lower() if target_style else "casual"
    style_map = STYLE_COMPATIBILITY_MATRIX.get(style_key, STYLE_COMPATIBILITY_MATRIX["casual"])
    style_scores = []
    for role, piece in pieces.items():
        st = piece.get("style", "casual").lower()
        style_scores.append(style_map.get(st, 65))
    S_target = float(np.mean(style_scores)) if style_scores else 75.0
    
    # 5. Visual/Style Similarity via KNN & Embeddings (V)
    pairwise_similarities = []
    piece_list = list(pieces.values())
    for i in range(len(piece_list)):
        for j in range(i + 1, len(piece_list)):
            sim = compute_knn_similarity(piece_list[i], piece_list[j])
            pairwise_similarities.append(sim)
            
    if pairwise_similarities:
        V = float(np.mean(pairwise_similarities))
    else:
        V = 85.0
        
    # Weighted Final Score S (25% Color + 20% Grammar + 25% Occasion + 20% Style + 10% Visual)
    base_score = (0.25 * C) + (0.20 * K) + (0.25 * O) + (0.20 * S_target) + (0.10 * V)
    final_score = round(min(100.0, max(0.0, base_score - wear_penalty)), 1)
    
    explanation = f"{outfit_type}: Color harmony ({round(C)}%) matches your palette; calibrated for {target_occasion.capitalize()} ({round(O)}% occasion fit) and {style_key.capitalize()} mood ({round(S_target)}% style match)."
    if wear_penalty > 0:
        explanation += f" (Adjusted for recent wear: -{round(wear_penalty)} pts)"
    
    res = {
        "compatibility_score": final_score,
        "outfit_type": outfit_type,
        "metrics": {
            "C": round(C, 1), 
            "K": K, 
            "O": round(O, 1), 
            "P": round(S_target, 1), 
            "V": round(V, 1),
            "wear_penalty": round(wear_penalty, 1)
        },
        "explanation": explanation
    }
    
    # Retain piece IDs for backward compatibility
    for role, piece in pieces.items():
        res[f"{role}_id"] = str(piece.get("_id", piece.get("id", "")))
        
    return res
