"""OAuth API - Mock OAuth login for WeChat/Google/Apple."""

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
import uuid

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.core.redis import get_redis
from app.models.user import OAuthAccount, User
from app.core.security import create_access_token, create_refresh_token, get_password_hash

router = APIRouter(prefix="/auth/oauth", tags=["oauth"])

# CRIT-001: Rate limit OAuth endpoint
OAUTH_RATE_LIMIT = 10  # max 10 OAuth attempts per IP per 10 minutes
OAUTH_WINDOW = 600
OAUTH_MAX_TOTAL_USERS = 100  # safety cap: max 100 OAuth-created users (MVP)


class OAuthLoginRequest(BaseModel):
    provider: Optional[str] = None  # Optional: can also come from path
    code: str  # Mock authorization code
    redirect_uri: Optional[str] = None


async def _check_oauth_rate_limit(request: Request) -> None:
    """CRIT-001 fix: Rate limit OAuth by IP to prevent account spam."""
    redis = await get_redis()
    client_ip = request.client.host if request.client else "unknown"
    key = f"oauth_rate:{client_ip}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, OAUTH_WINDOW)
    if count > OAUTH_RATE_LIMIT:
        raise AppException(ErrorCode.OAUTH_RATE_LIMITED, 429, "Too many OAuth attempts. Try again later.")


@router.post("/{provider}")
async def oauth_login(
    provider: str,
    req: OAuthLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Mock OAuth login for WeChat/Google/Apple.
    
    Accepts both:
    - Body with provider field: {"provider": "wechat", "code": "xxx"}
    - Body without provider field: {"code": "xxx"} (provider from path)
    """
    if provider not in ("wechat", "google", "apple", "discord"):
        raise AppException(ErrorCode.OAUTH_UNSUPPORTED_PROVIDER, 400, "Unsupported provider")

    # CRIT-001: Rate limit by IP
    await _check_oauth_rate_limit(request)

    # Mock: generate fake provider user ID based on code
    provider_user_id = f"mock_{provider}_{req.code}"

    # Check if OAuth account exists
    stmt = select(OAuthAccount).where(
        OAuthAccount.provider == provider,
        OAuthAccount.provider_user_id == provider_user_id,
    )
    result = await db.execute(stmt)
    oauth_account = result.scalar_one_or_none()

    is_new = False
    if not oauth_account:
        # CRIT-001: Safety cap on total OAuth users
        total_stmt = select(func.count()).select_from(OAuthAccount)
        total_result = await db.execute(total_stmt)
        total_oauth = total_result.scalar() or 0
        if total_oauth >= OAUTH_MAX_TOTAL_USERS:
            raise AppException(ErrorCode.OAUTH_REGISTRATION_LIMIT, 429, "OAuth registration limit reached.")

        # Create new user + OAuth account
        new_user = User(
            email=f"oauth_{provider}_{req.code}@mock.local",
            password_hash=get_password_hash(f"oauth_mock_{req.code}"),
            display_name=f"{provider.title()} User",
            email_verified=True,
        )
        db.add(new_user)
        await db.flush()

        oauth_account = OAuthAccount(
            provider=provider,
            provider_user_id=provider_user_id,
            user_id=new_user.id,
        )
        db.add(oauth_account)
        await db.flush()
        is_new = True

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(oauth_account.user_id)})
    refresh_token = create_refresh_token(data={"sub": str(oauth_account.user_id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "provider": provider,
        "user_id": str(oauth_account.user_id),
        "new_user": is_new,
    }
