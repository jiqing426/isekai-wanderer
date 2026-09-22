"""CR-016 Subscription API endpoints — Phase 2.

Endpoints:
- GET  /api/subscription/status        → Get current subscription status
- POST /api/subscription/create        → Create subscription (mock payment)
- POST /api/subscription/cancel        → Cancel subscription
"""

from uuid import UUID
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional

from app.core.database import get_db
from app.core.exceptions import AppException
from app.api.v1.auth import get_current_user_id
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionTier, SubscriptionStatus
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/cr016/subscription", tags=["subscription-cr016"])


# ---- Request/Response Schemas ----

class CreateSubscriptionRequest(BaseModel):
    """Request to create a subscription."""
    tier: str = Field(..., description="Subscription tier: basic/standard/premium")
    cycle: str = Field(default="monthly", description="Billing cycle: monthly/yearly")


class CreateSubscriptionResponse(BaseModel):
    """Response after creating subscription."""
    status: str
    subscription_id: str
    tier: str
    expires_at: str
    quota_updated: bool
    action: str = Field(default="created", description="created/upgraded/renewed/downgrade_scheduled")
    pending_tier: Optional[str] = None
    message: str = ""


class CancelSubscriptionResponse(BaseModel):
    """Response after cancelling subscription."""
    subscription_id: str
    status: str
    expires_at: Optional[str]
    message: str


class SubscriptionStatusResponse(BaseModel):
    """Response for subscription status."""
    tier: str
    status: str
    started_at: Optional[str] = None
    expires_at: Optional[str] = None
    billing_cycle: Optional[str] = None
    pending_tier: Optional[str] = None
    permissions: dict
    is_exempt_from_quota: bool


# ---- Constants ----

# Price map for mock payment
PRICE_MAP = {
    "basic": {"monthly": 1.99, "yearly": 19.99},
    "standard": {"monthly": 4.99, "yearly": 49.99},
    "premium": {"monthly": 9.99, "yearly": 99.99},
}


# ---- Endpoints ----

