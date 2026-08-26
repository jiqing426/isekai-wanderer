"""Scene Config API routes (CR-027 T-005).

Admin-only endpoints for managing scene configurations bound to story nodes.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.auth import get_current_user_id
from app.models.user import User
from app.schemas.scene_config import SceneConfigUpsert, SceneConfigResponse
from app.services.scene_config_service import SceneConfigService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scene-configs", tags=["scene-configs"])

scene_config_service = SceneConfigService()


async def require_admin(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Dependency: only admin users can access scene config endpoints."""
    from sqlalchemy import select

    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user_id


@router.get("", response_model=list[SceneConfigResponse])
async def list_scene_configs(
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """List all scene configs."""
    return await scene_config_service.list(db)


@router.get("/node/{node_id}", response_model=SceneConfigResponse)
async def get_scene_config(
    node_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Get scene config by node ID."""
    config = await scene_config_service.get_by_node_id(db, node_id)
    if not config:
        raise HTTPException(status_code=404, detail="Scene config not found")
    return config


@router.put("/node/{node_id}", response_model=SceneConfigResponse)
async def upsert_scene_config(
    node_id: UUID,
    data: SceneConfigUpsert,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Create or update a scene config for a node."""
    try:
        return await scene_config_service.upsert(db, node_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/node/{node_id}")
async def delete_scene_config(
    node_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: str = Depends(require_admin),
):
    """Delete a scene config by node ID."""
    deleted = await scene_config_service.delete(db, node_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Scene config not found")
    return {"message": "Scene config deleted"}
