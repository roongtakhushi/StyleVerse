import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, db_instance, COLLECTIONS
from app.routes import auth, users, skin, wardrobe, outfits, planner

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="STYLEVERSE – AI-Powered Personalized Fashion Styling and Outfit Recommendation System API"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory static mount
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Application lifecycle
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Database health-check endpoint (sanitized - no sensitive URI or credentials)
@app.get("/api/health", tags=["Health"])
@app.get("/health", tags=["Health"])
async def health_check():
    db_connected = False
    mode = "atlas"
    
    if db_instance.is_fallback and db_instance.db is not None:
        db_connected = True
        mode = "resilient_local"
    elif db_instance.client is not None and db_instance.db is not None:
        try:
            ping_status = await db_instance.client.admin.command('ping')
            db_connected = ping_status.get("ok") == 1.0
        except Exception:
            db_connected = False
            
    return {
        "status": "online" if db_connected else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": {
            "name": settings.DATABASE_NAME,
            "connected": db_connected,
            "collections_status": "ready" if db_connected else "unavailable",
            "storage_mode": mode
        }
    }

# Register all API endpoints under /api
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(skin.router, prefix=settings.API_V1_STR)
app.include_router(wardrobe.router, prefix=settings.API_V1_STR)
app.include_router(outfits.router, prefix=settings.API_V1_STR)
app.include_router(planner.router, prefix=settings.API_V1_STR)
