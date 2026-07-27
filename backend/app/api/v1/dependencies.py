"""Shared FastAPI dependencies for API v1 endpoints."""

from fastapi import Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.user import User


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the authenticated user from the JWT token.

    Args:
        user_id: User ID extracted from the Bearer token.
        db: Database session.

    Returns:
        The User ORM object.

    Raises:
        AppException 401 if user not found.
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise AppException(ErrorCode.AUTH_USER_NOT_FOUND, 401, "User not found")
    return user
