"""CR-017 Unlock Animation System API routes."""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.dependencies import get_current_user
from app.models.user import User
from app.schemas.unlock_record import (
    UnlockRecordCreate,
    UnlockRecordResponse,
    UnlockBatchRequest,
    UnlockBatchResponse,
    MarkViewedRequest,
    MarkViewedResponse,
    UnlockListResponse,
)
from app.services.unlock_service import UnlockService

router = APIRouter(prefix="/cr017/unlock", tags=["CR-017 Unlock"])


@router.post("/record", response_model=UnlockRecordResponse)
async def record_unlock(
    request: UnlockRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record a new unlock event."""
    service = UnlockService(db)
    record = await service.record_unlock(
        user_id=current_user.id,
        unlock_type=request.unlock_type,
        content_id=request.content_id,
        title=request.title,
        description=request.description,
        image_url=request.image_url,
        rarity=request.rarity,
        reward_data=request.reward_data,
    )
    return record


@router.get("/list", response_model=UnlockListResponse)
async def get_unlock_list(
    unlock_type: Optional[str] = Query(None, description="Filter by unlock type"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's unlock records."""
    service = UnlockService(db)
    records = await service.get_user_unlocks(
        user_id=current_user.id,
        unlock_type=unlock_type,
    )
    return UnlockListResponse(
        records=[UnlockRecordResponse.model_validate(r) for r in records],
        total=len(records),
    )


@router.get("/pending", response_model=UnlockListResponse)
async def get_pending_unlocks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get unviewed unlock records."""
    service = UnlockService(db)
    records = await service.get_pending_unlocks(user_id=current_user.id)
    return UnlockListResponse(
        records=[UnlockRecordResponse.model_validate(r) for r in records],
        total=len(records),
    )


@router.post("/mark-viewed", response_model=MarkViewedResponse)
async def mark_unlock_viewed(
    request: MarkViewedRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark an unlock record as viewed."""
    service = UnlockService(db)
    
    # Verify the record belongs to the user
    record = await service.get_unlock_by_id(UUID(request.record_id))
    if not record:
        raise HTTPException(status_code=404, detail="Unlock record not found")
    if record.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this record")
    
    updated_record = await service.mark_as_viewed(UUID(request.record_id))
    return MarkViewedResponse(
        success=True,
        record_id=request.record_id,
        viewed=updated_record.viewed,
    )


@router.post("/batch", response_model=UnlockBatchResponse)
async def batch_record_unlocks(
    request: UnlockBatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record multiple unlocks in batch."""
    service = UnlockService(db)
    records = await service.batch_record_unlocks(
        user_id=current_user.id,
        unlocks=request.unlocks,
    )
    return UnlockBatchResponse(
        success=True,
        recorded_count=len(records),
        records=[UnlockRecordResponse.model_validate(r) for r in records],
    )
