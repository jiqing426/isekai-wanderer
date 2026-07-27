"""Gallery API endpoints."""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.gallery import Collection, Achievement
from app.models.memory import CharacterMemory

router = APIRouter(prefix="/gallery", tags=["gallery"])

# Mock CG data
MOCK_CGS = [
    {"id": "cg-001", "title": "初次相遇", "script_id": "11111111-1111-1111-1111-111111111111", "character_id": "char-001", "unlocked": True, "thumbnail_url": "/assets/cg/1_thumb.jpg", "full_url": "/assets/cg/1_full.jpg"},
    {"id": "cg-002", "title": "月下誓言", "script_id": "11111111-1111-1111-1111-111111111111", "character_id": "char-001", "unlocked": True, "thumbnail_url": "/assets/cg/2_thumb.jpg", "full_url": "/assets/cg/2_full.jpg"},
    {"id": "cg-003", "title": "樱花纷飞", "script_id": "a1111111-1111-1111-1111-111111111111", "character_id": "char-002", "unlocked": True, "thumbnail_url": "/assets/cg/3_thumb.jpg", "full_url": "/assets/cg/3_full.jpg"},
    {"id": "cg-004", "title": "星空告白", "script_id": "66666666-6666-6666-6666-666666666666", "character_id": "char-003", "unlocked": False, "thumbnail_url": "/assets/cg/4_thumb.jpg", "full_url": "/assets/cg/4_full.jpg"},
    {"id": "cg-005", "title": "永恒之约", "script_id": "66666666-6666-6666-6666-666666666666", "character_id": "char-003", "unlocked": False, "thumbnail_url": "/assets/cg/5_thumb.jpg", "full_url": "/assets/cg/5_full.jpg"},
    {"id": "cg-006", "title": "命运重逢", "script_id": "11111111-1111-1111-1111-111111111111", "character_id": "char-001", "unlocked": False, "thumbnail_url": "/assets/cg/6_thumb.jpg", "full_url": "/assets/cg/6_full.jpg"},
]

# Mock achievements
MOCK_ACHIEVEMENTS = [
    {"id": "ach-001", "name": "初见", "description": "完成第一次对话", "icon": "🎭", "unlocked": True, "unlocked_at": "2026-07-15T10:00:00Z"},
    {"id": "ach-002", "name": "羁绊", "description": "好感度达到60", "icon": "💕", "unlocked": True, "unlocked_at": "2026-07-16T14:30:00Z"},
    {"id": "ach-003", "name": "探索者", "description": "完成3个剧本", "icon": "🗺️", "unlocked": True, "unlocked_at": "2026-07-17T08:00:00Z"},
    {"id": "ach-004", "name": "收藏家", "description": "收集10个CG", "icon": "📸", "unlocked": True, "unlocked_at": "2026-07-17T12:00:00Z"},
    {"id": "ach-005", "name": "完美结局", "description": "达成所有good ending", "icon": "🌟", "unlocked": False, "unlocked_at": None},
    {"id": "ach-006", "name": "全勤", "description": "连续登录30天", "icon": "📅", "unlocked": False, "unlocked_at": None},
    {"id": "ach-007", "name": "真爱", "description": "好感度达到100", "icon": "❤️", "unlocked": False, "unlocked_at": None},
    {"id": "ach-008", "name": "大师", "description": "解锁所有成就", "icon": "👑", "unlocked": False, "unlocked_at": None},
]


class CollectionItem(BaseModel):
    item_type: str  # "cg" | "character" | "scene"
    item_id: str
    item_name: str
    image_url: Optional[str] = None


class AchievementItem(BaseModel):
    achievement_id: str
    title: str
    description: Optional[str] = None
    icon_url: Optional[str] = None


