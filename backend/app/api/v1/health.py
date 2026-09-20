"""Health check endpoint."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.core.config import settings
import os

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint for liveness probes."""
    return {
        "status": "ok",
        "version": settings.app_version,
    }


@router.get("/download/admin-spec")
@router.head("/download/admin-spec")
async def download_admin_spec():
    """Download admin system specification document."""
    file_path = "/app/static/admin-system-detailed-spec.md"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename="admin-system-detailed-spec.md",
        media_type="application/octet-stream"
    )
