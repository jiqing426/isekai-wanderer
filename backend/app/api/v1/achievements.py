"""CR3-020/021: Achievement definition, trigger, and claim API.

Replaces the mock achievements data previously in gallery.py with a
DB-backed achievement system that supports:
- Definition catalog (hardcoded for MVP)
- Trigger/unlock API (called by game engine or manual)
- Claim reward API (user claims unlocked achievements)
- Fragment reward granting via payment models
"""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.gallery import Achievement, UserAchievementClaim
from app.models.payment import Fragment, FragmentTransaction


router = APIRouter(prefix="/achievements", tags=["achievements"])


# ──────────────────────────────────────────────
# Achievement Catalog (MVP: hardcoded definitions)
# ──────────────────────────────────────────────

ACHIEVEMENT_CATALOG = {
    "ACH-001": {
        "id": "ACH-001",
        "name": "初见",
        "description": "完成第一次对话",
        "icon": "🎭",
        "rarity": "common",
        "reward_type": "fragments",
        "reward_amount": 20,
        "condition": {"type": "dialogue_count", "value": 1},
        "progress_target": 1,
    },
    "ACH-002": {
        "id": "ACH-002",
        "name": "羁绊",
        "description": "好感度达到 60",
        "icon": "💕",
        "rarity": "common",
        "reward_type": "fragments",
        "reward_amount": 50,
        "condition": {"type": "affection", "value": 60},
        "progress_target": 60,
    },
    "ACH-003": {
        "id": "ACH-003",
        "name": "探索者",
        "description": "完成 3 个剧本",
        "icon": "🗺️",
        "rarity": "common",
        "reward_type": "fragments",
        "reward_amount": 100,
        "condition": {"type": "completed_scripts", "value": 3},
        "progress_target": 3,
    },
    "ACH-004": {
        "id": "ACH-004",
        "name": "收藏家",
        "description": "收集 10 个 CG",
        "icon": "📸",
        "rarity": "rare",
        "reward_type": "fragments",
        "reward_amount": 80,
        "condition": {"type": "cg_count", "value": 10},
        "progress_target": 10,
    },
    "ACH-005": {
        "id": "ACH-005",
        "name": "完美结局",
        "description": "达成所有 good ending",
        "icon": "🌟",
        "rarity": "rare",
        "reward_type": "fragments",
        "reward_amount": 200,
        "condition": {"type": "all_good_endings", "value": 1},
        "progress_target": 1,
    },
    "ACH-006": {
        "id": "ACH-006",
        "name": "全勤",
        "description": "连续登录 30 天",
        "icon": "📅",
        "rarity": "rare",
        "reward_type": "fragments",
        "reward_amount": 300,
        "condition": {"type": "streak", "value": 30},
        "progress_target": 30,
    },
    "ACH-007": {
        "id": "ACH-007",
        "name": "真爱",
        "description": "好感度达到 100",
        "icon": "❤️",
        "rarity": "epic",
        "reward_type": "fragments",
        "reward_amount": 200,
        "condition": {"type": "affection", "value": 100},
        "progress_target": 100,
    },
    "ACH-008": {
        "id": "ACH-008",
        "name": "大师",
        "description": "解锁所有成就",
        "icon": "👑",
        "rarity": "epic",
        "reward_type": "fragments",
        "reward_amount": 500,
        "condition": {"type": "all_achievements_unlocked", "value": 1},
        "progress_target": 1,
    },
    "ACH-010": {
        "id": "ACH-010",
        "name": "月度玩家",
        "description": "连续登录 7 天",
        "icon": "📆",
        "rarity": "common",
        "reward_type": "fragments",
        "reward_amount": 40,
        "condition": {"type": "streak", "value": 7},
        "progress_target": 7,
    },
    "ACH-011": {
        "id": "ACH-011",
        "name": "礼物大师",
        "description": "送出 20 个礼物",
        "icon": "🎁",
        "rarity": "rare",
        "reward_type": "fragments",
        "reward_amount": 150,
        "condition": {"type": "gifts_sent", "value": 20},
        "progress_target": 20,
    },
    "ACH-012": {
        "id": "ACH-012",
        "name": "剧情分支",
        "description": "探索 10 条剧情分支",
        "icon": "🔀",
        "rarity": "rare",
        "reward_type": "fragments",
        "reward_amount": 120,
        "condition": {"type": "branches_explored", "value": 10},
        "progress_target": 10,
    },
    "ACH-013": {
        "id": "ACH-013",
        "name": "全角色解锁",
        "description": "解锁所有角色",
        "icon": "🎭",
        "rarity": "epic",
        "reward_type": "fragments",
        "reward_amount": 400,
        "condition": {"type": "characters_unlocked", "value": 1},
        "progress_target": 1,
    },
    "ACH-014": {
        "id": "ACH-014",
        "name": "对话专家",
        "description": "完成 50 次对话",
        "icon": "💬",
        "rarity": "rare",
        "reward_type": "fragments",
        "reward_amount": 180,
        "condition": {"type": "dialogue_count", "value": 50},
        "progress_target": 50,
    },
    "ACH-015": {
        "id": "ACH-015",
        "name": "选择困难",
        "description": "做出 100 次选择",
        "icon": "🤔",
        "rarity": "epic",
        "reward_type": "fragments",
        "reward_amount": 350,
        "condition": {"type": "choice_count", "value": 100},
        "progress_target": 100,
    },
}


