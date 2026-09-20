"""User profile and preferences API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.user import User

router = APIRouter(prefix="/user", tags=["user"])


class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_genre: Optional[str] = None
    locale: Optional[str] = None
    onboarding_completed: Optional[bool] = None


class PreferencesUpdate(BaseModel):
    preferred_genre: Optional[str] = None
    locale: Optional[str] = None
    onboarding_completed: Optional[bool] = None


@router.get("/profile")
async def get_profile(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current user profile (requires JWT auth)."""
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise AppException(ErrorCode.USER_NOT_FOUND, 404, "User not found")
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "email_verified": user.email_verified,
        "subscription_tier": user.subscription_tier,
        "preferred_genre": user.preferred_genre,
        "locale": user.locale,
        "onboarding_completed": user.onboarding_completed,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.put("/profile")
async def update_profile(
    body: ProfileUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile fields (e.g. onboarding_completed)."""
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise AppException(ErrorCode.USER_NOT_FOUND, 404, "User not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "email_verified": user.email_verified,
        "subscription_tier": user.subscription_tier,
        "preferred_genre": user.preferred_genre,
        "locale": user.locale,
        "onboarding_completed": user.onboarding_completed,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.patch("/preferences")
async def update_preferences(
    prefs: PreferencesUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update user preferences (partial update)."""
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise AppException(ErrorCode.USER_NOT_FOUND, 404, "User not found")

    update_data = prefs.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return {
        "status": "ok",
        "preferences": {
            "preferred_genre": user.preferred_genre,
            "locale": user.locale,
            "notification_enabled": True,
            "theme": "dark",
        },
    }


@router.get("/preferences")
async def get_preferences(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get user preferences."""
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise AppException(ErrorCode.USER_NOT_FOUND, 404, "User not found")

    return {
        "preferred_genre": user.preferred_genre,
        "locale": user.locale,
        "notification_enabled": True,
        "theme": "dark",
    }


@router.put("/preferences")
async def replace_preferences(
    prefs: PreferencesUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Replace user preferences (full body replace)."""
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise AppException(ErrorCode.USER_NOT_FOUND, 404, "User not found")

    update_data = prefs.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)

    return {
        "status": "ok",
        "preferences": {
            "preferred_genre": user.preferred_genre,
            "locale": user.locale,
            "notification_enabled": True,
            "theme": "dark",
        },
    }


@router.get("/subscription")
async def get_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户订阅信息（需要认证）- CR-012 新格式
    
    DEPRECATED: 内部已切换到 CR-016 新表，建议使用 /api/v1/cr016/subscription/status
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Deprecated endpoint /user/subscription called. Use /cr016/subscription/status instead.")
    
    uid = UUID(user_id)

    # Use new CR-016 service
    from app.services.subscription_service import SubscriptionService
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


@router.get("/progress/{script_id}")
async def get_user_progress(
    script_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get user progress in a specific script."""
    try:
        script_uuid = UUID(script_id)
        user_uuid = UUID(user_id)
    except ValueError:
        raise AppException(ErrorCode.INVALID_SCRIPT_ID, 400, "Invalid script_id format")
    
    from app.models.game import GameSession
    from app.models.script import Script
    
    # Verify script exists
    script_stmt = select(Script).where(Script.id == script_uuid)
    script_result = await db.execute(script_stmt)
    script = script_result.scalar_one_or_none()
    if not script:
        raise AppException(ErrorCode.SCRIPT_NOT_FOUND, 404, "Script not found")
    
    # Get user's game sessions for this script
    session_stmt = (
        select(GameSession)
        .where(
            GameSession.user_id == user_uuid,
            GameSession.script_id == script_uuid,
        )
    )
    session_result = await db.execute(session_stmt)
    sessions = list(session_result.scalars().all())
    
    # Calculate progress
    total_sessions = len(sessions)
    completed_sessions = len([s for s in sessions if s.status == "completed"])
    
    # Get latest session
    latest_session = None
    if sessions:
        latest_session = max(sessions, key=lambda s: s.started_at)
    
    return {
        "script_id": str(script_uuid),
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "latest_session": {
            "id": str(latest_session.id),
            "status": latest_session.status,
            "started_at": latest_session.started_at.isoformat() if latest_session else None,
        } if latest_session else None,
    }