@router.post("/collections")
async def add_collection(
    item: CollectionItem,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Add item to user's collection."""
    collection = Collection(
        user_id=UUID(user_id),
        item_type=item.item_type,
        item_id=item.item_id,
        item_name=item.item_name,
        image_url=item.image_url,
    )
    db.add(collection)
    await db.commit()
    await db.refresh(collection)

    return {
        "id": str(collection.id),
        "user_id": str(collection.user_id),
        "item_type": collection.item_type,
        "item_id": collection.item_id,
        "item_name": collection.item_name,
        "image_url": collection.image_url,
        "unlocked_at": collection.unlocked_at.isoformat(),
    }


@router.get("/collections")
async def get_collections(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get user's collection list."""
    result = await db.execute(
        select(Collection).where(Collection.user_id == UUID(user_id)).order_by(Collection.unlocked_at.desc())
    )
    collections = result.scalars().all()

    return {
        "collections": [
            {
                "id": str(c.id),
                "item_type": c.item_type,
                "item_id": c.item_id,
                "item_name": c.item_name,
                "image_url": c.image_url,
                "unlocked_at": c.unlocked_at.isoformat(),
            }
            for c in collections
        ]
    }


@router.delete("/collections/{collection_id}")
async def delete_collection(
    collection_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete item from collection."""
    result = await db.execute(
        select(Collection).where(
            Collection.id == UUID(collection_id),
            Collection.user_id == UUID(user_id),
        )
    )
    collection = result.scalar_one_or_none()

    if not collection:
        raise AppException(ErrorCode.COLLECTION_NOT_FOUND, 404, "Collection item not found")

    await db.delete(collection)
    await db.commit()

    return {"status": "deleted"}


@router.post("/achievements")
async def unlock_achievement(
    achievement: AchievementItem,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Unlock an achievement."""
    ach = Achievement(
        user_id=UUID(user_id),
        achievement_id=achievement.achievement_id,
        title=achievement.title,
        description=achievement.description,
        icon_url=achievement.icon_url,
    )
    db.add(ach)
    await db.commit()
    await db.refresh(ach)

    return {
        "id": str(ach.id),
        "user_id": str(ach.user_id),
        "achievement_id": ach.achievement_id,
        "title": ach.title,
        "description": ach.description,
        "icon_url": ach.icon_url,
        "unlocked_at": ach.unlocked_at.isoformat(),
    }


@router.get("/achievements")
async def get_achievements(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get user's achievement list."""
    result = await db.execute(
        select(Achievement).where(Achievement.user_id == UUID(user_id)).order_by(Achievement.unlocked_at.desc())
    )
    achievements = result.scalars().all()

    return {
        "achievements": [
            {
                "id": str(a.id),
                "achievement_id": a.achievement_id,
                "title": a.title,
                "description": a.description,
                "icon_url": a.icon_url,
                "unlocked_at": a.unlocked_at.isoformat(),
            }
            for a in achievements
        ]
    }


@router.get("/cgs")
async def get_cgs(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get CG gallery with unlock status."""
    return {"cgs": MOCK_CGS}


@router.get("/memories")
async def get_memories(
    character_id: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get user's character memories (CR3-054 / AC-GAME-013)."""
    uid = UUID(user_id)
    query = select(CharacterMemory).where(CharacterMemory.user_id == uid)
    
    if character_id:
        try:
            cid = UUID(character_id)
            query = query.where(CharacterMemory.character_id == cid)
        except ValueError:
            raise AppException(
                ErrorCode.INVALID_REQUEST, 400, "Invalid character_id format"
            )
    
    query = query.order_by(CharacterMemory.created_at.desc()).limit(limit)
    result = await db.execute(query)
    memories = result.scalars().all()

    return {
        "memories": [
            {
                "id": str(m.id),
                "character_id": str(m.character_id),
                "content": m.memory_text,
                "source": m.source or "unknown",
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in memories
        ]
    }


# Separate router for /achievements (no /gallery prefix)
achievements_router = APIRouter(prefix="/achievements", tags=["achievements"])


@achievements_router.get("")
async def get_achievements_wall(
    user_id: str = Depends(get_current_user_id),
):
    """Get achievement wall with unlock status (mock data)."""
    return {"achievements": MOCK_ACHIEVEMENTS}
