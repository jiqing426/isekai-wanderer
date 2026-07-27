"""User subscription and order API endpoints.

DEPRECATED: Use /api/v1/cr016/subscription/* instead.
This file is kept for backward compatibility and internally uses the new CR-016 tables.
"""

import logging
from uuid import UUID
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid

from app.core.database import get_db
from app.core.exceptions import AppException
from app.api.v1.auth import get_current_user_id
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["user-subscription-deprecated"])


class CreateOrderRequest(BaseModel):
    planId: str
    cycleType: str  # "monthly" or "yearly"


@router.get("/user/subscription")
async def get_user_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户订阅信息（需要认证）
    
    DEPRECATED: 内部已切换到 CR-016 新表，建议使用 /api/v1/cr016/subscription/status
    """
    logger.warning("Deprecated endpoint /user/subscription called. Use /cr016/subscription/status instead.")
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
    order_id = f"order_{uuid.uuid4().hex[:12]}"
    
    # Mock payment URL (in production, integrate with real payment gateway)
    pay_url = f"https://payment.example.com/pay?order_id={order_id}"
    
    return {
        "orderId": order_id,
        "payUrl": pay_url,
        "amount": amount,
        "currency": "USD"
    }
