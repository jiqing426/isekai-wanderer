"""Share API endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.share import ShareCard

router = APIRouter(prefix="/share", tags=["share"])


class ShareGenerateRequest(BaseModel):
    share_type: str  # "game_result" | "affection" | "achievement"
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


@router.post("/generate")
async def generate_share(
    req: ShareGenerateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Generate a share card."""
    card = ShareCard(
        user_id=UUID(user_id),
        share_type=req.share_type,
        title=req.title,
        description=req.description,
        image_url=req.image_url,
        extra_data=req.extra_data or {},
    )
    db.add(card)
    await db.commit()
    await db.refresh(card)

    return {
        "id": str(card.id),
        "share_type": card.share_type,
        "title": card.title,
        "description": card.description,
        "image_url": card.image_url,
        "extra_data": card.extra_data,
        "created_at": card.created_at.isoformat(),
    }


@router.get("/{share_id}")
async def get_share(
    share_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get share card content (public, no auth required)."""
    stmt = select(ShareCard).where(ShareCard.id == UUID(share_id))
    result = await db.execute(stmt)
    card = result.scalar_one_or_none()

    if not card:
        raise AppException(ErrorCode.SHARE_NOT_FOUND, 404, "Share card not found")

    return {
        "id": str(card.id),
        "user_id": str(card.user_id),
        "share_type": card.share_type,
        "title": card.title,
        "description": card.description,
        "image_url": card.image_url,
        "extra_data": card.extra_data,
        "created_at": card.created_at.isoformat(),
    }
