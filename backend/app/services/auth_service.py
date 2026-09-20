"""
AuthService — password reset logic for CR-002 AC-047.

Security requirements:
- Token: cryptographically random, 32+ chars
- Token TTL: 1 hour
- Token single-use: mark used after successful reset
- Rate limit: 3 requests per hour per email (via Redis)
- No email enumeration: always return success for forgot-password
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.core.email import get_email_service
from app.models.user import User, PasswordReset


# Config
RESET_TOKEN_TTL_HOURS = 1
RESET_RATE_LIMIT_PER_HOUR = 3


class AuthService:
    """Handles password reset token lifecycle."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_reset_token(self, user_id) -> str:
        """
        Generate a secure random reset token and persist it.

        Args:
            user_id: UUID of the user requesting reset.

        Returns:
            The generated token string.
        """
        token = secrets.token_urlsafe(48)  # 64-char URL-safe token
        expires_at = datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_TTL_HOURS)

        record = PasswordReset(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            used=False,
        )
        self.db.add(record)
        await self.db.flush()
        return token

    async def validate_reset_token(self, token: str) -> tuple[bool, Optional[object]]:
        """
        Validate a reset token: exists, not expired, not used.

        Returns:
            (is_valid, user_id) — user_id is None if invalid.
        """
        stmt = select(PasswordReset).where(PasswordReset.token == token)
        result = await self.db.execute(stmt)
        record = result.scalar_one_or_none()

        if not record:
            return False, None

        if record.used:
            return False, None

        # Handle both aware and naive datetimes
        expires = record.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        if expires < datetime.now(timezone.utc):
            return False, None

        return True, record.user_id

    async def reset_password(self, token: str, new_password: str) -> bool:
        """
        Reset password using a valid token.

        - Validates the token
        - Updates the user's password hash
        - Marks the token as used
        - Invalidates all other tokens for the same user

        Returns:
            True on success, False on failure.
        """
        is_valid, user_id = await self.validate_reset_token(token)
        if not is_valid:
            return False

        # Update password
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return False

        user.password_hash = get_password_hash(new_password)

        # Mark this token as used
        mark_stmt = update(PasswordReset).where(PasswordReset.token == token).values(used=True)
        await self.db.execute(mark_stmt)

        # Invalidate all other tokens for this user
        invalidate_stmt = (
            update(PasswordReset)
            .where(PasswordReset.user_id == user_id, PasswordReset.token != token)
            .values(used=True)
        )
        await self.db.execute(invalidate_stmt)

        await self.db.flush()
        return True

    async def request_password_reset(self, email: str) -> bool:
        """
        High-level: look up user by email, create token, send mock email.

        Always returns True (no email enumeration).
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            # Don't reveal whether the email exists
            return True

        # Check rate limit via Redis
        from app.core.redis import check_rate_limit
        allowed, _ = await check_rate_limit(f"password_reset:{email}", RESET_RATE_LIMIT_PER_HOUR, 3600)
        if not allowed:
            # Silently drop (no enumeration)
            return True

        token = await self.create_reset_token(user.id)

        # Build reset URL using app_url from config
        from app.core.config import settings
        reset_url = f"{settings.app_url}/reset-password?token={token}"

        # Send via mock email
        email_service = get_email_service()
        await email_service.send_password_reset_email(email, token, reset_url)

        await self.db.flush()
        return True
