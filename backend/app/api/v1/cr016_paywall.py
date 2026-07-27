"""CR-016 Paywall API endpoints — Phase 2.

Endpoints:
- POST /api/paywall/check-trigger  → Check if paywall should trigger
- POST /api/paywall/record-event   → Record modal/banner shown
- GET  /api/paywall/daily-count    → Get today's modal count
"""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from app.core.database import get_db
from app.api.v1.auth import get_current_user_id
from app.services.paywall_service import PaywallService

router = APIRouter(prefix="/cr016/paywall", tags=["paywall-cr016"])


# ---- Request/Response Schemas ----

class CheckTriggerRequest(BaseModel):
    """Request to check paywall trigger."""
    scene: str = Field(..., description="Paywall scene: T1_quota/T2_archive/...")
    user_initiated: bool = Field(default=False, description="True if user clicked subscription entry")


class CheckTriggerResponse(BaseModel):
    """Response for paywall trigger check."""
    should_show: bool
    display_type: Optional[str] = None  # modal/banner/toast
    payload: Optional[Dict[str, Any]] = None
    scene: str
    user_id: str


class RecordEventRequest(BaseModel):
    """Request to record paywall event."""
    scene: str
    display_type: str = Field(..., description="modal/banner/toast")


class RecordEventResponse(BaseModel):
    """Response after recording event."""
    status: str
    message: str


class DailyCountResponse(BaseModel):
    """Response for daily modal count."""
    user_id: str
    modal_count: int
    max_allowed: int
    should_downgrade: bool


# ---- Endpoints ----

@router.post("/check-trigger", response_model=CheckTriggerResponse)
async def check_paywall_trigger(
    request: CheckTriggerRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Check if paywall should be triggered (CR-016).
    
    Rate limiting rules:
    - Registration <= 3 days Free users: only banner/toast (no modal)
    - Subscribed users (Basic/Standard/Premium): all guidance permanently disabled
    - Registration > 3 days Free users: normal trigger
    - Daily modal limit: 2 times, downgrade to banner if exceeded
    - User-initiated subscription entry: bypass rate limiting
    
    T1 special rules:
    - Honeymoon (1-3 days): only banner
    - Growth/Regular: modal (C29 popup with upgrade + fragment purchase)
    """
    uid = UUID(user_id)
    paywall_service = PaywallService(db)
    
    # User-initiated subscription entry bypasses rate limiting
    if request.user_initiated:
        # Still check if subscribed (subscribed users see nothing)
        from app.services.subscription_service import SubscriptionService
        sub_service = SubscriptionService(db)
        if await sub_service.is_exempt_from_quota(uid):
            return CheckTriggerResponse(
                should_show=False,
                display_type=None,
                payload=None,
                scene=request.scene,
                user_id=user_id,
            )
        # User-initiated: always show modal, bypass daily limit
        return CheckTriggerResponse(
            should_show=True,
            display_type="modal",
            payload={"reason": "user_initiated", "bypass_rate_limit": True},
            scene=request.scene,
            user_id=user_id,
        )
    
    # Normal trigger check
    result = await paywall_service.check_trigger(uid, request.scene)
    
    return CheckTriggerResponse(
        should_show=result["should_show"],
        display_type=result.get("display_type"),
        payload=result.get("payload"),
        scene=request.scene,
        user_id=user_id,
    )


@router.post("/record-event", response_model=RecordEventResponse)
async def record_paywall_event(
    request: RecordEventRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Record that a paywall event was shown (CR-016).
    
    This is called by the frontend after displaying a modal/banner/toast.
    Used for tracking daily modal count.
    """
    uid = UUID(user_id)
    paywall_service = PaywallService(db)
    
    await paywall_service.record_paywall_event(
        user_id=uid,
        scene=request.scene,
        display_type=request.display_type,
    )
    
    return RecordEventResponse(
        status="success",
        message=f"Recorded {request.display_type} for scene {request.scene}",
    )


@router.get("/daily-count", response_model=DailyCountResponse)
async def get_daily_modal_count(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get today's modal count (CR-016).
    
    Returns:
    - modal_count: Number of modals shown today
    - max_allowed: Maximum modals allowed per day (2)
    - should_downgrade: True if should show banner instead of modal
    """
    uid = UUID(user_id)
    paywall_service = PaywallService(db)
    
    modal_count = await paywall_service.get_daily_modal_count(uid)
    should_downgrade = await paywall_service.should_downgrade(uid)
    
    return DailyCountResponse(
        user_id=user_id,
        modal_count=modal_count,
        max_allowed=2,
        should_downgrade=should_downgrade,
    )
