"""Scene config service (CR-027)."""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scene_config import SceneConfig
from app.models.script import Node, Route
from app.schemas.scene_config import SceneConfigUpsert, SceneConfigResponse

logger = logging.getLogger(__name__)


class SceneConfigService:
    """Service for managing scene configurations."""

    async def upsert(
        self,
        db: AsyncSession,
        node_id: UUID,
        data: SceneConfigUpsert,
    ) -> SceneConfigResponse:
        """Create or update a scene config for a node."""
        # Check if node exists
        node_stmt = select(Node).where(Node.id == node_id)
        node_result = await db.execute(node_stmt)
        if not node_result.scalar_one_or_none():
            raise ValueError(f"Node {node_id} not found")

        # Check if config already exists
        stmt = select(SceneConfig).where(SceneConfig.node_id == node_id)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()

        if config:
            # Update existing
            config.scene_name = data.scene_name
            config.tags = data.tags
            config.description = data.description
        else:
            # Create new
            config = SceneConfig(
                node_id=node_id,
                scene_name=data.scene_name,
                tags=data.tags,
                description=data.description,
            )
            db.add(config)

        await db.flush()
        await db.refresh(config)
        return SceneConfigResponse.model_validate(config)

    async def get_by_node_id(
        self, db: AsyncSession, node_id: UUID
    ) -> Optional[SceneConfigResponse]:
        """Get scene config by node ID."""
        stmt = select(SceneConfig).where(SceneConfig.node_id == node_id)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        if not config:
            return None
        return SceneConfigResponse.model_validate(config)

    async def delete(
        self, db: AsyncSession, node_id: UUID
    ) -> bool:
        """Delete a scene config by node ID."""
        stmt = select(SceneConfig).where(SceneConfig.node_id == node_id)
        result = await db.execute(stmt)
        config = result.scalar_one_or_none()
        if not config:
            return False

        await db.delete(config)
        await db.flush()
        return True

    async def list(
        self,
        db: AsyncSession,
        script_id: Optional[UUID] = None,
        route_id: Optional[UUID] = None,
    ) -> List[SceneConfigResponse]:
        """List scene configs with optional script/route filters."""
        # Start with base query
        stmt = select(SceneConfig)

        # Apply filters if provided
        if script_id or route_id:
            # Join with nodes and routes to filter
            stmt = stmt.join(Node, SceneConfig.node_id == Node.id)
            if route_id:
                stmt = stmt.where(Node.route_id == route_id)
            if script_id:
                stmt = stmt.join(Route, Node.route_id == Route.id)
                stmt = stmt.where(Route.script_id == script_id)

        stmt = stmt.order_by(SceneConfig.created_at.desc())
        result = await db.execute(stmt)
        configs = result.scalars().all()
        return [SceneConfigResponse.model_validate(c) for c in configs]
