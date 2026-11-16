from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field

# User Schemas
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    gender_preference: Optional[str] = "unisex"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    gender_preference: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Style Profile Schemas
class StylePreferencesUpdate(BaseModel):
    gender_preference: Optional[str] = None
    preferred_styles: Optional[List[str]] = None
    preferred_occasions: Optional[List[str]] = None
    favourite_colors: Optional[List[str]] = None

class StyleProfileResponse(BaseModel):
    user_id: str
    skin_tone_estimate: Optional[str] = "medium"
    undertone: Optional[str] = "neutral"
    undertone_confirmed: bool = False
    preferred_styles: List[str] = ["casual", "streetwear"]
    preferred_occasions: List[str] = ["daily", "college"]
    colour_palette: List[str] = []
    favourite_colors: List[str] = []

# Skin Analysis Schemas
class SkinToneConfirm(BaseModel):
    undertone: str  # warm, cool, neutral
    skin_tone: Optional[str] = None

class SkinAnalysisResponse(BaseModel):
    estimated_skin_tone: str
    estimated_undertone: str
    sample_hex: str
    suggested_palettes: Dict[str, List[str]]
    primary_palette: List[str]
    requires_confirmation: bool = True

# Wardrobe Schemas
class WardrobeItemResponse(BaseModel):
    id: str
    user_id: str
    image_url: str
    category: str
    subcategory: str
    dominant_colors: List[str]
    pattern: str = "solid"
    style: str = "casual"
    gender_category: str = "unisex"
    created_at: datetime

# Outfit Schemas
class OutfitGenerateRequest(BaseModel):
    occasion: str = "casual"
    style: Optional[str] = "casual"
    gender_category: Optional[str] = "unisex"
    use_wardrobe: bool = True

class OutfitItemDetail(BaseModel):
    id: str
    category: str
    subcategory: str
    image_url: str
    dominant_colors: List[str]
    style: str

class OutfitRecommendationResponse(BaseModel):
    id: str
    user_id: str
    occasion: str
    style: str
    compatibility_score: float
    explanation: str
    items: Dict[str, Any]
    created_at: datetime

class OutfitSaveRequest(BaseModel):
    outfit_id: Optional[str] = None
    occasion: Optional[str] = "casual"
    style: Optional[str] = "casual"
    compatibility_score: Optional[float] = 90.0
    explanation: Optional[str] = ""
    top_id: Optional[str] = None
    bottom_id: Optional[str] = None
    footwear_id: Optional[str] = None
    dress_id: Optional[str] = None
    outerwear_id: Optional[str] = None
    items: Optional[Dict[str, Any]] = None
    rating: Optional[int] = 5

class SavedOutfitResponse(BaseModel):
    id: str
    user_id: str
    outfit_id: str
    occasion: str
    style: str
    compatibility_score: float
    explanation: str
    top_id: Optional[str] = None
    bottom_id: Optional[str] = None
    footwear_id: Optional[str] = None
    dress_id: Optional[str] = None
    outerwear_id: Optional[str] = None
    items: Optional[Dict[str, Any]] = None
    is_favourite: bool = True
    rating: int = 5
    saved_at: datetime

class OutfitPlanRequest(BaseModel):
    date: str  # YYYY-MM-DD
    occasion: str
    outfit_id: str
    status: Optional[str] = "planned"

