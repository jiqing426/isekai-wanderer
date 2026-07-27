"""Health check endpoint."""

from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint for liveness probes."""
    return {
        "status": "ok",
        "version": settings.app_version,
    }
