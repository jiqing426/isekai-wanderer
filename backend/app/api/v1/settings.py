"""Settings API endpoints — /api/v1/users/me/* for settings management."""

from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.user import User
from app.models.user_settings import UserSettings
from app.models.login_device import LoginDevice
from app.models.payment import Fragment, FragmentTransaction

router = APIRouter(prefix="/users/me", tags=["settings"])


# ── Request / Response Schemas ──

class PlaySettingUpdate(BaseModel):
    typing_speed: Optional[str] = Field(None, pattern="^(slow|normal|fast|instant)$")
    auto_play: Optional[bool] = None
    auto_play_delay_ms: Optional[int] = Field(None, ge=1000, le=10000)
    bgm_volume: Optional[int] = Field(None, ge=0, le=100)
    sfx_volume: Optional[int] = Field(None, ge=0, le=100)
    animation_enabled: Optional[bool] = None
    animation_quality: Optional[str] = Field(None, pattern="^(low|medium|high)$")


class NotifySettingUpdate(BaseModel):
    update_notify: Optional[bool] = None
    activity_reminder: Optional[bool] = None
    ending_unlock: Optional[bool] = None
    checkin_push: Optional[bool] = None
    affection_change: Optional[bool] = None
    new_script: Optional[bool] = None


# ── Helper ──

async def _get_or_create_settings(db: AsyncSession, user_id: str) -> UserSettings:
    """Get or create user settings."""
    stmt = select(UserSettings).where(UserSettings.user_id == UUID(user_id))
    result = await db.execute(stmt)
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = UserSettings(user_id=UUID(user_id))
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    return settings


# ── 1. GET /users/me/play-setting ──

