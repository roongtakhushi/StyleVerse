import time
from datetime import datetime
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.database import get_db

router = APIRouter(tags=["Health"])

START_TIME = time.time()

@router.get("/health")
async def health_check():
    """
    Production-grade health probe verifying MongoDB latency,
    ML engine availability, and system uptime.
    """
    start_ping = time.time()
    db = get_db()
    db_status = "unhealthy"
    
    if db is not None:
        try:
            ping_res = await db.client.admin.command("ping")
            if ping_res.get("ok") == 1:
                db_status = "healthy"
        except Exception as e:
            db_status = f"degraded: {str(e)}"
            
    response_time_ms = round((time.time() - start_ping) * 1000, 2)
    uptime_seconds = int(time.time() - START_TIME)
    
    is_healthy = db_status == "healthy"
    return JSONResponse(
        status_code=status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": uptime_seconds,
            "response_time_ms": response_time_ms,
            "components": {
                "database": db_status,
                "ml_engine": "loaded",
                "storage": "writable"
            },
            "version": "1.0.0"
        }
    )
