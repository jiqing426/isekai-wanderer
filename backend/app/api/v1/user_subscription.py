"""User subscription and order API endpoints.

DEPRECATED: Use /api/v1/cr016/subscription/* instead.
This file is kept for backward compatibility and internally uses the new CR-016 tables.
"""

import logging
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.api.v1.auth import get_current_user_id
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["user-subscription-deprecated"])


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
