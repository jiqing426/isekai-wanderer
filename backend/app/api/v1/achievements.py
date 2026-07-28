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
    "ACH-009": {
        "id": "ACH-009",
        "name": "社交达人",
        "description": "添加 5 个好友",
        "icon": "🤝",
        "rarity": "common",
        "reward_type": "fragments",
        "reward_amount": 30,
        "condition": {"type": "friends_count", "value": 5},
        "progress_target": 5,
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


@router.get("")
async def list_achievements(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-020: List all achievement definitions with user unlock/claim state.
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
    for ach_id, defn in ACHIEVEMENT_CATALOG.items():
        user_ach = unlocked.get(ach_id)
        user_claim = claimed.get(ach_id)
        
        # Calculate progress (for now, return 0 for unlocked, target for completed)
        # TODO: Implement actual progress tracking based on condition type
        progress = 0
        if user_ach:
            progress = defn["progress_target"]
        
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
            "unlockedAt": user_ach.unlocked_at.isoformat() if user_ach else None,
            "claimedAt": user_claim.claimed_at.isoformat() if user_claim else None,
        })

    return {
        "achievements": items,
        "total": len(items),
        "unlocked_count": len(unlocked),
        "claimed_count": len(claimed),
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
