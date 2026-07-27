"""Affection decay service — CR-016 Phase 2.

Implements affection decay based on user inactivity:
- 3 days or less inactive: no decay
- 4-7 days inactive: -2 affection per day
- 7+ days inactive: -5 affection per day
- Minimum affection floor: 10 (never goes below)
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.affection import Affection
from app.models.user import User

logger = logging.getLogger(__name__)


class AffectionService:
    """Service for managing character affection with decay on login."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def apply_decay(self, user_id: UUID) -> Dict:
        """Apply affection decay based on user inactivity.
        
        Called on user login. Calculates days since last login,
        applies appropriate decay to all character affections,
        and updates affection_decay_last_calc timestamp.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            Dict with decay details:
            {
                "days_inactive": int,
                "decay_per_day": int,
                "characters_decayed": int,
                "total_decay_applied": int,
                "decay_applied": bool
            }
        """
        # Get user's last_login and affection_decay_last_calc
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"User not found for decay: {user_id}")
            return {"decay_applied": False, "error": "user_not_found"}
        
        # Calculate days since last login
        if not user.last_login:
            # First login or no last_login recorded — no decay
            logger.info(f"No last_login for user {user_id}, skipping decay")
            return {
                "days_inactive": 0,
                "decay_per_day": 0,
                "characters_decayed": 0,
                "total_decay_applied": 0,
                "decay_applied": False
            }
        
        now = datetime.now(timezone.utc)
        last_login = user.last_login
        
        # Ensure timezone-aware
        if last_login.tzinfo is None:
            last_login = last_login.replace(tzinfo=timezone.utc)
        
        days_inactive = (now - last_login).days
        
        # Determine decay rate
        if days_inactive <= 3:
            # 3 days or less: no decay
            decay_per_day = 0
        elif days_inactive <= 7:
            # 4-7 days: -2 per day
            decay_per_day = 2
        else:
            # 7+ days: -5 per day
            decay_per_day = 5
        
        if decay_per_day == 0:
            logger.info(f"User {user_id} inactive {days_inactive} days, no decay needed")
            return {
                "days_inactive": days_inactive,
                "decay_per_day": 0,
                "characters_decayed": 0,
                "total_decay_applied": 0,
                "decay_applied": False
            }
        
        # Calculate total decay amount
        total_decay = decay_per_day * days_inactive
        
        # Get all affection records for this user
        result = await self.db.execute(
            select(Affection).where(Affection.user_id == user_id)
        )
        affections = result.scalars().all()
        
        characters_decayed = 0
        total_applied = 0
        
        # Apply decay to each character
        for affection in affections:
            old_value = affection.value
            new_value = max(10, old_value - total_decay)  # Floor at 10
            
            if new_value < old_value:
                affection.value = new_value
                characters_decayed += 1
                total_applied += (old_value - new_value)
                logger.info(
                    f"Decay applied: user={user_id}, character={affection.character_id}, "
                    f"{old_value} -> {new_value} (delta={old_value - new_value})"
                )
        
        # Update affection_decay_last_calc
        user.affection_decay_last_calc = now
        await self.db.flush()
        
        logger.info(
            f"Decay complete: user={user_id}, days_inactive={days_inactive}, "
            f"decay_per_day={decay_per_day}, characters_decayed={characters_decayed}, "
            f"total_applied={total_applied}"
        )
        
        return {
            "days_inactive": days_inactive,
            "decay_per_day": decay_per_day,
            "characters_decayed": characters_decayed,
            "total_decay_applied": total_applied,
            "decay_applied": characters_decayed > 0
        }

    async def get_affection_list(self, user_id: UUID) -> List[Dict]:
        """Get all character affection values for a user.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            List of dicts with character_id and affection value
        """
        result = await self.db.execute(
            select(Affection).where(Affection.user_id == user_id)
        )
        affections = result.scalars().all()
        
        return [
            {
                "character_id": str(affection.character_id),
                "value": affection.value
            }
            for affection in affections
        ]

    async def get_affection(self, user_id: UUID, character_id: UUID) -> int:
        """Get affection value for a specific character.
        
        Args:
            user_id: The user's UUID
            character_id: The character's UUID
            
        Returns:
            Affection value (defaults to 0 if not found)
        """
        result = await self.db.execute(
            select(Affection).where(
                Affection.user_id == user_id,
                Affection.character_id == character_id
            )
        )
        affection = result.scalar_one_or_none()
        
        return affection.value if affection else 0
