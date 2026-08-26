"""Lorebook API routes (CR-027 T-003).

Admin-only endpoints for managing world knowledge entries.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.auth import get_current_user_id
from app.models.user import User
from app.schemas.lorebook import (
    LorebookEntryCreate,
    LorebookEntryUpdate,
    LorebookEntryResponse,
    LorebookEntryListResponse,
)
from app.services.lorebook_service import LorebookService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lorebook", tags=["lorebook"])

lorebook_service = LorebookService()


async def require_admin(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Dependency: only admin users can access lorebook endpoints."""
    from sqlalchemy import select

    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_id


@router.get("", response_model=LorebookEntryListResponse)
async def list_entries(
    page: int = 1,
    page_size: int = 20,
    tag: str | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """List lorebook entries with pagination and optional tag filter."""
    return await lorebook_service.list(db, page=page, page_size=page_size, tag=tag)


@router.post("", response_model=LorebookEntryResponse)
async def create_entry(
    data: LorebookEntryCreate,
    db: AsyncSession = Depends(get_db),
    admin_id: str = Depends(require_admin),
):
    """Create a new lorebook entry."""
    return await lorebook_service.create(db, data, created_by=UUID(admin_id))


@router.get("/{entry_id}", response_model=LorebookEntryResponse)
async def get_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Get a lorebook entry by ID."""
    entry = await lorebook_service.get(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Lorebook entry not found")
    return entry


@router.put("/{entry_id}", response_model=LorebookEntryResponse)
async def update_entry(
    entry_id: UUID,
    data: LorebookEntryUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Update a lorebook entry."""
    entry = await lorebook_service.update(db, entry_id, data)
    if not entry:
        raise HTTPException(status_code=404, detail="Lorebook entry not found")
    return entry


@router.delete("/{entry_id}")
async def delete_entry(
    entry_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Soft delete a lorebook entry."""
    deleted = await lorebook_service.soft_delete(db, entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lorebook entry not found")
    return {"message": "Lorebook entry deleted"}
