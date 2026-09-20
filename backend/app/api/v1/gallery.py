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
from app.models.gallery import Achievement
from app.models.memory import CharacterMemory
from app.services.subscription_service import SubscriptionService

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


class AchievementItem(BaseModel):
    achievement_id: str
    title: str
    description: Optional[str] = None
    icon_url: Optional[str] = None


@router.get("/collections")
async def get_collections(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get user's collection list grouped by script."""
    from app.models.asset import UnlockedCG, CGAsset
    from app.models.script import Script, Route
    
    # 查询所有剧本及其 CG 总数
    scripts_result = await db.execute(
        select(Script, Route, CGAsset)
        .outerjoin(Route, Route.script_id == Script.id)
        .outerjoin(CGAsset, CGAsset.route_id == Route.id)
        .order_by(Script.created_at.desc())
    )
    scripts_data = scripts_result.all()
    
    # 按剧本分组统计
    script_stats = {}
    for script, route, cg_asset in scripts_data:
        script_id = str(script.id)
        if script_id not in script_stats:
            script_stats[script_id] = {
                "id": script_id,
                "name": script.title,
                "description": script.description or "",
                "cover_url": script.cover_image_url,
                "items_count": 0,
                "items_unlocked": 0,
                "script_id": script_id,
            }
        if cg_asset:
            script_stats[script_id]["items_count"] += 1
    
    # 查询用户解锁的 CG
    unlocked_result = await db.execute(
        select(UnlockedCG, CGAsset, Script)
        .join(CGAsset, UnlockedCG.cg_id == CGAsset.id)
        .join(Script, CGAsset.script_id == Script.id)
        .where(UnlockedCG.user_id == UUID(user_id))
    )
    unlocked_cgs = unlocked_result.all()
    
    for ucg, cg_asset, script in unlocked_cgs:
        script_id = str(script.id)
        if script_id in script_stats:
            script_stats[script_id]["items_unlocked"] += 1
    
    # 只返回有 CG 的剧本
    collection_list = [s for s in script_stats.values() if s["items_count"] > 0]
    
    return {"collections": collection_list}


@router.get("/collections/{script_id}")
async def get_collection_items(
    script_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get all CG items for a specific script with unlock status."""
    from app.models.asset import UnlockedCG, CGAsset
    from app.models.script import Script, Route
    
    # 查询该剧本的所有CG
    cg_result = await db.execute(
        select(CGAsset, Route)
        .join(Route, CGAsset.route_id == Route.id)
        .where(Route.script_id == UUID(script_id))
        .order_by(CGAsset.created_at.asc())
    )
    cg_assets = cg_result.all()
    
    if not cg_assets:
        return {"items": []}
    
    # 查询用户解锁的CG ID列表
    unlocked_result = await db.execute(
        select(UnlockedCG.cg_id)
        .where(UnlockedCG.user_id == UUID(user_id))
    )
    unlocked_cg_ids = {str(row[0]) for row in unlocked_result.all()}
    
    # CR-043: Get user subscription tier for is_accessible calculation
    sub_service = SubscriptionService(db)
    tier = await sub_service.get_user_tier(UUID(user_id))
    tier_allows_full = tier in ("standard", "premium")
    
    # 构建返回数据
    items = []
    for cg_asset, route in cg_assets:
        cg_id = str(cg_asset.id)
        is_unlocked = cg_id in unlocked_cg_ids
        # CR-043 AC-001: is_accessible = is_unlocked OR tier_allows_full
        is_accessible = is_unlocked or tier_allows_full
        
        items.append({
            "id": cg_id,
            "collection_id": script_id,
            "title": cg_asset.name,
            "thumbnail_url": cg_asset.image_url,
            "full_url": cg_asset.image_url,
            "script_name": route.title if route else "",
            "unlock_status": "unlocked" if is_unlocked else "locked",
            "unlock_condition": "完成特定剧情节点" if not is_unlocked else "",
            "is_accessible": is_accessible,  # CR-043: new field
        })
    
    return {"items": items}


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
    db: AsyncSession = Depends(get_db),
):
    """Get achievement wall with real progress data."""
    from app.api.v1.users import get_achievements
    # Reuse the real achievements logic from /users/me/achievements
    result = await get_achievements(user_id=user_id, db=db)
    
    # Convert snake_case to camelCase for frontend compatibility
    achievements = []
    for ach in result["achievements"]:
        achievements.append({
            "id": ach["id"],
            "name": ach["name"],
            "description": ach["description"],
            "icon": ach["icon"],
            "iconUrl": ach.get("icon_url"),
            "isUnlocked": ach["is_unlocked"],
            "isClaimed": ach["reward"]["claimed"] if ach.get("reward") else False,
            "unlockedAt": ach.get("unlocked_at"),
            "progress": ach.get("progress"),
            "condition": {
                "type": ach["id"].replace("ach_", ""),
                "current": ach["progress"]["current"] if ach.get("progress") else 0,
                "target": ach["progress"]["target"] if ach.get("progress") else 1,
            },
            "reward": {
                "type": ach["reward"]["type"] if ach.get("reward") else "fragments",
                "amount": ach["reward"]["amount"] if ach.get("reward") else 0,
            } if ach.get("reward") else None,
        })
    
    return {
        "achievements": achievements,
        "total": result["total"],
        "unlocked_count": result["unlocked_count"],
        "claimed_count": result["claimed_count"],
    }