# ──────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────


class UnlockAchievementRequest(BaseModel):
    achievement_id: str


# ──────────────────────────────────────────────
# CR3-020: List achievements (catalog + user state)
# ──────────────────────────────────────────────


async def _calculate_progress(
    condition_type: str,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> int:
    """
    根据成就条件类型计算用户当前进度。
    """
    from app.models.gallery import Achievement
    from app.models.script import Character
    from app.models.affection import Affection
    from app.models.gift_record import GiftRecord
    
    if condition_type == "streak":
        # 连续签到天数
        from app.models.daily import DailyCheckin
        from datetime import date, timedelta
        
        # 获取所有签到记录，按日期倒序
        result = await db.execute(
            select(DailyCheckin.date)
            .where(DailyCheckin.user_id == user_id)
            .order_by(DailyCheckin.date.desc())
        )
        dates = [row[0] for row in result.all()]
        
        if not dates:
            return 0
        
        # 计算连续签到天数（从今天往前推）
        today = date.today()
        streak = 0
        expected_date = today
        
        for d in dates:
            if d == expected_date:
                streak += 1
                expected_date = expected_date - timedelta(days=1)
            elif d < expected_date:
                # 断签了，停止计算
                break
        
        return streak
    
    elif condition_type == "dialogue_count":
        # 对话次数（从 game_sessions 统计）
        from app.models.game import GameSession
        result = await db.execute(
            select(func.count(GameSession.id))
            .where(GameSession.user_id == user_id)
        )
        return result.scalar() or 0
    
    elif condition_type == "affection":
        # 最高好感度
        result = await db.execute(
            select(func.max(Affection.value))
            .where(Affection.user_id == user_id)
        )
        return result.scalar() or 0
    
    elif condition_type == "completed_scripts":
        # 完成的剧本数（有 completed_at 的 session）
        from app.models.game import GameSession
        result = await db.execute(
            select(func.count(GameSession.id))
            .where(
                GameSession.user_id == user_id,
                GameSession.completed_at.isnot(None)
            )
        )
        return result.scalar() or 0
    
    elif condition_type == "gifts_sent":
        # 送出礼物总数
        result = await db.execute(
            select(func.sum(GiftRecord.quantity))
            .where(GiftRecord.user_id == user_id)
        )
        return result.scalar() or 0
    
    elif condition_type == "characters_unlocked":
        # 解锁角色数（有好感度记录的视为解锁）
        result = await db.execute(
            select(func.count(func.distinct(Affection.character_id)))
            .where(Affection.user_id == user_id)
        )
        return result.scalar() or 0
    
    elif condition_type == "choice_count":
        # 选择次数（从 game_progress 统计）
        from app.models.game import GameProgress, GameSession
        result = await db.execute(
            select(func.count(GameProgress.id))
            .where(
                GameProgress.session_id.in_(
                    select(GameSession.id).where(GameSession.user_id == user_id)
                ),
                GameProgress.choice_id.isnot(None)
            )
        )
        return result.scalar() or 0
    
    elif condition_type == "branches_explored":
        # 探索的分支数（不同 node_id 的数量）
        from app.models.game import GameProgress, GameSession
        result = await db.execute(
            select(func.count(func.distinct(GameProgress.node_id)))
            .where(
                GameProgress.session_id.in_(
                    select(GameSession.id).where(GameSession.user_id == user_id)
                )
            )
        )
        return result.scalar() or 0
    
    elif condition_type == "cg_count":
        # 收集的CG数量
        from app.models.asset import UnlockedCG
        result = await db.execute(
            select(func.count(UnlockedCG.id))
            .where(UnlockedCG.user_id == user_id)
        )
        return result.scalar() or 0
    
    # 其他条件类型暂时返回 0
    return 0


@router.get("")
async def list_achievements(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-020: List all achievement definitions with user unlock/claim state.
    自动解锁进度已达标的成就。
    """
    uid = uuid.UUID(user_id)

    # Get user's unlocked achievements
    unlocked_result = await db.execute(
        select(Achievement).where(Achievement.user_id == uid)
    )
    unlocked = {a.achievement_id.upper(): a for a in unlocked_result.scalars().all()}

    # Get user's claimed achievements
    claimed_result = await db.execute(
        select(UserAchievementClaim).where(UserAchievementClaim.user_id == uid)
    )
    claimed = {c.achievement_id.upper(): c for c in claimed_result.scalars().all()}

    items = []
    auto_unlocked = []  # 记录本次自动解锁的成就
    
    for ach_id, defn in ACHIEVEMENT_CATALOG.items():
        user_ach = unlocked.get(ach_id)
        user_claim = claimed.get(ach_id)
        
        # 计算真实进度
        condition_type = defn["condition"]["type"]
        progress = await _calculate_progress(condition_type, uid, db)
        
        # 如果已解锁，进度至少是目标值
        if user_ach:
            progress = max(progress, defn["progress_target"])
        
        # 自动解锁：进度达标且未解锁
        if not user_ach and progress >= defn["progress_target"] and defn["progress_target"] > 0:
            # 自动解锁这个成就
            new_achievement = Achievement(
                user_id=uid,
                achievement_id=ach_id,
                title=defn["name"],
                description=defn["description"],
                icon_url=defn["icon"],
            )
            db.add(new_achievement)
            auto_unlocked.append(ach_id)
            user_ach = new_achievement  # 更新引用，后续逻辑可以正确处理
        
        items.append({
            "id": ach_id,
            "name": defn["name"],
            "description": defn["description"],
            "icon": defn["icon"],
            "rarity": defn["rarity"],
            "reward": {
                "type": defn["reward_type"],
                "amount": defn["reward_amount"],
            },
            "condition": defn["condition"],
            "progress": {
                "current": progress,
                "target": defn["progress_target"],
            },
            "isUnlocked": user_ach is not None,
            "isClaimed": user_claim is not None,
            "unlockedAt": user_ach.unlocked_at.isoformat() if user_ach and hasattr(user_ach, 'unlocked_at') and user_ach.unlocked_at else None,
            "claimedAt": user_claim.claimed_at.isoformat() if user_claim else None,
        })

    # 提交自动解锁的记录
    if auto_unlocked:
        await db.commit()
        # 刷新新添加的记录以获取 unlocked_at
        for ach_id in auto_unlocked:
            refreshed = await db.execute(
                select(Achievement).where(
                    Achievement.user_id == uid,
                    Achievement.achievement_id == ach_id
                )
            )
            refreshed_ach = refreshed.scalar_one_or_none()
            if refreshed_ach:
                # 更新 items 中的 unlockedAt
                for item in items:
                    if item["id"] == ach_id:
                        item["isUnlocked"] = True
                        item["unlockedAt"] = refreshed_ach.unlocked_at.isoformat()
                        break

    return {
        "achievements": items,
        "total": len(items),
        "unlocked_count": len([i for i in items if i["isUnlocked"]]),
        "claimed_count": len(claimed),
        "auto_unlocked": auto_unlocked,  # 返回本次自动解锁的成就列表
    }


# ──────────────────────────────────────────────
# CR3-020: Trigger/unlock achievement
# ──────────────────────────────────────────────


@router.post("/unlock")
async def trigger_achievement(
    request: UnlockAchievementRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-020: Trigger (unlock) an achievement for the user.
    Called by game engine when condition is met, or manually for testing.
    """
    uid = uuid.UUID(user_id)
    ach_id = request.achievement_id.upper()  # 转换为大写以匹配 CATALOG

    if ach_id not in ACHIEVEMENT_CATALOG:
        raise AppException(
            ErrorCode.ACHIEVEMENT_NOT_FOUND,
            404,
            f"Achievement '{ach_id}' not defined in catalog",
        )

    # Check if already unlocked
    existing = await db.execute(
        select(Achievement).where(
            Achievement.user_id == uid,
            Achievement.achievement_id == ach_id,
        )
    )
    if existing.scalar_one_or_none():
        raise AppException(
            ErrorCode.ACHIEVEMENT_ALREADY_UNLOCKED,
            409,
            f"Achievement '{ach_id}' already unlocked",
        )

    defn = ACHIEVEMENT_CATALOG[ach_id]
    achievement = Achievement(
        user_id=uid,
        achievement_id=ach_id,
        title=defn["name"],
        description=defn["description"],
        icon_url=defn["icon"],
    )
    db.add(achievement)
    await db.commit()
    await db.refresh(achievement)

    return {
        "achievement_id": ach_id,
        "title": defn["name"],
        "description": defn["description"],
        "icon": defn["icon"],
        "unlocked_at": achievement.unlocked_at.isoformat(),
        "reward": {"type": defn["reward_type"], "amount": defn["reward_amount"]},
    }


# ──────────────────────────────────────────────
# CR3-021: Claim achievement reward
# ──────────────────────────────────────────────


@router.post("/claim")
async def claim_achievement(
    request: UnlockAchievementRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-021: Claim the reward for an unlocked achievement.
    Returns 400 if not unlocked, 409 if already claimed.
    """
    uid = uuid.UUID(user_id)
    ach_id = request.achievement_id.upper()  # 转换为大写以匹配 CATALOG

    if ach_id not in ACHIEVEMENT_CATALOG:
        raise AppException(
            ErrorCode.ACHIEVEMENT_NOT_FOUND,
            404,
            f"Achievement '{ach_id}' not defined",
        )

    # Check if unlocked
    unlocked = await db.execute(
        select(Achievement).where(
            Achievement.user_id == uid,
            Achievement.achievement_id == ach_id,
        )
    )
    if not unlocked.scalars().first():
        raise AppException(
            ErrorCode.ACHIEVEMENT_NOT_UNLOCKED,
            400,
            f"Achievement '{ach_id}' not yet unlocked",
        )

    # Check if already claimed
    claimed = await db.execute(
        select(UserAchievementClaim).where(
            UserAchievementClaim.user_id == uid,
            UserAchievementClaim.achievement_id == ach_id,
        )
    )
    if claimed.scalars().first():
        raise AppException(
            ErrorCode.ACHIEVEMENT_ALREADY_CLAIMED,
            409,
            f"Achievement '{ach_id}' reward already claimed",
        )

    defn = ACHIEVEMENT_CATALOG[ach_id]
    reward_amount = defn["reward_amount"]

    # Record claim
    claim = UserAchievementClaim(
        user_id=uid,
        achievement_id=ach_id,
        reward_type=defn["reward_type"],
        reward_amount=reward_amount,
    )
    db.add(claim)

    # Grant fragment reward
    frag_result = await db.execute(
        select(Fragment).where(Fragment.user_id == uid)
    )
    frag = frag_result.scalar_one_or_none()
    if frag:
        frag.balance += reward_amount
    else:
        frag = Fragment(user_id=uid, balance=reward_amount)
        db.add(frag)

    # Record transaction
    tx = FragmentTransaction(
        user_id=uid,
        amount=reward_amount,
        reason=f"achievement_claim:{ach_id}",
    )
    db.add(tx)

    await db.commit()

    return {
        "achievement_id": ach_id,
        "claimed": True,
        "reward": {"type": defn["reward_type"], "amount": reward_amount},
        "claimed_at": claim.claimed_at.isoformat(),
    }
