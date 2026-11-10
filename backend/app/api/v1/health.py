"""
Health Check Endpoint
=====================
GET /health — Operational monitoring endpoint for deployments (Render, Railway, Uptime)
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.dependencies import get_db

router = APIRouter()


@router.get("/health", summary="Application health check", tags=["Health"])
async def health_check(db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Checks MongoDB connectivity and returns application health status.
    Returns 200 OK if database ping succeeds; 503 if disconnected.
    """
    try:
        await db.command("ping")
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0",
        }
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(exc),
            },
        )
