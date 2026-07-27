"""Paywall API endpoints.

DEPRECATED: Use /api/v1/cr016/paywall/* instead.
This file is kept for backward compatibility and internally uses the new CR-016 tables.
"""

import logging
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.api.v1.auth import get_current_user_id
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User
from app.services.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/paywall", tags=["paywall-deprecated"])


# 触发场景配置
SCENE_CONFIG = {
    "T1": {
        "type": "fullscreen",
        "message": "您的对话额度已用完，升级套餐获得无限额度",
        "condition": "quota_exhausted"
    },
    "T2": {
        "type": "fullscreen",
        "message": "此功能需要高级套餐",
        "condition": "premium_feature"
    },
    "T3": {
        "type": "banner",
        "message": "对话次数达到阈值，考虑升级？",
        "condition": "quota_threshold"
    },
    "T4": {
        "type": "fullscreen",
        "message": "解锁高级角色需要标准套餐",
        "condition": "premium_character"
    },
    "T5": {
        "type": "toast",
        "message": "CG画廊需要标准或高级套餐",
        "condition": "premium_gallery"
    },
    "T6": {
        "type": "banner",
        "message": "好久不见！回来看看新内容？",
        "condition": "inactive_user"
    },
    "T7": {
        "type": "toast",
        "message": "恭喜完成成就！解锁更多特权？",
        "condition": "achievement_complete"
    },
    "T8": {
        "type": "toast",
        "message": "碎片不足，购买更多碎片？",
        "condition": "insufficient_fragments"
    }
}


@router.get("/check")
async def check_paywall(
    scene: str = Query(..., description="触发场景（T1-T8）"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """检查是否应该显示Paywall
    
    DEPRECATED: 内部已切换到 CR-016 新服务，建议使用 /api/v1/cr016/paywall/check-trigger
    """
    logger.warning("Deprecated endpoint /paywall/check called. Use /cr016/paywall/check-trigger instead.")
    
    # 验证场景
    if scene not in SCENE_CONFIG:
        return {
            "should_show": False,
            "type": None,
            "message": None,
            "scene": scene,
            "cooldown_remaining": 0,
            "_deprecated": True,
            "_new_endpoint": "/api/v1/cr016/paywall/check-trigger"
        }
    
    config = SCENE_CONFIG[scene]
    uid = UUID(user_id)
    
    # Use new CR-016 services
    subscription_service = SubscriptionService(db)
    tier = await subscription_service.get_user_tier(uid)
    is_subscribed = await subscription_service.is_exempt_from_quota(uid)
    
    # 根据场景判断是否显示
    should_show = False
    cooldown_remaining = 0
    
    if scene == "T1":  # 额度用完
        # For free users, check quota via QuotaService
        if tier == "free":
            from app.services.quota_service import QuotaService
            quota_service = QuotaService(db)
            quota_status = await quota_service.get_user_quota_status(uid)
            if quota_status["remaining"] == 0:
                should_show = True
    
    elif scene == "T2":  # 高级功能
        if tier in ["free", "basic"]:
            should_show = True
    
    elif scene == "T3":  # 对话阈值
        if tier == "free":
            from app.services.quota_service import QuotaService
            quota_service = QuotaService(db)
            quota_status = await quota_service.get_user_quota_status(uid)
            # Show when 80% of quota used
            if quota_status["base_quota"] > 0:
                usage_ratio = quota_status["consumed"] / quota_status["base_quota"]
                if usage_ratio >= 0.8:
                    should_show = True
    
    elif scene == "T4":  # 高级角色
        if tier in ["free", "basic"]:
            should_show = True
    
    elif scene == "T5":  # CG画廊
        if tier in ["free", "basic"]:
            should_show = True
    
    elif scene == "T6":  # 不活跃用户
        if tier == "free":
            should_show = True
    
    elif scene == "T7":  # 成就完成
        if tier == "free":
            should_show = True
    
    elif scene == "T8":  # 碎片不足
        should_show = True
    
    return {
        "should_show": should_show,
        "type": config["type"] if should_show else None,
        "message": config["message"] if should_show else None,
        "scene": scene,
        "cooldown_remaining": cooldown_remaining,
        "_deprecated": True,
        "_new_endpoint": "/api/v1/cr016/paywall/check-trigger"
    }
