"""Subscription API endpoints.

DEPRECATED: Use /api/v1/cr016/subscription/* instead.
This file is kept for backward compatibility and internally uses the new CR-016 tables.
"""

import logging
from uuid import UUID
from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id, get_current_user_id_optional
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscription", tags=["subscription-deprecated"])


@router.get("/plans")
async def list_plans():
    """
    获取所有订阅套餐配置（无需认证）
    返回4个套餐：free/basic/standard/premium
    """
    plans = [
        {
            "planId": "free",
            "name": "免费版",
            "priceMonthly": 0,
            "priceYearly": 0,
            "featureList": [
                "基础对话功能",
                "每日50次对话额度"
            ],
            "fragmentDiscountRate": 0,
            "recommend": False
        },
        {
            "planId": "basic",
            "name": "基础版",
            "priceMonthly": 1.99,
            "priceYearly": 19.99,
            "featureList": [
                "基础对话功能",
                "每日200次对话额度",
                "基础角色解锁"
            ],
            "fragmentDiscountRate": 0.1,
            "recommend": False
        },
        {
            "planId": "standard",
            "name": "标准版",
            "priceMonthly": 4.99,
            "priceYearly": 49.99,
            "featureList": [
                "高级对话功能",
                "每日500次对话额度",
                "全部角色解锁",
                "CG画廊"
            ],
            "fragmentDiscountRate": 0.2,
            "recommend": True
        },
        {
            "planId": "premium",
            "name": "高级版",
            "priceMonthly": 9.99,
            "priceYearly": 99.99,
            "featureList": [
                "全部功能",
                "无限对话额度",
                "全部角色解锁",
                "CG画廊",
                "专属客服"
            ],
            "fragmentDiscountRate": 0.3,
            "recommend": False
        }
    ]
    return {"plans": plans}


from pydantic import BaseModel
from typing import Optional


class CreateOrderRequest(BaseModel):
    planId: str
    cycleType: str  # "monthly" or "yearly"


