import os
import sys

# Ensure both repository root (containing 'ml') and backend dir are in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.dirname(backend_dir)
for p in [project_root, backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

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

import re

class SlashMiddleware:
    """Normalizes duplicate consecutive slashes (e.g. //auth/login -> /auth/login) for client resilience."""
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            scope["path"] = re.sub(r"/+", "/", scope["path"])
        await self.app(scope, receive, send)

app.add_middleware(SlashMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CORSStaticFiles(StaticFiles):
    """
    Subclass of Starlette StaticFiles that injects permissive CORS and CORP headers
    so cross-origin frontends (e.g. Vercel) can render images without ORB or CORS blocking.
    """
    async def get_response(self, path: str, scope):
        try:
            response = await super().get_response(path, scope)
        except Exception:
            from starlette.responses import Response
            response = Response(status_code=404)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        response.headers["Cache-Control"] = "public, max-age=86400"
        return response

# Upload directory static mount with cross-origin headers
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", CORSStaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/api/uploads", CORSStaticFiles(directory=settings.UPLOAD_DIR), name="api_uploads")

# Application lifecycle
@app.on_event("startup")
async def startup_event():
    # Ensure default studio cutouts exist in upload dir if missing
    try:
        cutouts_dir = os.path.join(project_root, "test_samples", "studio_cutouts")
        if os.path.exists(cutouts_dir):
            import shutil
            for fname in os.listdir(cutouts_dir):
                src = os.path.join(cutouts_dir, fname)
                dest = os.path.join(settings.UPLOAD_DIR, f"studio_live_{fname}")
                if os.path.isfile(src) and not os.path.exists(dest):
                    shutil.copyfile(src, dest)
    except Exception as e:
        print(f"Startup asset copy notice: {e}")
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# Database health-check endpoint (sanitized - supports both GET and HEAD for free Uptime monitors)
@app.api_route("/api/health", methods=["GET", "HEAD"], tags=["Health"])
@app.api_route("/health", methods=["GET", "HEAD"], tags=["Health"])
@app.api_route("/", methods=["GET", "HEAD"], tags=["Health"])
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

# Register all API endpoints under /api and root aliases for total client URL resilience
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix="", tags=["Auth-Aliases"])

app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix="", tags=["Users-Aliases"])

app.include_router(skin.router, prefix=settings.API_V1_STR)
app.include_router(skin.router, prefix="", tags=["Skin-Aliases"])

app.include_router(wardrobe.router, prefix=settings.API_V1_STR)
app.include_router(wardrobe.router, prefix="", tags=["Wardrobe-Aliases"])

app.include_router(outfits.router, prefix=settings.API_V1_STR)
app.include_router(outfits.router, prefix="", tags=["Outfits-Aliases"])

app.include_router(planner.router, prefix=settings.API_V1_STR)
app.include_router(planner.router, prefix="", tags=["Planner-Aliases"])
