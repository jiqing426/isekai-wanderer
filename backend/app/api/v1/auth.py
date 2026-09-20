"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.redis import get_redis
from app.core.exceptions import AppException, ErrorCode
from app.models.user import User

router = APIRouter()

# Bearer token security
security = HTTPBearer(auto_error=False)

# Login lockout config
LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 900  # 15 minutes


# ---- Request/Response Schemas ----

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    code: str  # 邮箱验证码
    display_name: Optional[str] = None

class SendCodeRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds


# ---- Auth Dependency ----

MOCK_USER_ID = "bd7f90f9-f543-4fb0-98eb-b9c2a42410a2"

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Extract and validate JWT token, return user_id."""
    import logging
    logger = logging.getLogger(__name__)
    
    if not credentials or not credentials.credentials:
        logger.warning("get_current_user_id: Missing authorization credentials")
        raise AppException(
            error_code=ErrorCode.AUTH_TOKEN_EXPIRED,
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Missing authorization token. Please include 'Authorization: Bearer <token>' header.",
        )
    token = credentials.credentials
    payload = decode_token(token, expected_type="access")
    
    if not payload:
        logger.warning(f"get_current_user_id: Invalid or expired token (first 20 chars: {token[:20]}...)")
        raise AppException(
            error_code=ErrorCode.AUTH_TOKEN_EXPIRED,
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid or expired token. Please login again.",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        logger.warning(f"get_current_user_id: Token payload missing 'sub' field. Payload: {payload}")
        raise AppException(
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid token payload",
        )
    
    logger.debug(f"get_current_user_id: Successfully authenticated user {user_id}")
    return user_id


async def get_current_user_id_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[str]:
    """Extract and validate JWT token, return user_id or None if not authenticated."""
    if not credentials or not credentials.credentials:
        return None
    token = credentials.credentials
    payload = decode_token(token, expected_type="access")
    
    if not payload:
        return None
    
    user_id = payload.get("sub")
    return user_id


# ---- Login Lockout Helpers (SEC-002) ----

async def _check_login_lockout(email: str) -> None:
    """Raise 429 if account is locked out due to too many failed attempts."""
    redis = await get_redis()
    key = f"login_lockout:{email}"
    attempts = await redis.get(key)
    if attempts and int(attempts) >= LOGIN_MAX_ATTEMPTS:
        ttl = await redis.ttl(key)
        raise AppException(
            error_code="AUTH_ACCOUNT_LOCKED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message=f"Account locked. Try again in {ttl}s.",
        )


async def _record_failed_login(email: str) -> None:
    """Increment failed login counter in Redis."""
    redis = await get_redis()
    key = f"login_lockout:{email}"
    attempts = await redis.incr(key)
    if attempts == 1:
        await redis.expire(key, LOGIN_LOCKOUT_SECONDS)


async def _clear_failed_login(email: str) -> None:
    """Clear failed login counter on successful login."""
    redis = await get_redis()
    key = f"login_lockout:{email}"
    await redis.delete(key)


# ---- Endpoints ----

# ---- Email Verification Code ----

VERIFY_CODE_TTL = 300  # 5 minutes
VERIFY_CODE_RESEND_COOLDOWN = 60  # 60s between sends
VERIFY_CODE_HOURLY_LIMIT = 5  # max 5 per hour

@router.post("/auth/send-code")
async def send_verification_code(
    request: SendCodeRequest,
    db: AsyncSession = Depends(get_db),
):
    """发送注册验证码到邮箱。防刷：60秒冷却 + 每小时5次上限。"""
    email = request.email

    # Check if email already registered
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise AppException(
            error_code="AUTH_EMAIL_EXISTS",
            status_code=status.HTTP_409_CONFLICT,
            message="该邮箱已注册",
        )

    redis = await get_redis()

    # Cooldown check (60s between sends)
    cooldown_key = f"email:verify:lock:{email}"
    if await redis.get(cooldown_key):
        raise AppException(
            error_code="RATE_LIMIT",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message="请稍后再试（60秒冷却中）",
        )

    # Hourly limit check
    count_key = f"email:verify:count:{email}"
    count = await redis.get(count_key)
    if count and int(count) >= VERIFY_CODE_HOURLY_LIMIT:
        raise AppException(
            error_code="RATE_LIMIT",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            message="请求过于频繁，请稍后再试",
        )

    # Generate 6-digit code
    import random
    code = str(random.randint(100000, 999999))

    # Store code in Redis (5 min TTL)
    code_key = f"email:verify:code:{email}"
    await redis.setex(code_key, VERIFY_CODE_TTL, code)

    # Set cooldown (60s)
    await redis.setex(cooldown_key, VERIFY_CODE_RESEND_COOLDOWN, "1")

    # Increment hourly counter
    hourly_count = await redis.incr(count_key)
    if hourly_count == 1:
        await redis.expire(count_key, 3600)

    # Send email
    from app.core.email import get_email_service
    email_service = get_email_service()
    await email_service.send_verification_code(email, code)

    return {"message": "验证码已发送"}


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user. Requires email verification code."""
    # Verify code from Redis
    redis = await get_redis()
    code_key = f"email:verify:code:{request.email}"
    stored_code = await redis.get(code_key)

    if not stored_code or stored_code != request.code:
        raise AppException(
            error_code="AUTH_INVALID_CODE",
            status_code=status.HTTP_400_BAD_REQUEST,
            message="验证码无效或已过期",
        )

    # Check if email exists
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise AppException(
            error_code="AUTH_EMAIL_EXISTS",
            status_code=status.HTTP_409_CONFLICT,
            message="Email already registered",
        )

    # Create user
    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        display_name=request.display_name or request.email.split("@")[0],
        email_verified=False,  # 需要邮箱验证
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Clear verification code from Redis
    await redis.delete(code_key)

    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "email_verified": False,
    }


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    request_obj: Request,
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password. Locks account after 5 failed attempts."""
    # CRIT-002 fix: check lockout before attempting login
    await _check_login_lockout(request.email)

    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(request.password, user.password_hash):
        # Record failure
        await _record_failed_login(request.email)
        raise AppException(
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid email or password",
        )
    
    if not user.email_verified:
        raise AppException(
            error_code=ErrorCode.AUTH_EMAIL_NOT_VERIFIED,
            status_code=status.HTTP_403_FORBIDDEN,
            message="Email not verified",
        )
    
    # Clear lockout on success
    await _clear_failed_login(request.email)

    # Track last_login
    from datetime import datetime, timezone
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 86400,
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
    }


@router.post("/auth/refresh")
async def refresh_token(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """HIGH-001 fix: Refresh access token using refresh token."""
    payload = decode_token(request.refresh_token, expected_type="refresh")
    if not payload:
        raise AppException(
            error_code=ErrorCode.AUTH_TOKEN_EXPIRED,
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid or expired refresh token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise AppException(
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Invalid refresh token payload",
        )

    # Verify user still exists
    from uuid import UUID
    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise AppException(
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="User not found",
        )

    # Issue new tokens
    new_access = create_access_token({"sub": str(user.id)})
    new_refresh = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "expires_in": 86400,
    }


# ---- Password Reset (CR-002 AC-047) ----

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/auth/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    AC-047: Request a password reset email.
    Always returns 200 (no email enumeration).
    """
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    await auth_service.request_password_reset(request.email)
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/auth/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    AC-047: Reset password using a valid token.
    """
    from app.services.auth_service import AuthService
    auth_service = AuthService(db)
    success = await auth_service.reset_password(request.token, request.new_password)
    if not success:
        raise AppException(
            error_code="AUTH_INVALID_TOKEN",
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid or expired reset token",
        )
    await db.commit()
    return {"message": "Password reset successful"}
