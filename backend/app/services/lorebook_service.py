"""Lorebook service (CR-027)."""

import json
import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, or_, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lorebook import LorebookEntry
from app.schemas.lorebook import (
    LorebookEntryCreate,
    LorebookEntryUpdate,
    LorebookEntryResponse,
    LorebookEntryListItem,
    LorebookEntryListResponse,
)

logger = logging.getLogger(__name__)


class LorebookService:
    """Service for managing world knowledge entries."""

    async def create(
        self,
        db: AsyncSession,
        data: LorebookEntryCreate,
        created_by: Optional[UUID] = None,
    ) -> LorebookEntryResponse:
        """Create a new lorebook entry."""
        entry = LorebookEntry(
            title=data.title,
            content=data.content,
            tags=data.tags,
            priority=data.priority,
            created_by=created_by,
        )
        db.add(entry)
        await db.flush()
        await db.refresh(entry)
        return LorebookEntryResponse.model_validate(entry)

    async def get(
        self, db: AsyncSession, entry_id: UUID
    ) -> Optional[LorebookEntryResponse]:
        """Get a lorebook entry by ID."""
        stmt = select(LorebookEntry).where(
            LorebookEntry.id == entry_id,
            LorebookEntry.status == "active",
        )
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        if not entry:
            return None
        return LorebookEntryResponse.model_validate(entry)

    async def update(
        self,
        db: AsyncSession,
        entry_id: UUID,
        data: LorebookEntryUpdate,
    ) -> Optional[LorebookEntryResponse]:
        """Update a lorebook entry."""
        stmt = select(LorebookEntry).where(
            LorebookEntry.id == entry_id,
            LorebookEntry.status == "active",
        )
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        if not entry:
            return None

        if data.title is not None:
            entry.title = data.title
        if data.content is not None:
            entry.content = data.content
        if data.tags is not None:
            entry.tags = data.tags
        if data.priority is not None:
            entry.priority = data.priority

        await db.flush()
        await db.refresh(entry)
        return LorebookEntryResponse.model_validate(entry)

    async def soft_delete(
        self, db: AsyncSession, entry_id: UUID
    ) -> bool:
        """Soft delete a lorebook entry (set status to 'deleted')."""
        stmt = select(LorebookEntry).where(
            LorebookEntry.id == entry_id,
            LorebookEntry.status == "active",
        )
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        if not entry:
            return False

        entry.status = "deleted"
        await db.flush()
        return True

    async def list(
        self,
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        tag: Optional[str] = None,
    ) -> LorebookEntryListResponse:
        """List lorebook entries with pagination and optional tag filter."""
        # Base query
        base_stmt = select(LorebookEntry).where(LorebookEntry.status == "active")

        # Apply tag filter if provided
        if tag:
            # Detect database dialect for appropriate JSON query
            dialect_name = db.bind.dialect.name if hasattr(db.bind, 'dialect') else 'sqlite'
            
            if dialect_name == 'postgresql':
                # PostgreSQL: use JSONB contains operator
                base_stmt = base_stmt.where(
                    LorebookEntry.tags.contains([tag])
                )
            else:
                # SQLite/other: use LIKE with JSON-serialized tag
                # json.dumps will escape Unicode characters to match SQLite storage
                tag_json = json.dumps(tag, ensure_ascii=True)
                base_stmt = base_stmt.where(
                    LorebookEntry.tags.cast(String).like(f'%{tag_json}%')
                )

        # Count total
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * page_size
        items_stmt = (
            base_stmt.order_by(LorebookEntry.priority.desc(), LorebookEntry.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        items_result = await db.execute(items_stmt)
        entries = items_result.scalars().all()

        items = [LorebookEntryListItem.model_validate(e) for e in entries]
        return LorebookEntryListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def match_by_tags(
        self,
        db: AsyncSession,
        tags: List[str],
        limit: int = 10,
    ) -> List[LorebookEntryResponse]:
        """Match lorebook entries by tag intersection, ordered by priority DESC."""
        if not tags:
            return []

        # Detect database dialect for appropriate JSON query
        dialect_name = db.bind.dialect.name if hasattr(db.bind, 'dialect') else 'sqlite'
        
        # Build conditions based on dialect
        conditions = []
        if dialect_name == 'postgresql':
            # PostgreSQL: use JSONB overlap operator
            conditions.append(LorebookEntry.tags.overlap(tags))
        else:
            # SQLite/other: use LIKE with JSON-serialized tags
            for tag in tags:
                tag_json = json.dumps(tag, ensure_ascii=True)
                conditions.append(LorebookEntry.tags.cast(String).like(f'%{tag_json}%'))

        stmt = (
            select(LorebookEntry)
            .where(
                LorebookEntry.status == "active",
                or_(*conditions),
            )
            .order_by(LorebookEntry.priority.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        entries = result.scalars().all()
        return [LorebookEntryResponse.model_validate(e) for e in entries]