@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status_cr016(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current subscription status (CR-016).
    
    Returns tier, status, expiration, and permissions.
    """
    uid = UUID(user_id)
    subscription_service = SubscriptionService(db)
    
    # Get user tier
    tier = await subscription_service.get_user_tier(uid)
    
    # Get permissions
    permissions_obj = await subscription_service.get_tier_permissions(tier)
    permissions = permissions_obj.model_dump()
    
    # Check if exempt from quota
    is_exempt = await subscription_service.is_exempt_from_quota(uid)
    
    # Get subscription record for expires_at
    sub = await subscription_service.get_user_subscription(uid)
    started_at = sub.started_at.isoformat() if sub and sub.started_at else None
    expires_at = sub.expires_at.isoformat() if sub and sub.expires_at else None
    billing_cycle = sub.billing_cycle if sub else None
    pending_tier = sub.pending_tier if sub else None
    
    # Determine status
    if sub:
        status = sub.status
    else:
        status = "none" if tier == "free" else "active"
    
    return SubscriptionStatusResponse(
        tier=tier,
        status=status,
        started_at=started_at,
        expires_at=expires_at,
        billing_cycle=billing_cycle,
        pending_tier=pending_tier,
        permissions=permissions,
        is_exempt_from_quota=is_exempt,
    )


# Tier ordering for upgrade/downgrade comparison
TIER_RANK = {"free": 0, "basic": 1, "standard": 2, "premium": 3}


@router.post("/create", response_model=CreateSubscriptionResponse)
async def create_subscription_cr016(
    request: CreateSubscriptionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create/upgrade/renew subscription (mock payment, CR-016).

    Rules:
    - Upgrade (basic→standard→premium): immediately effective, remaining days added to new cycle
    - Same-tier renew (premium monthly → premium yearly): remaining days added
    - Downgrade (premium→standard): NOT immediate — sets pending_tier, current period continues,
      auto-downgrades when expires_at passes
    """
    uid = UUID(user_id)

    # Validate tier
    valid_tiers = ["basic", "standard", "premium"]
    if request.tier not in valid_tiers:
        raise AppException("INVALID_TIER", 400, f"Invalid tier: {request.tier}")

    # Validate cycle
    if request.cycle not in ["monthly", "yearly"]:
        raise AppException("INVALID_CYCLE", 400, f"Invalid cycle: {request.cycle}")

    subscription_service = SubscriptionService(db)

    # Calculate new cycle days
    new_days = 30 if request.cycle == "monthly" else 365
    now = datetime.now(timezone.utc)

    # Check for existing active subscription
    existing_sub = await subscription_service.get_user_subscription(uid)

    if existing_sub and existing_sub.tier != "free":
        current_rank = TIER_RANK.get(existing_sub.tier, 0)
        new_rank = TIER_RANK.get(request.tier, 0)

        if new_rank > current_rank:
            # === UPGRADE ===
            # Remaining days from current subscription
            remaining_days = 0
            if existing_sub.expires_at and existing_sub.expires_at > now:
                remaining_delta = existing_sub.expires_at - now
                remaining_days = remaining_delta.total_seconds() / 86400
                # Round up to full days
                import math
                remaining_days = math.ceil(remaining_days)

            new_expires = now + timedelta(days=new_days + remaining_days)

            existing_sub.tier = request.tier
            existing_sub.status = SubscriptionStatus.active.value
            existing_sub.expires_at = new_expires
            existing_sub.started_at = now
            existing_sub.billing_cycle = request.cycle
            existing_sub.pending_tier = None  # Clear any pending downgrade
            sub_id = existing_sub.id

            # Update user tier immediately
            result = await db.execute(select(User).where(User.id == uid))
            user = result.scalar_one()
            user.subscription_tier = request.tier

            await db.flush()

            return CreateSubscriptionResponse(
                status="success",
                subscription_id=str(sub_id),
                tier=request.tier,
                expires_at=new_expires.isoformat(),
                quota_updated=True,
                action="upgraded",
                message=f"升级成功！已将剩余 {remaining_days} 天叠加到新周期，到期时间 {new_expires.strftime('%Y-%m-%d')}",
            )

        elif new_rank == current_rank:
            # === SAME-TIER RENEW ===
            # Add new cycle days to existing expires_at (or now if expired)
            base = existing_sub.expires_at if existing_sub.expires_at and existing_sub.expires_at > now else now
            new_expires = base + timedelta(days=new_days)

            existing_sub.status = SubscriptionStatus.active.value
            existing_sub.expires_at = new_expires
            existing_sub.billing_cycle = request.cycle
            existing_sub.pending_tier = None
            sub_id = existing_sub.id

            result = await db.execute(select(User).where(User.id == uid))
            user = result.scalar_one()
            user.subscription_tier = request.tier

            await db.flush()

            return CreateSubscriptionResponse(
                status="success",
                subscription_id=str(sub_id),
                tier=request.tier,
                expires_at=new_expires.isoformat(),
                quota_updated=True,
                action="renewed",
                message=f"续费成功！到期时间延长至 {new_expires.strftime('%Y-%m-%d')}",
            )

        else:
            # === DOWNGRADE ===
            # Don't change current tier/expires_at — schedule for after current period
            existing_sub.pending_tier = request.tier
            existing_sub.billing_cycle = request.cycle  # New cycle for when downgrade takes effect
            sub_id = existing_sub.id

            # DON'T update user.subscription_tier — current tier stays until expiry

            await db.flush()

            expires_str = existing_sub.expires_at.strftime('%Y-%m-%d') if existing_sub.expires_at else "未知"

            return CreateSubscriptionResponse(
                status="success",
                subscription_id=str(sub_id),
                tier=existing_sub.tier,  # Current tier, not new
                expires_at=existing_sub.expires_at.isoformat() if existing_sub.expires_at else "",
                quota_updated=False,
                action="downgrade_scheduled",
                pending_tier=request.tier,
                message=f"降级已预约！当前 {existing_sub.tier} 会员有效期至 {expires_str}，到期后自动降级为 {request.tier} 会员",
            )

    else:
        # === NEW SUBSCRIPTION (no existing or was free) ===
        expires_at = now + timedelta(days=new_days)
        subscription = await subscription_service.on_subscription_created(
            user_id=uid,
            tier=request.tier,
            expires_at=expires_at,
        )
        subscription.billing_cycle = request.cycle
        subscription.pending_tier = None
        sub_id = subscription.id

        # Update user tier
        result = await db.execute(select(User).where(User.id == uid))
        user = result.scalar_one()
        user.subscription_tier = request.tier

        # CR-044: Fragment granting is handled by process_monthly_grants cron job
        # Do not grant on subscription creation — wait for monthly cycle
        # await subscription_service._grant_fragments(uid, request.tier)

        await db.flush()

        return CreateSubscriptionResponse(
            status="success",
            subscription_id=str(sub_id),
            tier=request.tier,
            expires_at=expires_at.isoformat(),
            quota_updated=True,
            action="created",
            message=f"订阅成功！{request.tier} 会员，到期时间 {expires_at.strftime('%Y-%m-%d')}",
        )


@router.post("/cancel", response_model=CancelSubscriptionResponse)
async def cancel_subscription_cr016(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Cancel active subscription (CR-016).
    
    User keeps premium until expires_at, then downgrades to free.
    """
    uid = UUID(user_id)
    subscription_service = SubscriptionService(db)
    
    # Get active subscription
    sub = await subscription_service.get_user_subscription(uid)
    
    if not sub:
        raise AppException("NO_SUBSCRIPTION", 400, "No active subscription to cancel")
    
    # Mark as cancelled
    sub.status = SubscriptionStatus.cancelled.value
    sub.cancelled_at = datetime.now(timezone.utc)
    
    await db.flush()
    
    return CancelSubscriptionResponse(
        subscription_id=str(sub.id),
        status="cancelled",
        expires_at=sub.expires_at.isoformat() if sub.expires_at else None,
        message="Subscription cancelled. Access continues until expiry.",
    )
