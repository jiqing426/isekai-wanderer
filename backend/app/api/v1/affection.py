"""Affection API endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.affection import Affection, AffectionHistory
from app.models.script import Character
from app.services.narrative.affection_service import AffectionService
from app.services.narrative.rule_engine import get_affection_level

router = APIRouter(prefix="/affection", tags=["affection"])


@router.get("")
async def get_all_affections(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get all character affection values for the current user."""
    try:
        service = AffectionService(db)
        affections = await service.get_all_affections(UUID(user_id))
        return {"affections": affections}
    except AppException:
        raise
    except Exception as e:
        raise AppException(ErrorCode.INTERNAL_ERROR, 500, f"Failed to fetch affections: {e}")


@router.get("/history")
async def get_affection_history(
    character_id: str = Query(..., description="Character ID"),
    limit: int = Query(50, ge=1, le=200),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    DEV-BE-009: Get affection change history for a specific character.
    
    Returns a list of affection changes with timestamps and reasons.
    """
    try:
        char_uuid = UUID(character_id)
        user_uuid = UUID(user_id)

        # Verify character exists
        char_result = await db.execute(select(Character).where(Character.id == char_uuid))
        character = char_result.scalar_one_or_none()
        if not character:
            raise AppException(ErrorCode.CHARACTER_NOT_FOUND, 404, "Character not found")

        # Fetch history
        stmt = (
            select(AffectionHistory)
            .where(
                AffectionHistory.user_id == user_uuid,
                AffectionHistory.character_id == char_uuid,
            )
            .order_by(AffectionHistory.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        history_rows = list(result.scalars().all())

        return {
            "character_id": str(character_id),
            "character_name": character.name,
            "history": [
                {
                    "id": str(h.id),
                    "delta": h.delta,
                    "old_value": h.old_value,
                    "new_value": h.new_value,
                    "old_level": h.old_level,
                    "new_level": h.new_level,
                    "reason": h.reason,
                    "source_session_id": str(h.source_session_id) if h.source_session_id else None,
                    "source_choice_id": str(h.source_choice_id) if h.source_choice_id else None,
                    "created_at": h.created_at.isoformat(),
                }
                for h in history_rows
            ],
            "total": len(history_rows),
        }
    except AppException:
        raise
    except Exception as e:
        raise AppException(ErrorCode.INTERNAL_ERROR, 500, f"Failed to fetch affection history: {e}")


@router.get("/{character_id}")
async def get_affection(
    character_id: str,
    limit: int = Query(50, ge=1, le=200),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get affection for a specific character, including change history."""
    try:
        char_uuid = UUID(character_id)
        user_uuid = UUID(user_id)

        service = AffectionService(db)
        affection = await service.get_affection(user_uuid, char_uuid)

        # Look up character name
        char_result = await db.execute(select(Character).where(Character.id == char_uuid))
        character = char_result.scalar_one_or_none()
        character_name = character.name if character else "Unknown"

        # Fetch history
        stmt = (
            select(AffectionHistory)
            .where(
                AffectionHistory.user_id == user_uuid,
                AffectionHistory.character_id == char_uuid,
            )
            .order_by(AffectionHistory.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        history_rows = list(result.scalars().all())
    except AppException:
        raise
    except Exception as e:
        raise AppException(ErrorCode.INTERNAL_ERROR, 500, f"Failed to fetch affection: {e}")

    return {
        "character_id": str(affection.character_id),
        "character_name": character_name,
        "affection_value": affection.value,
        "level": get_affection_level(affection.value),
        "history": [
            {
                "delta": h.delta,
                "old_value": h.old_value,
                "new_value": h.new_value,
                "old_level": h.old_level,
                "new_level": h.new_level,
                "reason": h.reason,
                "created_at": h.created_at.isoformat(),
            }
            for h in history_rows
        ],
    }
