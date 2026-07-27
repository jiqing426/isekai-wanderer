"""Unlock service for CR-017 unlock animation system."""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.unlock_record import UnlockRecord, UnlockType
from app.schemas.unlock_record import UnlockRecordCreate, UnlockBatchItem

logger = logging.getLogger(__name__)


class UnlockService:
    """Service for managing unlock records."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def record_unlock(
        self,
        user_id: uuid.UUID,
        unlock_type: str,
        content_id: str,
        title: str,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        rarity: Optional[str] = None,
        reward_data: Optional[Dict[str, Any]] = None,
    ) -> UnlockRecord:
        """Record a new unlock event.
        
        Args:
            user_id: User who unlocked the content
            unlock_type: Type of unlock (cg/achievement/hidden_story/voice/exclusive_script/reward_float/multi_reward)
            content_id: ID of the unlocked content
            title: Title of the unlock
            description: Optional description
            image_url: Optional thumbnail URL
            rarity: Optional rarity level (R/SR/SSR)
            reward_data: Optional additional reward data
            
        Returns:
            Created UnlockRecord
        """
        record = UnlockRecord(
            user_id=user_id,
            unlock_type=unlock_type,
            content_id=content_id,
            title=title,
            description=description,
            image_url=image_url,
            rarity=rarity,
            reward_data=reward_data,
            unlocked_at=datetime.utcnow(),
            viewed=False,
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        
        logger.info(f"Unlock recorded: user={user_id}, type={unlock_type}, content={content_id}")
        return record

    async def get_user_unlocks(
        self,
        user_id: uuid.UUID,
        unlock_type: Optional[str] = None,
    ) -> List[UnlockRecord]:
        """Get user's unlock records.
        
        Args:
            user_id: User ID
            unlock_type: Optional filter by unlock type
            
        Returns:
            List of UnlockRecord
        """
        query = select(UnlockRecord).where(UnlockRecord.user_id == user_id)
        
        if unlock_type:
            query = query.where(UnlockRecord.unlock_type == unlock_type)
        
        query = query.order_by(UnlockRecord.unlocked_at.desc())
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_as_viewed(self, record_id: uuid.UUID) -> Optional[UnlockRecord]:
        """Mark an unlock record as viewed.
        
        Args:
            record_id: ID of the unlock record
            
        Returns:
            Updated UnlockRecord or None if not found
        """
        result = await self.db.execute(
            select(UnlockRecord).where(UnlockRecord.id == record_id)
        )
        record = result.scalar_one_or_none()
        
        if not record:
            return None
        
        record.viewed = True
        await self.db.flush()
        await self.db.refresh(record)
        
        logger.info(f"Unlock marked as viewed: record={record_id}")
        return record

    async def get_pending_unlocks(self, user_id: uuid.UUID) -> List[UnlockRecord]:
        """Get unviewed unlock records for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of unviewed UnlockRecord
        """
        result = await self.db.execute(
            select(UnlockRecord)
            .where(
                and_(
                    UnlockRecord.user_id == user_id,
                    UnlockRecord.viewed == False,
                )
            )
            .order_by(UnlockRecord.unlocked_at.desc())
        )
        return list(result.scalars().all())

    async def batch_record_unlocks(
        self,
        user_id: uuid.UUID,
        unlocks: List[UnlockBatchItem],
    ) -> List[UnlockRecord]:
        """Record multiple unlocks in batch.
        
        Args:
            user_id: User ID
            unlocks: List of unlock items to record
            
        Returns:
            List of created UnlockRecord
        """
        records = []
        for item in unlocks:
            record = await self.record_unlock(
                user_id=user_id,
                unlock_type=item.unlock_type,
                content_id=item.content_id,
                title=item.title,
                description=item.description,
                image_url=item.image_url,
                rarity=item.rarity,
                reward_data=item.reward_data,
            )
            records.append(record)
        
        logger.info(f"Batch unlock recorded: user={user_id}, count={len(records)}")
        return records

    async def get_unlock_by_id(self, record_id: uuid.UUID) -> Optional[UnlockRecord]:
        """Get a specific unlock record by ID.
        
        Args:
            record_id: Unlock record ID
            
        Returns:
            UnlockRecord or None if not found
        """
        result = await self.db.execute(
            select(UnlockRecord).where(UnlockRecord.id == record_id)
        )
        return result.scalar_one_or_none()
