"""CR3-024: Activity progress and chest claim API.

Activity system tracks daily engagement and rewards users with tiered chests
based on activity points earned throughout the day.
"""

import uuid
from datetime import datetime, date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.daily import DailyTask
from app.models.gallery import ActivityChestClaim
from app.models.payment import Fragment, FragmentTransaction


router = APIRouter(prefix="/activity", tags=["activity"])


# ──────────────────────────────────────────────
# Activity Chest Definitions
# ──────────────────────────────────────────────

ACTIVITY_CHESTS = {
    1: {
        "tier": 1,
        "name": "青铜宝箱",
        "threshold": 50,  # Activity points needed
        "rewards": [
            {"type": "fragments", "amount": 30},
        ],
        "icon": "🥉",
    },
    2: {
        "tier": 2,
        "name": "白银宝箱",
        "threshold": 150,
        "rewards": [
            {"type": "fragments", "amount": 100},
        ],
        "icon": "🥈",
    },
    3: {
        "tier": 3,
        "name": "黄金宝箱",
        "threshold": 300,
        "rewards": [
            {"type": "fragments", "amount": 250},
        ],
        "icon": "🥇",
    },
}


# ──────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────


class ClaimChestRequest(BaseModel):
    chest_tier: int


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────


async def _calculate_activity_points(uid: uuid.UUID, db: AsyncSession) -> int:
    """
    Calculate today's activity points based on completed tasks.
    MVP: Each completed task = 50 points.
    """
    today = date.today()
    result = await db.execute(
        select(func.count(DailyTask.id)).where(
            DailyTask.user_id == uid,
            DailyTask.date == today,
            DailyTask.completed == True,
        )
    )
    completed_tasks = result.scalar() or 0
    return completed_tasks * 50


# ──────────────────────────────────────────────
# CR3-024: Get activity progress
# ──────────────────────────────────────────────


@router.get("/progress")
async def get_activity_progress(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-024: Get current activity progress and chest eligibility.
    """
    uid = uuid.UUID(user_id)
    points = await _calculate_activity_points(uid, db)

    # Get claimed chests
    claimed_result = await db.execute(
        select(ActivityChestClaim).where(
            ActivityChestClaim.user_id == uid,
        )
    )
    claimed_tiers = {c.chest_tier for c in claimed_result.scalars().all()}

    chests = []
    for tier, defn in ACTIVITY_CHESTS.items():
        eligible = points >= defn["threshold"]
        claimed = tier in claimed_tiers
        chests.append({
            "tier": tier,
            "name": defn["name"],
            "icon": defn["icon"],
            "threshold": defn["threshold"],
            "eligible": eligible,
            "claimed": claimed,
            "can_claim": eligible and not claimed,
            "rewards": defn["rewards"],
        })

    return {
        "activity_points": points,
        "chests": chests,
        "reset_at": "UTC 00:00",
    }


# ──────────────────────────────────────────────
# CR3-024: Claim chest
# ──────────────────────────────────────────────


@router.post("/claim")
async def claim_chest(
    request: ClaimChestRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-024: Claim an activity chest reward.
    Returns 400 if not eligible, 409 if already claimed.
    """
    uid = uuid.UUID(user_id)
    tier = request.chest_tier

    if tier not in ACTIVITY_CHESTS:
        raise AppException(
            ErrorCode.ACTIVITY_CHEST_NOT_ELIGIBLE,
            400,
            f"Invalid chest tier: {tier}",
        )

    # Check eligibility
    points = await _calculate_activity_points(uid, db)
    defn = ACTIVITY_CHESTS[tier]

    if points < defn["threshold"]:
        raise AppException(
            ErrorCode.ACTIVITY_CHEST_NOT_ELIGIBLE,
            400,
            f"Not enough activity points ({points}/{defn['threshold']})",
        )

    # Check if already claimed
    claimed = await db.execute(
        select(ActivityChestClaim).where(
            ActivityChestClaim.user_id == uid,
            ActivityChestClaim.chest_tier == tier,
        )
    )
    if claimed.scalar_one_or_none():
        raise AppException(
            ErrorCode.ACTIVITY_CHEST_ALREADY_CLAIMED,
            409,
            f"Chest tier {tier} already claimed",
        )

    # Record claim
    claim = ActivityChestClaim(
        user_id=uid,
        chest_tier=tier,
    )
    db.add(claim)

    # Grant rewards
    total_fragments = 0
    for reward in defn["rewards"]:
        if reward["type"] == "fragments":
            total_fragments += reward["amount"]

    if total_fragments > 0:
        frag_result = await db.execute(
            select(Fragment).where(Fragment.user_id == uid)
        )
        frag = frag_result.scalar_one_or_none()
        if frag:
            frag.balance += total_fragments
        else:
            frag = Fragment(user_id=uid, balance=total_fragments)
            db.add(frag)

        # Record transaction
        tx = FragmentTransaction(
            user_id=uid,
            amount=total_fragments,
            reason=f"activity_chest_tier_{tier}",
        )
        db.add(tx)

    await db.commit()

    return {
        "chest_tier": tier,
        "name": defn["name"],
        "icon": defn["icon"],
        "claimed": True,
        "rewards": defn["rewards"],
        "claimed_at": claim.claimed_at.isoformat(),
    }
