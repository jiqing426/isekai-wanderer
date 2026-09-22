"""Admin system configuration API — CRUD for system_configs table."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.redis import get_redis
from app.api.v1.auth import get_current_user_id
from app.models.user import User
from app.models.system_config import SystemConfig

router = APIRouter()


# ---- Schemas ----

class SystemConfigItem(BaseModel):
    key: str
    value: Optional[str]
    category: str = "general"
    description: Optional[str] = None
    is_secret: bool = False


class SystemConfigResponse(BaseModel):
    key: str
    value: Optional[str]  # *** for secrets
    category: str
    description: Optional[str]
    is_secret: bool
    updated_at: Optional[datetime] = None


class SystemConfigUpdate(BaseModel):
    key: str
    value: str


# ---- Admin permission check ----

async def require_admin(user_id: str, db: AsyncSession) -> User:
    """Verify user is admin, return user object."""
    from uuid import UUID
    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


# ---- Endpoints ----

@router.get("/admin/system-config", response_model=List[SystemConfigResponse])
async def get_system_configs(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get all system configurations. Secrets return *** as value."""
    await require_admin(user_id, db)

    stmt = select(SystemConfig).order_by(SystemConfig.category, SystemConfig.key)
    result = await db.execute(stmt)
    configs = result.scalars().all()

    return [
        SystemConfigResponse(
            key=c.key,
            value="***" if c.is_secret else c.value,
            category=c.category,
            description=c.description,
            is_secret=c.is_secret,
            updated_at=c.updated_at,
        )
        for c in configs
    ]


@router.put("/admin/system-config", response_model=SystemConfigResponse)
async def update_system_config(
    update: SystemConfigUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update a system configuration value. Triggers email service reload if SMTP config changed."""
    await require_admin(user_id, db)

    stmt = select(SystemConfig).where(SystemConfig.key == update.key)
    result = await db.execute(stmt)
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Config key '{update.key}' not found",
        )

    config.value = update.value
    config.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(config)

    # Reload email service if SMTP-related config changed
    if config.category == "email":
        from app.core.email import reload_email_service
        reload_email_service()

    return SystemConfigResponse(
        key=config.key,
        value="***" if config.is_secret else config.value,
        category=config.category,
        description=config.description,
        is_secret=config.is_secret,
        updated_at=config.updated_at,
    )
