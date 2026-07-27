"""W06 User dialogue count API."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID

from app.core.database import get_db
from app.models.user_dialogue_count import UserDialogueCount
from app.api.v1.auth import get_current_user_id

router = APIRouter(prefix="/user", tags=["user"])


class DialogueCountRequest(BaseModel):
    script_id: str


@router.get("/dialogue-count")
async def get_dialogue_count(
    script_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get user's dialogue count for a specific script."""
    result = await db.execute(
        select(UserDialogueCount).where(
            UserDialogueCount.user_id == UUID(user_id),
            UserDialogueCount.script_id == UUID(script_id)
        )
    )
    record = result.scalar_one_or_none()
    
    count = record.dialogue_count if record else 0
    limit = 3  # 免费用户限制
    
    return {
        "dialogue_count": count,
        "limit": limit,
        "can_continue": count < limit
    }


@router.post("/dialogue-count")
async def increment_dialogue_count(
    body: DialogueCountRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Increment user's dialogue count for a specific script."""
    result = await db.execute(
        select(UserDialogueCount).where(
            UserDialogueCount.user_id == UUID(user_id),
            UserDialogueCount.script_id == UUID(body.script_id)
        )
    )
    record = result.scalar_one_or_none()
    
    if not record:
        record = UserDialogueCount(
            user_id=UUID(user_id),
            script_id=UUID(body.script_id),
            dialogue_count=1
        )
        db.add(record)
    else:
        record.dialogue_count += 1
        from datetime import datetime
        record.last_dialogue_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(record)
    
    limit = 3
    return {
        "dialogue_count": record.dialogue_count,
        "limit": limit,
        "can_continue": record.dialogue_count < limit,
        "message": "已达到免费试用限制" if record.dialogue_count >= limit else None
    }
