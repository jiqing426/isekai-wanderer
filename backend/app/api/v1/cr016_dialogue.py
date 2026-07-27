"""CR-016 Dialogue Quota API endpoints — Phase 2.

Endpoints:
- GET /api/dialogue/quota/status  → Get current quota status
- GET /api/dialogue/lifecycle     → Get lifecycle information
"""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_user_id
from app.services.quota_service import QuotaService

router = APIRouter(prefix="/cr016/dialogue", tags=["dialogue-cr016"])


# ---- Response Schemas ----

class QuotaStatusResponse(BaseModel):
    """Response for quota status."""
    base_quota: int
    consumed: int
    fragment_extra: int
    fragment_consumed: int
    remaining: int  # -1 means unlimited
    is_exempt: bool


class LifecycleResponse(BaseModel):
    """Response for lifecycle information."""
    stage: str  # honeymoon/growth/regular/returnee
    days_since_registration: int
    days_since_last_login: Optional[int]
    daily_base_quota: int


# ---- Endpoints ----

@router.get("/quota/status", response_model=QuotaStatusResponse)
async def get_quota_status(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current quota status (CR-016).
    
    Returns:
    - base_quota: Daily base quota based on lifecycle stage
    - consumed: How much base quota has been used today
    - fragment_extra: Extra quota purchased with fragments
    - fragment_consumed: How much fragment quota has been used today
    - remaining: Total remaining quota (-1 = unlimited for subscribed users)
    - is_exempt: Whether user is exempt from quota (subscribed users)
    """
    uid = UUID(user_id)
    quota_service = QuotaService(db)
    
    status = await quota_service.get_user_quota_status(uid)
    
    return QuotaStatusResponse(
        base_quota=status["base_quota"],
        consumed=status["consumed"],
        fragment_extra=status["fragment_extra"],
        fragment_consumed=status["fragment_consumed"],
        remaining=status["remaining"],
        is_exempt=status["is_exempt"],
    )


@router.get("/lifecycle", response_model=LifecycleResponse)
async def get_lifecycle_info(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get lifecycle information (CR-016).
    
    Returns:
    - stage: honeymoon (1-3 days) / growth (4-7 days) / regular (8+ days) / returnee
    - days_since_registration: Days since user registered
    - days_since_last_login: Days since last login (null if never logged in)
    - daily_base_quota: Base quota for current lifecycle stage
    """
    uid = UUID(user_id)
    quota_service = QuotaService(db)
    
    info = await quota_service.get_lifecycle_info(uid)
    
    return LifecycleResponse(
        stage=info["stage"],
        days_since_registration=info["days_since_registration"],
        days_since_last_login=info["days_since_last_login"],
        daily_base_quota=info["daily_base_quota"],
    )
