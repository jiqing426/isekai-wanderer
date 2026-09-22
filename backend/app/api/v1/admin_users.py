"""Admin user management API — list, detail, update users."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.api.v1.auth import get_current_user_id
from app.models.user import User

router = APIRouter()


# ---- Schemas ----

class UserSummary(BaseModel):
    id: str
    email: str
    display_name: Optional[str] = None
    is_admin: bool
    email_verified: bool
    subscription_tier: str
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


class UserDetail(UserSummary):
    avatar_url: Optional[str] = None
    oauth_provider: Optional[str] = None
    locale: Optional[str] = None
    onboarding_completed: bool = False
    updated_at: Optional[datetime] = None


class UserListResponse(BaseModel):
    items: list[UserSummary]
    total: int
    page: int
    page_size: int


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    is_admin: Optional[bool] = None
    email_verified: Optional[bool] = None


# ---- Admin permission check (same pattern as admin_system.py) ----

async def require_admin(user_id: str, db: AsyncSession) -> User:
    """Verify user is admin, return user object."""
    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


def _to_summary(user: User) -> UserSummary:
    return UserSummary(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        is_admin=user.is_admin,
        email_verified=user.email_verified,
        subscription_tier=user.subscription_tier,
        created_at=user.created_at,
        last_login=user.last_login,
    )


# ---- Endpoints ----

@router.get("/admin/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Search by email or display_name"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """List all users with pagination and optional search by email/display_name."""
    await require_admin(user_id, db)

    base_stmt = select(User)

    if search:
        pattern = f"%{search}%"
        base_stmt = base_stmt.where(
            or_(User.email.ilike(pattern), User.display_name.ilike(pattern))
        )

    # Count total
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * page_size
    stmt = base_stmt.order_by(User.created_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(stmt)
    users = result.scalars().all()

    return UserListResponse(
        items=[_to_summary(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/admin/users/{user_id_path}", response_model=UserDetail)
async def get_user_detail(
    user_id_path: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed info for a single user."""
    await require_admin(user_id, db)

    try:
        target_uuid = UUID(user_id_path)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    stmt = select(User).where(User.id == target_uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserDetail(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        is_admin=user.is_admin,
        email_verified=user.email_verified,
        subscription_tier=user.subscription_tier,
        created_at=user.created_at,
        last_login=user.last_login,
        avatar_url=user.avatar_url,
        oauth_provider=user.oauth_provider,
        locale=user.locale,
        onboarding_completed=user.onboarding_completed,
        updated_at=user.updated_at,
    )


@router.patch("/admin/users/{user_id_path}", response_model=UserDetail)
async def update_user(
    user_id_path: str,
    update: UserUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update a user — toggle is_admin, toggle email_verified, or update display_name."""
    await require_admin(user_id, db)

    try:
        target_uuid = UUID(user_id_path)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    stmt = select(User).where(User.id == target_uuid)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if update.display_name is not None:
        user.display_name = update.display_name
    if update.is_admin is not None:
        user.is_admin = update.is_admin
    if update.email_verified is not None:
        user.email_verified = update.email_verified

    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    return UserDetail(
        id=str(user.id),
        email=user.email,
        display_name=user.display_name,
        is_admin=user.is_admin,
        email_verified=user.email_verified,
        subscription_tier=user.subscription_tier,
        created_at=user.created_at,
        last_login=user.last_login,
        avatar_url=user.avatar_url,
        oauth_provider=user.oauth_provider,
        locale=user.locale,
        onboarding_completed=user.onboarding_completed,
        updated_at=user.updated_at,
    )
