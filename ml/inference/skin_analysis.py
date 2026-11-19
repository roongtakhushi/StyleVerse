import math

# Comprehensive 15-Combination Seasonal Matrix
# Combines 5 Skin Tone Depths (fair, light, medium, tan, deep) x 3 Undertones (warm, cool, neutral)
# Derived from Seasonal Color Analysis (12/16-Season System) and CIELAB Colorimetry.
SEASONAL_PALETTES = {
    # 1. FAIR COMPLEXIONS (L* >= 75)
    ("fair", "warm"): {
        "season_name": "Light Warm Spring",
        "season_description": "Delicate golden-ivory complexion that glows with sunny, warm, and fresh luminous tones.",
        "primary_palette": ["#F4A261", "#FFCAD4", "#E76F51", "#B7E4C7", "#FFF1E6", "#E9C46A", "#DDA15E", "#2A9D8F"],
        "palettes": {
            "spring_pastels": ["#FFCAD4", "#FFE5D9", "#D8E2DC", "#FFEAA7", "#F7D794"],
            "warm_accents": ["#F4A261", "#E76F51", "#E9C46A", "#DDA15E", "#2A9D8F"],
            "luxe_neutrals": ["#FFF1E6", "#F0EFEB", "#DDBEA9", "#B7B7A4", "#A5A58D"]
        },
        "styling_advice": "Wear warm peaches, golden coral, and fresh mint near your face. Opt for light camel instead of heavy black."
    },
    ("fair", "cool"): {
        "season_name": "Light Cool Summer",
        "season_description": "Porcelain skin with subtle rosy or bluish undertones, complemented by soft pastels and cool misty hues.",
        "primary_palette": ["#A0C4FF", "#BDB2FF", "#F7CAD0", "#C5C6C7", "#778DA9", "#E2E2E2", "#6B7280", "#5B8FB9"],
        "palettes": {
            "soft_summer": ["#A0C4FF", "#BDB2FF", "#F7CAD0", "#FFC6FF", "#E7C6FF"],
            "cool_slate": ["#778DA9", "#415A77", "#1B263B", "#6B7280", "#5B8FB9"],
            "pearl_neutrals": ["#F8F9FA", "#E9ECEF", "#DEE2E6", "#CED4DA", "#6C757D"]
        },
        "styling_advice": "Dusty rose, powder blue, and cool lavender illuminate your features. Avoid stark orange and brassy yellow."
    },
    ("fair", "neutral"): {
        "season_name": "Soft Fair Neutral",
        "season_description": "Even, balanced fair skin that effortlessly rocks gentle muted tones, champagnes, and soft dusty greens.",
        "primary_palette": ["#E8D8C8", "#99A799", "#D3C5E5", "#D5B4B4", "#F4EEFF", "#A2B29F", "#BCB682", "#73777B"],
        "palettes": {
            "soft_champagne": ["#E8D8C8", "#F4EEFF", "#D3C5E5", "#D5B4B4", "#C8B6A6"],
            "sage_harmony": ["#99A799", "#A2B29F", "#BCB682", "#B0BBBF", "#8F9779"],
            "muted_basics": ["#EFEFEF", "#DCDCDC", "#A8A8A8", "#73777B", "#4A4E69"]
        },
        "styling_advice": "Soft rose gold, muted sage, and oyster grey highlight your complexion. Highly adaptable to both silver and gold."
    },

    # 2. LIGHT COMPLEXIONS (65 <= L* < 75)
    ("light", "warm"): {
        "season_name": "Clear Warm Spring",
        "season_description": "Bright golden-apricot undertones that come alive with clear, vibrant warm tones and rich creams.",
        "primary_palette": ["#F39C12", "#16A085", "#E67E22", "#F1C40F", "#27AE60", "#FDEBD0", "#D35400", "#1ABC9C"],
        "palettes": {
            "vibrant_spring": ["#F39C12", "#E67E22", "#F1C40F", "#D35400", "#E74C3C"],
            "warm_turquoise": ["#16A085", "#1ABC9C", "#27AE60", "#2ECC71", "#34495E"],
            "honey_neutrals": ["#FDEBD0", "#F5CBA7", "#EDBB99", "#E59866", "#BA4A00"]
        },
        "styling_advice": "Golden honey, warm apricot, and warm turquoise pop brilliantly. Complement with cream and rich tan."
    },
    ("light", "cool"): {
        "season_name": "Cool True Summer",
        "season_description": "Delicate pink-cool complexion that pairs elegantly with dusty berry, French navy, and heather lilac.",
        "primary_palette": ["#4A90E2", "#9B51E0", "#C2185B", "#607D8B", "#7986CB", "#B39DDB", "#90A4AE", "#37474F"],
        "palettes": {
            "french_blues": ["#4A90E2", "#5C6BC0", "#3F51B5", "#283593", "#1A237E"],
            "berry_accents": ["#9B51E0", "#C2185B", "#AD1457", "#880E4F", "#B39DDB"],
            "cool_greys": ["#ECEFF1", "#CFD8DC", "#90A4AE", "#607D8B", "#37474F"]
        },
        "styling_advice": "French blue, cool raspberry, and heather lilac frame your face beautifully. Pair with cool grey and brushed silver."
    },
    ("light", "neutral"): {
        "season_name": "Light Soft Neutral",
        "season_description": "Refined neutral undertones that balance cool blues and warm earth shades with modern sophistication.",
        "primary_palette": ["#5C6B73", "#9DB4C0", "#C2DFE3", "#E0FBFC", "#8D6E63", "#A1887F", "#BCAAA4", "#455A64"],
        "palettes": {
            "muted_teal": ["#5C6B73", "#9DB4C0", "#C2DFE3", "#E0FBFC", "#253237"],
            "almond_earth": ["#8D6E63", "#A1887F", "#BCAAA4", "#D7CCC8", "#6D4C41"],
            "urban_slate": ["#ECEFF1", "#CFD8DC", "#78909C", "#546E7A", "#37474F"]
        },
        "styling_advice": "Dusty teal, rosewood, and soft charcoal provide effortlessly chic, understated elegance."
    },

    # 3. MEDIUM COMPLEXIONS (52 <= L* < 65)
    ("medium", "warm"): {
        "season_name": "Warm True Autumn",
        "season_description": "Rich golden-olive undertones that harmonize with earth tones, terracotta, forest greens, and burnt sienna.",
        "primary_palette": ["#C07D38", "#4A5D23", "#80382B", "#D9A05B", "#263F36", "#B47A57", "#E4CDA5", "#8C5835"],
        "palettes": {
            "warm_autumn": ["#80382B", "#C07D38", "#4A5D23", "#D9A05B", "#683B2B"],
            "earthy_forest": ["#263F36", "#B47A57", "#E4CDA5", "#8C5835", "#C49A45"],
            "golden_cognac": ["#D4AF37", "#9E6D38", "#4E3629", "#F3E5AB", "#7B3F00"]
        },
        "styling_advice": "Terracotta, olive green, mustard gold, and warm rust flatter your natural radiance. Pair with warm camel outerwear."
    },
    ("medium", "cool"): {
        "season_name": "Cool Jewel Winter",
        "season_description": "Crisp, defined complexion with cool undertones that excels in high-contrast jewel tones and pure navy.",
        "primary_palette": ["#003366", "#4B0082", "#800020", "#2E8B57", "#4682B4", "#1A2B4C", "#5C2C47", "#E6ECF5"],
        "palettes": {
            "jewel_tones": ["#003366", "#4B0082", "#800020", "#2E8B57", "#4682B4"],
            "winter_night": ["#1A2B4C", "#5C2C47", "#8A9EA7", "#E6ECF5", "#22223B"],
            "cool_contrast": ["#0D1B2A", "#1B263B", "#415A77", "#778DA9", "#E0E1DD"]
        },
        "styling_advice": "Deep emerald, royal cobalt, ruby wine, and crisp optical white deliver striking contrast."
    },
    ("medium", "neutral"): {
        "season_name": "Medium Classic Neutral",
        "season_description": "Versatile olive or beige complexion that effortlessly shifts between warm camel and cool navy.",
        "primary_palette": ["#1B263B", "#415A77", "#778DA9", "#E0E1DD", "#A37081", "#555B6E", "#89B0AE", "#2B2D42"],
        "palettes": {
            "classic_chic": ["#1B263B", "#415A77", "#778DA9", "#E0E1DD", "#A37081"],
            "soft_neutral": ["#263F36", "#B47A57", "#E4CDA5", "#555B6E", "#89B0AE"],
            "metropolitan": ["#2B2D42", "#8D99AE", "#EDF2F4", "#EF233C", "#D90429"]
        },
        "styling_advice": "Rich navy, heather taupe, and deep plum form your ultimate capsule wardrobe. Both gold and silver shine."
    },

    # 4. TAN COMPLEXIONS (40 <= L* < 52)
    ("tan", "warm"): {
        "season_name": "Deep Warm Autumn",
        "season_description": "Sun-kissed bronze complexion enhanced by rich ochre, deep marigold, toasted cinnamon, and olive pine.",
        "primary_palette": ["#A0522D", "#DAA520", "#556B2F", "#8B4513", "#CD853F", "#2E473B", "#B8860B", "#D2691E"],
        "palettes": {
            "spiced_bronze": ["#A0522D", "#DAA520", "#CD853F", "#B8860B", "#D2691E"],
            "deep_greens": ["#556B2F", "#2E473B", "#1E3F20", "#3E5622", "#4B5320"],
            "cognac_earth": ["#8B4513", "#A0522D", "#6F4E37", "#5C4033", "#3D2B1F"]
        },
        "styling_advice": "Toasted cinnamon, golden mustard, and deep forest green highlight warm bronze undertones. Chunky gold jewelry excels."
    },
    ("tan", "cool"): {
        "season_name": "True Contrast Winter",
        "season_description": "Striking tan complexion with cool or neutral-cool undertones that commands bold, vivid jewel contrast.",
        "primary_palette": ["#0047AB", "#FF1493", "#191970", "#008080", "#DC143C", "#F8F8FF", "#4169E1", "#2F4F4F"],
        "palettes": {
            "vivid_contrast": ["#0047AB", "#FF1493", "#DC143C", "#4169E1", "#7B1FA2"],
            "midnight_teal": ["#191970", "#008080", "#004D40", "#01579B", "#2F4F4F"],
            "stark_modern": ["#F8F8FF", "#E0E0E0", "#9E9E9E", "#424242", "#212121"]
        },
        "styling_advice": "Cobalt blue, deep fuchsia, and teal create electrifying contrast against your tan complexion. Pair with pure white."
    },
    ("tan", "neutral"): {
        "season_name": "Rich Tan Neutral",
        "season_description": "Deeply saturated neutral complexion that carries dramatic dark neutrals, rich plums, and toasted walnuts.",
        "primary_palette": ["#3E2723", "#4A148C", "#263238", "#37474F", "#795548", "#827717", "#D7CCC8", "#5D4037"],
        "palettes": {
            "toasted_walnut": ["#3E2723", "#5D4037", "#795548", "#8D6E63", "#D7CCC8"],
            "deep_plum": ["#4A148C", "#6A1B9A", "#7B1FA2", "#8E24AA", "#AB47BC"],
            "slate_shadow": ["#263238", "#37474F", "#455A64", "#546E7A", "#78909C"]
        },
        "styling_advice": "Charcoal, deep mulberry, and olive brown create luxurious depth. Use cream accents for a polished lift."
    },

    # 5. DEEP COMPLEXIONS (L* < 40)
    ("deep", "warm"): {
        "season_name": "Rich Deep Autumn",
        "season_description": "Magnificent deep complexion with rich golden-red undertones, radiant in burnished copper, sienna, and burgundy.",
        "primary_palette": ["#581845", "#36190D", "#CD7F32", "#C70039", "#3D402B", "#641E16", "#78281F", "#D35400"],
        "palettes": {
            "burnished_copper": ["#CD7F32", "#D35400", "#E67E22", "#BA4A00", "#B9770E"],
            "regal_burgundy": ["#581845", "#641E16", "#78281F", "#C70039", "#900C3F"],
            "espresso_gold": ["#36190D", "#4A235A", "#1B4F72", "#117A65", "#7D6608"]
        },
        "styling_advice": "Burnished copper, rich burgundy, and deep olive look regal. Warm metals and fiery accents bring extraordinary glow."
    },
    ("deep", "cool"): {
        "season_name": "Deep Contrast Winter",
        "season_description": "Exquisite obsidian and deep espresso skin with cool undertones, possessing the highest visual contrast capability.",
        "primary_palette": ["#1D3557", "#FFFFFF", "#0F4C3A", "#9B2226", "#023E8A", "#7209B7", "#000000", "#F72585"],
        "palettes": {
            "high_voltage": ["#023E8A", "#7209B7", "#F72585", "#9B2226", "#1D3557"],
            "pure_contrast": ["#FFFFFF", "#000000", "#0F4C3A", "#E63946", "#F1FAEE"],
            "royal_monarch": ["#03045E", "#023E8A", "#0077B6", "#0096C7", "#00B4D8"]
        },
        "styling_advice": "Optic white, pure black, electric cobalt, and vivid ruby crimson look breathtaking. Maximum contrast is your superpower."
    },
    ("deep", "neutral"): {
        "season_name": "Luxe Deep Neutral",
        "season_description": "Commanding deep complexion that harmonizes with midnight plum, dark peacock teal, and graphite silver.",
        "primary_palette": ["#212529", "#3A0CA3", "#0B525B", "#4A0E17", "#6C757D", "#2B2D42", "#495057", "#14213D"],
        "palettes": {
            "midnight_peacock": ["#0B525B", "#1B4965", "#3A0CA3", "#2B2D42", "#14213D"],
            "graphite_luxe": ["#212529", "#495057", "#6C757D", "#ADB5BD", "#CED4DA"],
            "dark_mulberry": ["#4A0E17", "#3B0910", "#540D18", "#7209B7", "#560BAD"]
        },
        "styling_advice": "Deep peacock teal, graphite, and dark mulberry frame your silhouette with peerless modern luxury."
    }
}