@router.post("/order/create")
async def create_order(
    request: CreateOrderRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """创建订阅订单（需要认证）"""
    uid = UUID(user_id)
    
    # Validate planId
    valid_plans = ["basic", "standard", "premium"]
    if request.planId not in valid_plans:
        raise AppException("PLAN_NOT_FOUND", 404, f"套餐不存在: {request.planId}")
    
    # Validate cycleType
    if request.cycleType not in ["monthly", "yearly"]:
        raise AppException("INVALID_CYCLE_TYPE", 400, f"无效的订阅周期: {request.cycleType}")
    
    # Price map
    price_map = {
        "basic": {"monthly": 1.99, "yearly": 19.99},
        "standard": {"monthly": 4.99, "yearly": 49.99},
        "premium": {"monthly": 9.99, "yearly": 99.99}
    }
    
    amount = price_map[request.planId][request.cycleType]
    
    # Generate mock order ID
    import uuid
    order_id = f"order_{uuid.uuid4().hex[:12]}"
    
    # Mock payment URL (in production, integrate with real payment gateway)
    pay_url = f"https://payment.example.com/pay?order_id={order_id}"
    
    return {
        "orderId": order_id,
        "payUrl": pay_url,
        "amount": amount,
        "currency": "USD"
    }


@router.get("/status")
async def get_subscription_status(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户订阅信息（需要认证）
    
    DEPRECATED: 内部已切换到 CR-016 新表，建议使用 /api/v1/cr016/subscription/status
    """
    logger.warning("Deprecated endpoint /subscription/status called. Use /cr016/subscription/status instead.")
    uid = UUID(user_id)
    
    # Use new CR-016 service
    subscription_service = SubscriptionService(db)
    tier = await subscription_service.get_user_tier(uid)
    permissions = await subscription_service.get_tier_permissions(tier)
    is_exempt = await subscription_service.is_exempt_from_quota(uid)
    
    # Get subscription record for expires_at
    sub = await subscription_service.get_user_subscription(uid)
    expires_at = sub.expires_at.isoformat() if sub and sub.expires_at else None

    # Map new permissions to old API format for backward compatibility
    old_permissions = {
        "canAccessAllCharacters": permissions.script_access in ["all_normal", "all_including_exclusive"],
        "canAccessCGGallery": permissions.ugc_access or tier in ["standard", "premium"],
        "canUseAdvancedFeatures": tier in ["standard", "premium"],
        "canUseFreeChat": True,
        "canUseMemorySystem": tier in ["standard", "premium"]
    }

    return {
        "currentPlanId": tier,
        "remainStamina": -1 if is_exempt else 50,  # -1 = unlimited
        "freeCycleStage": None if is_exempt else "honeymoon",
        "permissions": old_permissions,
        "expiresAt": expires_at,
        "autoRenew": False,
        "_deprecated": True,
        "_new_endpoint": "/api/v1/cr016/subscription/status"
    }


@router.get("/users/me/subscription")
async def get_user_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户订阅信息和额度"""
    uid = UUID(user_id)

    # Get user for current tier
    user_result = await db.execute(select(User).where(User.id == uid))
    user = user_result.scalar_one()

    # Get active subscription
    stmt = (
        select(Subscription)
        .where(
            Subscription.user_id == uid,
            Subscription.status == "active",
        )
        .order_by(Subscription.started_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()

    tier = user.subscription_tier or "free"
    
    # Calculate quota based on tier
    quota_map = {
        "free": 50,
        "basic": 200,
        "standard": 500,
        "premium": -1  # unlimited
    }
    
    if sub:
        quota_total = sub.quota_total or quota_map.get(sub.plan_id, 50)
        quota_used = sub.quota_used or 0
        quota_period = sub.quota_period or "honeymoon"
        expires_at = sub.expires_at.isoformat() if sub.expires_at else None
        auto_renew = sub.auto_renew
    else:
        quota_total = quota_map.get(tier, 50)
        quota_used = 0
        quota_period = "honeymoon" if tier == "free" else None
        expires_at = None
        auto_renew = False
    
    return {
        "tier": tier,
        "quota": {
            "total": quota_total,
            "used": quota_used,
            "remaining": quota_total - quota_used if quota_total > 0 else -1,
            "period": quota_period
        },
        "expires_at": expires_at,
        "auto_renew": auto_renew
    }


@router.post("/subscribe")
async def subscribe(
    tier: str,
    payment_method: str = "stripe",
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """订阅或升级套餐"""
    uid = UUID(user_id)
    
    # Validate tier
    valid_tiers = ["basic", "standard", "premium"]
    if tier not in valid_tiers:
        raise AppException("INVALID_TIER", 400, f"无效的套餐等级: {tier}")
    
    # Check if user already has active subscription
    stmt = (
        select(Subscription)
        .where(
            Subscription.user_id == uid,
            Subscription.status == "active",
        )
    )
    result = await db.execute(stmt)
    existing_sub = result.scalar_one_or_none()
    
    if existing_sub and existing_sub.plan_id == tier:
        raise AppException("SUBSCRIPTION_ALREADY_ACTIVE", 409, "已有相同等级的活跃订阅")
    
    # Mock payment processing (in production, integrate with real payment gateway)
    # Calculate quota
    quota_map = {
        "basic": 200,
        "standard": 500,
        "premium": -1
    }
    
    # Price map
    price_map = {
        "basic": 1.99,
        "standard": 4.99,
        "premium": 9.99
    }
    
    # Create or update subscription
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    
    if existing_sub:
        # Upgrade existing subscription
        existing_sub.plan_id = tier
        existing_sub.price = price_map[tier]
        existing_sub.quota_total = quota_map[tier]
        existing_sub.quota_used = 0
        existing_sub.expires_at = expires_at
        existing_sub.auto_renew = True
        sub_id = existing_sub.id
    else:
        # Create new subscription
        new_sub = Subscription(
            user_id=uid,
            plan_id=tier,
            status="active",
            billing_cycle="monthly",
            currency="USD",
            price=price_map[tier],
            is_mock=True,
            quota_total=quota_map[tier],
            quota_used=0,
            quota_period="honeymoon",
            expires_at=expires_at,
            auto_renew=True
        )
        db.add(new_sub)
        await db.flush()
        sub_id = new_sub.id
    
    # Update user tier
    user_result = await db.execute(select(User).where(User.id == uid))
    user = user_result.scalar_one()
    user.subscription_tier = tier
    
    await db.commit()
    
    return {
        "status": "success",
        "subscription_id": str(sub_id),
        "tier": tier,
        "expires_at": expires_at.isoformat(),
        "quota_updated": True
    }


@router.post("/cancel")
async def cancel_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    AC-041: Cancel active subscription.
    User keeps premium until expires_at, then downgrades to free.
    """
    uid = UUID(user_id)
    stmt = (
        select(Subscription)
        .where(
            Subscription.user_id == uid,
            Subscription.status == "active",
        )
    )
    result = await db.execute(stmt)
    sub = result.scalar_one_or_none()

    if not sub:
        raise AppException(ErrorCode.SUBSCRIPTION_ACTIVE, 400, "No active subscription to cancel")

    sub.status = "cancelled"
    sub.cancelled_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "subscription_id": str(sub.id),
        "status": "cancelled",
        "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
        "message": "Subscription cancelled. Premium access continues until expiry.",
    }


async def run_subscription_expiry_check(db: AsyncSession) -> int:
    """
    AC-041 cron: Check for expired subscriptions and downgrade users to free tier.

    Call this daily (e.g., from a cron job or scheduler).

    Returns:
        Number of users downgraded.
    """
    now = datetime.now(timezone.utc)

    # Find expired active/cancelled subscriptions
    stmt = (
        select(Subscription)
        .where(
            Subscription.status.in_(["active", "cancelled"]),
            Subscription.expires_at.isnot(None),
            Subscription.expires_at <= now,
        )
    )
    result = await db.execute(stmt)
    expired_subs = list(result.scalars().all())

    downgraded = 0
    for sub in expired_subs:
        sub.status = "expired"

        # Downgrade user to free tier
        user_result = await db.execute(
            select(User).where(User.id == sub.user_id)
        )
        user = user_result.scalar_one_or_none()
        if user and user.subscription_tier != "free":
            user.subscription_tier = "free"
            downgraded += 1

    await db.commit()
    return downgraded


async def run_monthly_fragment_grant(db: AsyncSession) -> int:
    """
    Cron job: Grant monthly fragments to active subscribers.
    
    Call this daily to check and grant fragments for subscriptions
    that are due for their monthly grant.
    
    Returns:
        Number of users granted fragments.
    """
    from app.services.subscription_service import SubscriptionService
    
    service = SubscriptionService(db)
    granted_count = await service.process_monthly_grants()
    
    return granted_count
