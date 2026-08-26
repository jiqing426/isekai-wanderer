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

# 每日签到基础奖励（按连续签到天数分段）
DAILY_BASE_REWARDS = [
    (1, 6, 2),     # Day 1-6: 2碎片/天
    (7, 13, 3),    # Day 7-13: 3碎片/天
    (14, 29, 5),   # Day 14-29: 5碎片/天
    (30, 9999, 8), # Day 30+: 8碎片/天
]

# 里程碑奖励（Day 3/7/14/30）
STREAK_MILESTONES = {
    3:  {"amount": 10, "special": None,              "title": "三日之约", "description": "连续签到 3 天 +10 碎片"},
    7:  {"amount": 20, "special": "hidden_dialogue", "title": "七日之约", "description": "连续签到 7 天 +20 碎片 + 隐藏对话解锁"},
    14: {"amount": 30, "special": "cg_rare",         "title": "两周之约", "description": "连续签到 14 天 +30 碎片 + 稀有CG解锁 + 角色好感度+5"},
    30: {"amount": 50, "special": "cg_exclusive",    "title": "月满之约", "description": "连续签到 30 天 +50 碎片 + 独占CG解锁 + 成就 Day 30 Streak"},
}


def get_daily_base_reward(streak_days: int) -> int:
    """根据连续签到天数返回当日基础碎片奖励"""
    for start, end, amount in DAILY_BASE_REWARDS:
        if start <= streak_days <= end:
            return amount
    return 8  # 默认 Day 30+


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

    await db.commit()

    # Check if current streak hits a milestone
    milestone_reward = None
    if streak.current_streak in STREAK_MILESTONES:
        m = STREAK_MILESTONES[streak.current_streak]
        milestone_reward = {
            "milestone_day": streak.current_streak,
            "title": m["title"],
            "description": m["description"],
            "reward": {"type": "fragment", "amount": m["amount"]},
            "special_item": m["special"],
        }
        # Grant milestone fragment reward
        frag_stmt = select(Fragment).where(Fragment.user_id == uid)
        frag_result = await db.execute(frag_stmt)
        fragment = frag_result.scalar_one_or_none()
        if fragment:
            fragment.balance += m["amount"]
        else:
            fragment = Fragment(user_id=uid, balance=m["amount"])
            db.add(fragment)
        
        # Create transaction record for milestone reward
        milestone_txn = FragmentTransaction(
            user_id=uid,
            amount=m["amount"],
            reason=f"streak_milestone_day_{streak.current_streak}"
        )
        db.add(milestone_txn)
        await db.commit()

    # Calculate fragments earned (按分段规则)
    fragments_earned = get_daily_base_reward(streak.current_streak)
    
    # Grant daily base fragments
    frag_stmt = select(Fragment).where(Fragment.user_id == uid)
    frag_result = await db.execute(frag_stmt)
    fragment = frag_result.scalar_one_or_none()
    if fragment:
        fragment.balance += fragments_earned
    else:
        fragment = Fragment(user_id=uid, balance=fragments_earned)
        db.add(fragment)
    
    # Create transaction record for daily check-in
    checkin_txn = FragmentTransaction(
        user_id=uid,
        amount=fragments_earned,
        reason="daily_checkin"
    )
    db.add(checkin_txn)
    await db.commit()

    # Build message
    message = f"签到成功！获得 {fragments_earned} 碎片"
    if streak.current_streak > 1:
        message += f"，连续签到 {streak.current_streak} 天"

    return {
        "status": "success",
        "streak_days": streak.current_streak,
        "fragments_earned": fragments_earned,
        "milestone": milestone_reward,
        "message": message,
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
    next_milestone = None
    for days, m in sorted(STREAK_MILESTONES.items()):
        if streak_days < days:
            next_milestone = {
                "days": days,
                "reward_type": "fragment",
                "reward_amount": m["amount"],
                "title": m["title"],
                "description": m["description"],
            }
            break

    # Get current fragment balance (consistent with /gift endpoint)
    frag_stmt = select(Fragment).where(Fragment.user_id == uid)
    frag_result = await db.execute(frag_stmt)
    fragment = frag_result.scalar_one_or_none()
    current_balance = fragment.balance if fragment else 0

    # Calculate total fragments earned from check-ins (not current balance)
    # Sum all check-in related transactions (daily_checkin + streak_milestone)
    total_earned_stmt = select(func.sum(FragmentTransaction.amount)).where(
        FragmentTransaction.user_id == uid,
        FragmentTransaction.reason.like('%checkin%')
    )
    milestone_earned_stmt = select(func.sum(FragmentTransaction.amount)).where(
        FragmentTransaction.user_id == uid,
        FragmentTransaction.reason.like('%milestone%')
    )
    total_earned_result = await db.execute(total_earned_stmt)
    milestone_earned_result = await db.execute(milestone_earned_stmt)
    total_fragments = (total_earned_result.scalar() or 0) + (milestone_earned_result.scalar() or 0)

    return {
        "checked_in_today": checked_in_today,
        "streak_days": streak_days,
        "total_checkins": total_checkins,
        "total_fragments": total_fragments,
        "this_week": this_week,
        "next_milestone": next_milestone,
    }