SKIN_TONE_CATEGORIES = {
    "fair": {"L_min": 75, "undertone_hint": "cool"},
    "light": {"L_min": 65, "undertone_hint": "neutral"},
    "medium": {"L_min": 52, "undertone_hint": "warm"},
    "tan": {"L_min": 40, "undertone_hint": "warm"},
    "deep": {"L_min": 0, "undertone_hint": "neutral"}
}

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

def rgb_to_lab(r: int, g: int, b: int):
    """Approximate RGB to CIELAB conversion."""
    r_lin = r / 255.0
    g_lin = g / 255.0
    b_lin = b / 255.0
    L = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
    L = 116.0 * (L ** (1/3) if L > 0.008856 else (7.787 * L + 16/116)) - 16
    a = 500.0 * ((r_lin - g_lin) * 0.5)
    b_val = 200.0 * ((g_lin - b_lin) * 0.5)
    return L, a, b_val

def estimate_undertone(r: int = 128, g: int = 128, b: int = 128) -> str:
    """
    Heuristic undertone determination:
    Warm: higher yellow/red ratio (R > G > B with notable yellow component)
    Cool: higher blue/pink component (B or R-B balance)
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

def calculate_ita(L_star: float, b_star: float) -> float:
    """
    Individual Typology Angle (ITA) in degrees:
    ITA = arctan((L* - 50) / (b* - 128)) * (180 / pi)
    Standard dermatological metric for skin pigmentation.
    """
    b_centered = b_star - 128.0
    if abs(b_centered) < 0.001:
        return 90.0 if (L_star - 50.0) >= 0 else -90.0
    rad = math.atan((L_star - 50.0) / b_centered)
    return round(float(math.degrees(rad)), 1)

def get_recommended_palettes(undertone: str, skin_tone: str) -> dict:
    """
    Retrieves tailored 8-swatch primary palette, sub-palettes, and styling profile
    based on the full 15-combination matrix (Skin Depth x Undertone).
    """
    u_key = (undertone or "neutral").lower()
    if u_key not in ["warm", "cool", "neutral"]:
        u_key = "neutral"
        
    s_key = (skin_tone or "medium").lower()
    if s_key not in ["fair", "light", "medium", "tan", "deep"]:
        s_key = "medium"
        
    combo_key = (s_key, u_key)
    profile = SEASONAL_PALETTES.get(combo_key, SEASONAL_PALETTES[("medium", "warm")])
    
    return {
        "undertone": u_key,
        "skin_tone": s_key,
        "season_name": profile["season_name"],
        "season_description": profile["season_description"],
        "palettes": profile["palettes"],
        "primary_palette": profile["primary_palette"],
        "styling_advice": profile["styling_advice"]
    }
