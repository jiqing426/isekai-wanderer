"""CR-016 Subscription API endpoints — Phase 2.

Endpoints:
- GET  /api/subscription/status        → Get current subscription status
- POST /api/subscription/create        → Create subscription (mock payment)
- POST /api/subscription/cancel        → Cancel subscription
- POST /api/subscription/fragment-purchase → Fragment purchase for extra dialogue
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
from app.models.payment import Fragment, FragmentTransaction
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


class CancelSubscriptionResponse(BaseModel):
    """Response after cancelling subscription."""
    subscription_id: str
    status: str
    expires_at: Optional[str]
    message: str


class FragmentPurchaseRequest(BaseModel):
    """Request to purchase extra dialogue with fragments."""
    amount: int = Field(..., gt=0, description="Number of dialogue units to purchase (3 fragments = 1 unit)")


class FragmentPurchaseResponse(BaseModel):
    """Response after fragment purchase."""
    status: str
    fragments_spent: int
    dialogue_added: int
    new_fragment_balance: int
    message: str


class SubscriptionStatusResponse(BaseModel):
    """Response for subscription status."""
    tier: str
    status: str
    expires_at: Optional[str]
    permissions: dict
    is_exempt_from_quota: bool


# ---- Constants ----

# Fragment cost: 3 fragments = 1 dialogue unit
FRAGMENT_COST_PER_DIALOGUE = 3

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
    expires_at = sub.expires_at.isoformat() if sub and sub.expires_at else None
    
    # Determine status
    if sub:
        status = sub.status
    else:
        status = "none" if tier == "free" else "active"
    
    return SubscriptionStatusResponse(
        tier=tier,
        status=status,
        expires_at=expires_at,
        permissions=permissions,
        is_exempt_from_quota=is_exempt,
    )


@router.post("/create", response_model=CreateSubscriptionResponse)
async def create_subscription_cr016(
    request: CreateSubscriptionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a subscription (mock payment, CR-016).
    
    Mock payment logic:
    - Directly creates subscription record
    - Sets expires_at = now() + 30 days (monthly) or +365 days (yearly)
    - Updates user.subscription_tier
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
    
    # Calculate expiration
    days = 30 if request.cycle == "monthly" else 365
    expires_at = datetime.now(timezone.utc) + timedelta(days=days)
    
    # Check for existing active subscription
    existing_sub = await subscription_service.get_user_subscription(uid)
    
    if existing_sub:
        # Update existing subscription
        existing_sub.tier = request.tier
        existing_sub.status = SubscriptionStatus.active.value
        existing_sub.expires_at = expires_at
        existing_sub.started_at = datetime.now(timezone.utc)
        sub_id = existing_sub.id
    else:
        # Create new subscription
        subscription = await subscription_service.on_subscription_created(
            user_id=uid,
            tier=request.tier,
            expires_at=expires_at,
        )
        sub_id = subscription.id
    
    # Update user tier
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one()
    user.subscription_tier = request.tier
    
    await db.flush()
    
    return CreateSubscriptionResponse(
        status="success",
        subscription_id=str(sub_id),
        tier=request.tier,
        expires_at=expires_at.isoformat(),
        quota_updated=True,
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


@router.post("/fragment-purchase", response_model=FragmentPurchaseResponse)
async def fragment_purchase_dialogue(
    request: FragmentPurchaseRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Purchase extra dialogue quota with fragments (CR-016).
    
    Cost: 3 fragments = 1 dialogue unit.
    
    Logic:
    1. Check user fragment balance >= amount * 3
    2. Deduct fragments
    3. Call quota_service.add_fragment_quota(user_id, amount)
    """
    uid = UUID(user_id)
    
    # Calculate total fragment cost
    fragments_needed = request.amount * FRAGMENT_COST_PER_DIALOGUE
    
    # Lock the fragment row to prevent concurrent double-spend
    result = await db.execute(
        select(Fragment).where(Fragment.user_id == uid).with_for_update()
    )
    fragment_record = result.scalar_one_or_none()
    
    current_balance = fragment_record.balance if fragment_record else 0
    
    if current_balance < fragments_needed:
        raise AppException(
            "INSUFFICIENT_FRAGMENTS",
            402,
            f"Insufficient fragments. Need {fragments_needed}, have {current_balance}"
        )
    
    # Deduct fragments
    if not fragment_record:
        fragment_record = Fragment(user_id=uid, balance=0)
        db.add(fragment_record)
    
    fragment_record.balance -= fragments_needed
    
    # Record transaction
    transaction = FragmentTransaction(
        user_id=uid,
        amount=-fragments_needed,
        reason=f"dialogue_quota_purchase:{request.amount}",
    )
    db.add(transaction)
    
    # Add fragment quota (uses its own locking internally)
    from app.services.quota_service import QuotaService
    quota_service = QuotaService(db)
    await quota_service.add_fragment_quota(uid, request.amount)
    
    await db.flush()
    
    return FragmentPurchaseResponse(
        status="success",
        fragments_spent=fragments_needed,
        dialogue_added=request.amount,
        new_fragment_balance=fragment_record.balance,
        message=f"Purchased {request.amount} dialogue units for {fragments_needed} fragments",
    )
