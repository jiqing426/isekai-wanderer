"""Sign-in / Check-in API endpoints — /api/v1/sign/*."""

from uuid import UUID
from datetime import datetime, timezone, date, timedelta

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.daily import DailyCheckin, StreakRecord
from app.models.payment import Fragment, FragmentTransaction

router = APIRouter(prefix="/sign", tags=["sign"])

# Tiered rewards configuration
TIERED_REWARDS = {
    3: 10,   # 3 days: +10 fragments
    7: 30,   # 7 days: +30 fragments
    30: 200, # 30 days: +200 fragments
}


@router.post("/checkin")
async def checkin(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Perform daily check-in with tiered rewards (BE-FEAT-027)."""
    uid = UUID(user_id)
    today = date.today()

    # Check if already checked in today
    today_stmt = select(DailyCheckin).where(
        DailyCheckin.user_id == uid,
        DailyCheckin.date == today,
    )
    today_result = await db.execute(today_stmt)
    if today_result.scalar_one_or_none():
        raise AppException(
            error_code="ALREADY_CHECKED_IN",
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Already checked in today",
        )

    # Get or create streak record
    streak_stmt = select(StreakRecord).where(StreakRecord.user_id == uid)
    streak_result = await db.execute(streak_stmt)
    streak = streak_result.scalar_one_or_none()

    if not streak:
        # First check-in
        streak = StreakRecord(user_id=uid, current_streak=0, max_streak=0)
        db.add(streak)
        await db.flush()

    # Update streak
    yesterday = today - timedelta(days=1)
    if streak.last_checkin_date == yesterday:
        # Continue streak
        streak.current_streak += 1
    else:
        # Reset streak (missed a day)
        streak.current_streak = 1

    streak.last_checkin_date = today
    if streak.current_streak > streak.max_streak:
        streak.max_streak = streak.current_streak

    # Create check-in record
    checkin_record = DailyCheckin(user_id=uid, date=today)
    db.add(checkin_record)

    # Calculate tiered reward
    base_reward = 10
    tiered_reward = TIERED_REWARDS.get(streak.current_streak, 0)
    total_reward = base_reward + tiered_reward

    # Award fragments
    frag_stmt = select(Fragment).where(Fragment.user_id == uid)
    frag_result = await db.execute(frag_stmt)
    fragment = frag_result.scalar_one_or_none()

    if fragment:
        fragment.balance += total_reward
    else:
        fragment = Fragment(user_id=uid, balance=total_reward)
        db.add(fragment)

    # CR-018 T-010: Create FragmentTransaction record for sign/checkin
    # This is required so /sign/info can compute total_fragments correctly
    checkin_txn = FragmentTransaction(
        user_id=uid,
        amount=total_reward,
        reason="daily_checkin"
    )
    db.add(checkin_txn)

    await db.commit()

    return {
        "status": "success",
        "streak_days": streak.current_streak,
        "reward": total_reward,
        "base_reward": base_reward,
        "tiered_reward": tiered_reward,
        "message": f"签到成功！连续签到 {streak.current_streak} 天，获得 {total_reward} 碎片",
    }


@router.get("/info")
async def get_sign_info(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get check-in info for personal center."""
    uid = UUID(user_id)
    today = date.today()

    # Check if checked in today
    today_stmt = select(func.count()).select_from(DailyCheckin).where(
        DailyCheckin.user_id == uid,
        DailyCheckin.date == today,
    )
    today_result = await db.execute(today_stmt)
    checked_in_today = (today_result.scalar() or 0) > 0

    # Get streak record
    streak_stmt = select(StreakRecord).where(StreakRecord.user_id == uid)
    streak_result = await db.execute(streak_stmt)
    streak = streak_result.scalar_one_or_none()

    streak_days = streak.current_streak if streak else 0

    # Get total check-ins
    total_stmt = select(func.count()).select_from(DailyCheckin).where(
        DailyCheckin.user_id == uid
    )
    total_result = await db.execute(total_stmt)
    total_checkins = total_result.scalar() or 0

    # Build this_week array (Monday to Sunday)
    # Find the Monday of this week
    monday = today - timedelta(days=today.weekday())
    this_week = []
    for i in range(7):
        day = monday + timedelta(days=i)
        day_stmt = select(func.count()).select_from(DailyCheckin).where(
            DailyCheckin.user_id == uid,
            DailyCheckin.date == day,
        )
        day_result = await db.execute(day_stmt)
        this_week.append((day_result.scalar() or 0) > 0)

    # Next milestone
    milestones = [
        (3, "fragment", 10),
        (7, "fragment", 30),
        (30, "fragment", 200),
    ]
    next_milestone = None
    for days, reward_type, reward_amount in milestones:
        if streak_days < days:
            next_milestone = {
                "days": days,
                "reward_type": reward_type,
                "reward_amount": reward_amount,
            }
            break

    # Get current fragment balance (consistent with /gift endpoint)
    frag_stmt = select(Fragment).where(Fragment.user_id == uid)
    frag_result = await db.execute(frag_stmt)
    fragment = frag_result.scalar_one_or_none()
    total_fragments = fragment.balance if fragment else 0

    return {
        "checked_in_today": checked_in_today,
        "streak_days": streak_days,
        "total_checkins": total_checkins,
        "total_fragments": total_fragments,
        "this_week": this_week,
        "next_milestone": next_milestone,
    }