@router.get("/play-setting")
async def get_play_setting(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get play preferences."""
    settings = await _get_or_create_settings(db, user_id)
    
    return {
        "typing_speed": settings.typing_speed,
        "auto_play": settings.auto_play,
        "auto_play_delay_ms": settings.auto_play_delay_ms,
        "bgm_volume": settings.bgm_volume,
        "sfx_volume": settings.sfx_volume,
        "animation_enabled": settings.animation_enabled,
        "animation_quality": settings.animation_quality,
    }


# ── 2. PATCH /users/me/play-setting ──

@router.patch("/play-setting")
async def update_play_setting(
    body: PlaySettingUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update play preferences."""
    settings = await _get_or_create_settings(db, user_id)
    
    if body.typing_speed is not None:
        settings.typing_speed = body.typing_speed
    if body.auto_play is not None:
        settings.auto_play = body.auto_play
    if body.auto_play_delay_ms is not None:
        settings.auto_play_delay_ms = body.auto_play_delay_ms
    if body.bgm_volume is not None:
        settings.bgm_volume = body.bgm_volume
    if body.sfx_volume is not None:
        settings.sfx_volume = body.sfx_volume
    if body.animation_enabled is not None:
        settings.animation_enabled = body.animation_enabled
    if body.animation_quality is not None:
        settings.animation_quality = body.animation_quality
    
    settings.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(settings)
    
    return {
        "typing_speed": settings.typing_speed,
        "auto_play": settings.auto_play,
        "auto_play_delay_ms": settings.auto_play_delay_ms,
        "bgm_volume": settings.bgm_volume,
        "sfx_volume": settings.sfx_volume,
        "animation_enabled": settings.animation_enabled,
        "animation_quality": settings.animation_quality,
    }


# ── 3. GET /users/me/notify-setting ──

@router.get("/notify-setting")
async def get_notify_setting(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get notification settings."""
    settings = await _get_or_create_settings(db, user_id)
    
    return {
        "update_notify": settings.update_notify,
        "activity_reminder": settings.activity_reminder,
        "ending_unlock": settings.notification_cg_unlock,
        "checkin_push": settings.checkin_push,
        "affection_change": settings.notification_affection,
        "new_script": settings.notification_new_script,
    }


# ── 4. PATCH /users/me/notify-setting ──

@router.patch("/notify-setting")
async def update_notify_setting(
    body: NotifySettingUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update notification settings."""
    settings = await _get_or_create_settings(db, user_id)
    
    if body.update_notify is not None:
        settings.update_notify = body.update_notify
    if body.activity_reminder is not None:
        settings.activity_reminder = body.activity_reminder
    if body.ending_unlock is not None:
        settings.notification_cg_unlock = body.ending_unlock
    if body.checkin_push is not None:
        settings.checkin_push = body.checkin_push
    if body.affection_change is not None:
        settings.notification_affection = body.affection_change
    if body.new_script is not None:
        settings.notification_new_script = body.new_script
    
    settings.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(settings)
    
    return {
        "update_notify": settings.update_notify,
        "activity_reminder": settings.activity_reminder,
        "ending_unlock": settings.notification_cg_unlock,
        "checkin_push": settings.checkin_push,
        "affection_change": settings.notification_affection,
        "new_script": settings.notification_new_script,
    }


# ── 5. GET /users/me/devices ──

@router.get("/devices")
async def get_devices(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get login devices list."""
    stmt = (
        select(LoginDevice)
        .where(LoginDevice.user_id == UUID(user_id))
        .order_by(LoginDevice.last_active_at.desc())
    )
    result = await db.execute(stmt)
    devices = result.scalars().all()
    
    return {
        "devices": [
            {
                "id": str(d.id),
                "device_name": d.device_name,
                "device_type": d.device_type,
                "browser": d.browser,
                "os": d.os,
                "ip_address": d.ip_address,
                "location": d.location,
                "last_active_at": d.last_active_at.isoformat() if d.last_active_at else None,
                "is_current": d.is_current,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in devices
        ],
        "total": len(devices),
    }


# ── 6. POST /users/me/devices/{deviceId}/logout ──

@router.post("/devices/{device_id}/logout")
async def logout_device(
    device_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Logout a specific device (cannot logout current device)."""
    stmt = select(LoginDevice).where(
        LoginDevice.id == UUID(device_id),
        LoginDevice.user_id == UUID(user_id),
    )
    result = await db.execute(stmt)
    device = result.scalar_one_or_none()
    
    if not device:
        raise AppException(
            error_code="DEVICE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            message="Device not found",
        )
    
    if device.is_current:
        raise AppException(
            error_code="DEVICE_IS_CURRENT",
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Cannot logout current device",
        )
    
    await db.delete(device)
    await db.commit()
    
    return {
        "status": "ok",
        "message": "Device logged out successfully",
        "device_id": device_id,
    }


# ── 7. GET /users/me/member-info ──

@router.get("/member-info")
async def get_member_info(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get member info with fragment balance and recent bills."""
    # Get user
    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise AppException(
            error_code=ErrorCode.USER_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            message="User not found",
        )
    
    # Get fragment balance
    stmt = select(Fragment).where(Fragment.user_id == UUID(user_id))
    result = await db.execute(stmt)
    fragment = result.scalar_one_or_none()
    fragment_balance = fragment.balance if fragment else 0
    
    # Get recent bills (last 5 transactions)
    stmt = (
        select(FragmentTransaction)
        .where(FragmentTransaction.user_id == UUID(user_id))
        .order_by(FragmentTransaction.created_at.desc())
        .limit(5)
    )
    result = await db.execute(stmt)
    transactions = result.scalars().all()
    
    # 交易类型中文映射
    reason_labels = {
        'daily_checkin': '每日签到',
        'streak_milestone': '连续签到奖励',
        'gift_send': '送礼支出',
        'gift_receive': '收到礼物',
        'dialogue_quota_purchase': '碎片兑换对话',
        'shop_purchase': '商城购买',
        'refund': '退款',
        'admin_adjustment': '管理员调整',
        'system_reward': '系统奖励',
        'achievement_reward': '成就奖励',
    }
    
    # Determine member status
    now = datetime.now(timezone.utc)
    member_status = "inactive"
    if user.subscription_tier == "free":
        member_status = "inactive"
    elif user.trial_started_at and user.trial_ends_at:
        if now < user.trial_ends_at:
            member_status = "trialing"
        else:
            member_status = "inactive"
    else:
        member_status = "active"
    
    # Benefits based on tier
    benefits = []
    if user.subscription_tier == "standard":
        benefits = ["free_chat_enabled", "full_memory_access", "exclusive_cg"]
    elif user.subscription_tier == "premium":
        benefits = ["free_chat_enabled", "full_memory_access", "exclusive_cg", "priority_support", "custom_avatar"]
    
    return {
        "tier": user.subscription_tier,
        "status": member_status,
        "member_since": user.trial_started_at.isoformat() if user.trial_started_at else None,
        "expires_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None,
        "auto_renew": False,  # Not tracked yet
        "fragment_balance": fragment_balance,
        "benefits": benefits,
        "recent_bills": [
            {
                "id": str(t.id),
                "type": "earn" if t.amount > 0 else "spend",
                "description": reason_labels.get(t.reason, t.reason),
                "amount": abs(t.amount),
                "currency": "CNY",
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in transactions
        ],
    }
