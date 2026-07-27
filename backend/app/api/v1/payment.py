"""Payment Mock API endpoints.

DEPRECATED: Subscription-related endpoints use old table.
Use /api/v1/cr016/subscription/* for new subscription APIs.
"""

import logging
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.payment import Fragment, FragmentTransaction, Purchase, Subscription
from app.models.user import User
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payment", tags=["payment-deprecated"])


# --- Schemas ---

class SubscribeRequest(BaseModel):
    plan: str  # "free" | "basic" | "premium"
    billing_cycle: str = "monthly"  # "monthly" | "yearly"


class PurchaseRequest(BaseModel):
    item_id: str  # "fragments_100" | "fragments_500" | "stamina_5" | etc.
    item_name: str
    price: float
    currency: str = "USD"


class RechargeRequest(BaseModel):
    shards: int
    amount: float
    currency: str = "USD"
    provider: str = "mock"


# --- Constants ---

PLANS = {
    "free": {"price_monthly": 0, "price_yearly": 0, "daily_stamina": 10, "fragment_rate": 1.0},
    "basic": {"price_monthly": 4.99, "price_yearly": 49.99, "daily_stamina": 20, "fragment_rate": 1.5},
    "premium": {"price_monthly": 9.99, "price_yearly": 99.99, "daily_stamina": 50, "fragment_rate": 2.0},
}


# --- Endpoints ---

@router.get("/plans")
async def get_plans():
    """Get subscription plan list."""
    return {
        "plans": [
            {
                "id": plan_id,
                "name": plan_id.capitalize(),
                "price_monthly": info["price_monthly"],
                "price_yearly": info["price_yearly"],
                "daily_stamina": info["daily_stamina"],
                "fragment_rate": info["fragment_rate"],
            }
            for plan_id, info in PLANS.items()
        ]
    }


@router.post("/subscribe")
async def subscribe(
    req: SubscribeRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Mock subscription purchase."""
    if req.plan not in PLANS:
        raise AppException(ErrorCode.PAYMENT_UNKNOWN_PLAN, 400, f"Unknown plan: {req.plan}")

    plan_info = PLANS[req.plan]
    price = plan_info[f"price_{req.billing_cycle}"]

    # Cancel existing active subscriptions
    existing = await db.execute(
        select(Subscription).where(
            Subscription.user_id == UUID(user_id),
            Subscription.status == "active",
        )
    )
    for sub in existing.scalars().all():
        sub.status = "cancelled"
        sub.cancelled_at = datetime.utcnow()

    # Create new subscription
    expires = datetime.utcnow() + timedelta(days=30 if req.billing_cycle == "monthly" else 365)
    sub = Subscription(
        user_id=UUID(user_id),
        plan_id=req.plan,
        status="active",
        billing_cycle=req.billing_cycle,
        price=price,
        is_mock=True,
        expires_at=expires,
    )
    db.add(sub)

    # Update user subscription_tier
    user_result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = user_result.scalar_one()
    user.subscription_tier = req.plan

    await db.commit()

    return {
        "subscription_id": str(sub.id),
        "plan": req.plan,
        "billing_cycle": req.billing_cycle,
        "price": price,
        "currency": "USD",
        "status": "active",
        "expires_at": expires.isoformat(),
        "is_mock": True,
    }


@router.post("/purchase")
async def purchase(
    req: PurchaseRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Mock in-app purchase (fragments/stamina)."""
    record = Purchase(
        user_id=UUID(user_id),
        item_id=req.item_id,
        item_name=req.item_name,
        price=req.price,
        currency=req.currency,
        is_mock=True,
    )
    db.add(record)

    # If fragments purchase, add to balance
    if req.item_id.startswith("fragments"):
        amount = int(req.item_id.split("_")[1]) if "_" in req.item_id else 100
        frag_result = await db.execute(
            select(Fragment).where(Fragment.user_id == UUID(user_id))
        )
        frag = frag_result.scalar_one_or_none()
        if not frag:
            frag = Fragment(user_id=UUID(user_id), balance=amount)
            db.add(frag)
        else:
            frag.balance += amount

        txn = FragmentTransaction(
            user_id=UUID(user_id),
            amount=amount,
            reason=f"purchase:{req.item_id}",
        )
        db.add(txn)

    await db.commit()
    await db.refresh(record)

    return {
        "purchase_id": str(record.id),
        "item_id": req.item_id,
        "item_name": req.item_name,
        "price": req.price,
        "currency": req.currency,
        "status": "completed",
        "is_mock": True,
    }


@router.post("/recharge")
async def recharge(
    req: RechargeRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Mock fragment recharge (IAP top-up)."""
    uid = UUID(user_id)

    # Get or create fragment balance
    frag_result = await db.execute(
        select(Fragment).where(Fragment.user_id == uid)
    )
    frag = frag_result.scalar_one_or_none()
    old_balance = frag.balance if frag else 0

    if not frag:
        frag = Fragment(user_id=uid, balance=req.shards)
        db.add(frag)
    else:
        frag.balance += req.shards

    # Record transaction
    txn = FragmentTransaction(
        user_id=uid,
        amount=req.shards,
        reason=f"recharge:{req.provider}",
    )
    db.add(txn)

    # Record purchase record
    purchase_record = Purchase(
        user_id=uid,
        item_id=f"fragments_{req.shards}",
        item_name=f"{req.shards} Fragments",
        price=req.amount,
        currency=req.currency,
        is_mock=True,
    )
    db.add(purchase_record)

    await db.commit()
    await db.refresh(frag)

    return {
        "transaction_id": str(txn.id),
        "status": "success",
        "shards_added": req.shards,
        "bonus": 0,
        "new_balance": frag.balance,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/history")
async def get_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get payment history."""
    uid = UUID(user_id)
    offset = (page - 1) * page_size

    # Purchases
    stmt = (
        select(Purchase)
        .where(Purchase.user_id == uid)
        .order_by(Purchase.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    purchases = list(result.scalars().all())

    # Subscriptions
    sub_stmt = (
        select(Subscription)
        .where(Subscription.user_id == uid)
        .order_by(Subscription.started_at.desc())
    )
    sub_result = await db.execute(sub_stmt)
    subs = list(sub_result.scalars().all())

    return {
        "purchases": [
            {
                "id": str(p.id),
                "item_id": p.item_id,
                "item_name": p.item_name,
                "price": float(p.price),
                "currency": p.currency,
                "is_mock": p.is_mock,
                "created_at": p.created_at.isoformat(),
            }
            for p in purchases
        ],
        "subscriptions": [
            {
                "id": str(s.id),
                "plan_id": s.plan_id,
                "status": s.status,
                "billing_cycle": s.billing_cycle,
                "price": float(s.price),
                "started_at": s.started_at.isoformat(),
                "expires_at": s.expires_at.isoformat() if s.expires_at else None,
            }
            for s in subs
        ],
        "page": page,
        "page_size": page_size,
    }
