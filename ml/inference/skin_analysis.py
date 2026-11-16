import math

# Palettes corresponding to skin undertone and complexion
PALETTE_LIBRARY = {
    "warm": {
        "earthy": ["#263F36", "#B47A57", "#E4CDA5", "#8C5835", "#C49A45"],
        "warm_autumn": ["#80382B", "#C07D38", "#4A5D23", "#D9A05B", "#683B2B"],
        "golden_vibes": ["#D4AF37", "#9E6D38", "#4E3629", "#F3E5AB", "#7B3F00"]
    },
    "cool": {
        "jewel": ["#003366", "#4B0082", "#800020", "#2E8B57", "#4682B4"],
        "winter_frost": ["#1A2B4C", "#5C2C47", "#8A9EA7", "#E6ECF5", "#22223B"],
        "summer_breeze": ["#6A82FB", "#FC5C7D", "#A1C4FD", "#C2E9FB", "#7F7FD5"]
    },
    "neutral": {
        "soft_neutral": ["#263F36", "#B47A57", "#E4CDA5", "#555B6E", "#89B0AE"],
        "classic_chic": ["#1B263B", "#415A77", "#778DA9", "#E0E1DD", "#A37081"],
        "monochrome_earth": ["#2B2D42", "#8D99AE", "#EDF2F4", "#EF233C", "#D90429"]
    }
}

SKIN_TONE_CATEGORIES = {
    "fair": {"L_min": 75, "undertone_hint": "cool"},
    "light": {"L_min": 65, "undertone_hint": "neutral"},
    "medium": {"L_min": 52, "undertone_hint": "warm"},
    "tan": {"L_min": 40, "undertone_hint": "warm"},
    "deep": {"L_min": 0, "undertone_hint": "neutral"}
}

def rgb_to_lab(r, g, b):
    """Simple RGB to approximate CIELAB conversion."""
    # Normalize RGB to 0-1
    r_lin = r / 255.0
    g_lin = g / 255.0
    b_lin = b / 255.0
    
    # Luminance approx (Perceived brightness)
    L = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
    L = 116.0 * (L ** (1/3) if L > 0.008856 else (7.787 * L + 16/116)) - 16
    
    # Approximate red-green (a) and yellow-blue (b) balance
    a = 500.0 * ((r_lin - g_lin) * 0.5)
    b_val = 200.0 * ((g_lin - b_lin) * 0.5)
    return L, a, b_val

def estimate_skin_tone_category(L: float) -> str:
    if L >= 75:
        return "fair"
    elif L >= 65:
        return "light"
    elif L >= 52:
        return "medium"
    elif L >= 40:
        return "tan"
    else:
        return "deep"

def estimate_undertone(r: int, g: int, b: int) -> str:
    """
    Heuristic undertone determination:
    Warm undertones: higher yellow/red ratio (R > G > B with notable yellow component)
    Cool undertones: higher blue/pink component (B or R-B balance)
    Neutral: balanced ratios
    """
    diff_rg = r - g
    diff_gb = g - b
    
    if diff_gb > 25 and (r > b + 30):
        return "warm"
    elif b > g or abs(r - b) < 15:
        return "cool"
    else:
        return "neutral"

def get_recommended_palettes(undertone: str, skin_tone: str) -> dict:
    undertone_key = undertone.lower() if undertone.lower() in PALETTE_LIBRARY else "neutral"
    palettes = PALETTE_LIBRARY[undertone_key]
    
    # Flatten primary recommended colors for easy matching
    all_colors = []
    for p_name, colors in palettes.items():
        all_colors.extend(colors)
    unique_colors = list(dict.fromkeys(all_colors))[:8]
    
    return {
        "undertone": undertone_key,
        "skin_tone": skin_tone,
        "palettes": palettes,
        "primary_palette": unique_colors
    }

