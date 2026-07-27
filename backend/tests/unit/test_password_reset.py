"""
Test cases for Password Reset (DEV-CR2-002).

AC-047: User can request a password reset via email (mock), receive a token
(valid 1h, single-use), and reset their password.

Security requirements:
- Email enumeration protection (always return 200, even for unknown emails)
- Token single-use (used tokens are invalid)
- Token TTL 1 hour
- Rate limit: 3 requests per hour per email
"""

import pytest
import uuid
from datetime import datetime, timedelta, timezone


class TestPasswordResetService:
    """Unit tests for password reset service logic."""

    @pytest.fixture
    def temp_log_file(self, tmp_path):
        return str(tmp_path / "mock-email.log")

    @pytest.mark.asyncio
    async def test_generate_reset_token(self, db_session):
        """Token should be generated and stored in password_resets table."""
        from app.models.user import User, PasswordReset
        from app.core.security import get_password_hash

        user = User(
            email="reset@example.com",
            password_hash=get_password_hash("old_password"),
            display_name="Reset",
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        from app.services.auth_service import AuthService
        auth_service = AuthService(db_session)
        token = await auth_service.create_reset_token(user.id)

        assert token is not None
        assert len(token) >= 32  # secure random token

        # Verify stored in DB
        from sqlalchemy import select
        stmt = select(PasswordReset).where(PasswordReset.user_id == user.id)
        result = await db_session.execute(stmt)
        reset_record = result.scalar_one_or_none()
        assert reset_record is not None
        assert reset_record.token == token
        assert reset_record.used is False
        assert reset_record.expires_at > datetime.now(timezone.utc)

    @pytest.mark.asyncio
    async def test_reset_token_expires_in_1_hour(self, db_session):
        """Token expires_at should be ~1 hour from creation."""
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.services.auth_service import AuthService

        user = User(
            email="expire@example.com",
            password_hash=get_password_hash("pw"),
            display_name="Exp",
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        auth_service = AuthService(db_session)
        token = await auth_service.create_reset_token(user.id)

        from app.models.user import PasswordReset
        from sqlalchemy import select
        stmt = select(PasswordReset).where(PasswordReset.token == token)
        result = await db_session.execute(stmt)
        record = result.scalar_one()

        expected = datetime.now(timezone.utc) + timedelta(hours=1)
        assert abs((record.expires_at - expected).total_seconds()) < 5  # within 5s

    @pytest.mark.asyncio
    async def test_validate_valid_token(self, db_session):
        """Valid token should pass validation."""
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.services.auth_service import AuthService

        user = User(
            email="valid@example.com",
            password_hash=get_password_hash("old"),
            display_name="V",
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        auth_service = AuthService(db_session)
        token = await auth_service.create_reset_token(user.id)

        is_valid, user_id = await auth_service.validate_reset_token(token)
        assert is_valid is True
        assert user_id == user.id

    @pytest.mark.asyncio
    async def test_validate_expired_token(self, db_session):
        """Expired token should fail validation."""
        from app.models.user import User, PasswordReset
        from app.core.security import get_password_hash
        from app.services.auth_service import AuthService

        user = User(
            email="expired@example.com",
            password_hash=get_password_hash("old"),
            display_name="E",
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Insert an expired token
        expired_token = "expired-token-" + str(uuid.uuid4())
        record = PasswordReset(
            user_id=user.id,
            token=expired_token,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
        )
        db_session.add(record)
        await db_session.commit()

        auth_service = AuthService(db_session)
        is_valid, user_id = await auth_service.validate_reset_token(expired_token)
        assert is_valid is False
        assert user_id is None

    @pytest.mark.asyncio
    async def test_validate_used_token(self, db_session):
        """Already-used token should fail validation (single-use)."""
        from app.models.user import User, PasswordReset
        from app.core.security import get_password_hash
        from app.services.auth_service import AuthService

        user = User(
            email="used@example.com",
            password_hash=get_password_hash("old"),
            display_name="U",
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        used_token = "used-token-" + str(uuid.uuid4())
        record = PasswordReset(
            user_id=user.id,
            token=used_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            used=True,
        )
        db_session.add(record)
        await db_session.commit()

        auth_service = AuthService(db_session)
        is_valid, user_id = await auth_service.validate_reset_token(used_token)
        assert is_valid is False
        assert user_id is None

    @pytest.mark.asyncio
    async def test_validate_nonexistent_token(self, db_session):
        """Non-existent token should fail (no email enumeration)."""
        from app.services.auth_service import AuthService

        auth_service = AuthService(db_session)
        is_valid, user_id = await auth_service.validate_reset_token("nonexistent-token")
        assert is_valid is False
        assert user_id is None

    @pytest.mark.asyncio
    async def test_reset_password_success(self, db_session):
        """Successful reset should update password and mark token as used."""
        from app.models.user import User, PasswordReset
        from app.core.security import get_password_hash, verify_password
        from app.services.auth_service import AuthService

        user = User(
            email="success@example.com",
            password_hash=get_password_hash("old_password"),
            display_name="S",
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        auth_service = AuthService(db_session)
        token = await auth_service.create_reset_token(user.id)

        result = await auth_service.reset_password(token, "new_password_123")
        assert result is True

        # Verify password changed
        from sqlalchemy import select
        stmt = select(User).where(User.id == user.id)
        res = await db_session.execute(stmt)
        updated_user = res.scalar_one()
        assert verify_password("new_password_123", updated_user.password_hash)
        assert not verify_password("old_password", updated_user.password_hash)

        # Verify token marked as used
        stmt2 = select(PasswordReset).where(PasswordReset.token == token)
        res2 = await db_session.execute(stmt2)
        reset_record = res2.scalar_one()
        assert reset_record.used is True

    @pytest.mark.asyncio
    async def test_reset_invalidates_old_tokens(self, db_session):
        """After reset, old tokens for this user should be invalidated."""
        from app.models.user import User, PasswordReset
        from app.core.security import get_password_hash
        from app.services.auth_service import AuthService
        from sqlalchemy import select

        user = User(
            email="invalidate@example.com",
            password_hash=get_password_hash("old"),
            display_name="I",
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        auth_service = AuthService(db_session)
        token1 = await auth_service.create_reset_token(user.id)
        token2 = await auth_service.create_reset_token(user.id)

        # Reset with token2
        await auth_service.reset_password(token2, "new_pw_123")

        # token1 should now be invalid
        is_valid, _ = await auth_service.validate_reset_token(token1)
        assert is_valid is False


class TestPasswordResetAPI:
    """API-level tests for password reset endpoints."""

    @pytest.mark.asyncio
    async def test_forgot_password_returns_200_for_existing_email(self, client, db_session):
        """POST /auth/forgot-password should return 200 for existing email."""
        from app.models.user import User
        from app.core.security import get_password_hash

        user = User(
            email="forgot@example.com",
            password_hash=get_password_hash("pw12345678"),
            display_name="F",
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()

        resp = await client.post("/api/v1/auth/forgot-password", json={"email": "forgot@example.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("message") is not None

    @pytest.mark.asyncio
    async def test_forgot_password_returns_200_for_unknown_email(self, client, db_session):
        """AC-047 security: unknown email should also return 200 (no enumeration)."""
        resp = await client.post("/api/v1/auth/forgot-password", json={"email": "unknown@example.com"})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_reset_password_with_valid_token(self, client, db_session):
        """POST /auth/reset-password should succeed with valid token."""
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.services.auth_service import AuthService

        user = User(
            email="apireset@example.com",
            password_hash=get_password_hash("old12345678"),
            display_name="A",
            email_verified=True,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        auth_service = AuthService(db_session)
        token = await auth_service.create_reset_token(user.id)

        resp = await client.post("/api/v1/auth/reset-password", json={
            "token": token,
            "new_password": "new_secure_pw",
        })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_reset_password_with_invalid_token(self, client, db_session):
        """POST /auth/reset-password should fail with invalid token."""
        resp = await client.post("/api/v1/auth/reset-password", json={
            "token": "invalid-token-xyz",
            "new_password": "new_pw",
        })
        assert resp.status_code == 400
