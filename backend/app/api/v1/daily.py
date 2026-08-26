"""Daily check-in API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date
from uuid import UUID

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.daily import DailyCheckin, StreakRecord
from app.models.payment import Fragment, FragmentTransaction

# 每日签到基础奖励（按连续签到天数分段）
DAILY_BASE_REWARDS = [
    (1, 6, 2),     # Day 1-6: 2碎片/天
    (7, 13, 3),    # Day 7-13: 3碎片/天
    (14, 29, 5),   # Day 14-29: 5碎片/天
    (30, 9999, 8), # Day 30+: 8碎片/天
]

# 里程碑奖励（Day 3/7/14/30）
STREAK_MILESTONES = {
    3:  {"type": "fragment", "amount": 10,  "special": None,              "title": "三日之约", "description": "连续签到 3 天 +10 碎片"},
    7:  {"type": "fragment", "amount": 20,  "special": "hidden_dialogue", "title": "七日之约", "description": "连续签到 7 天 +20 碎片 + 隐藏对话解锁"},
    14: {"type": "fragment", "amount": 30,  "special": "cg_rare",         "title": "两周之约", "description": "连续签到 14 天 +30 碎片 + 稀有CG解锁 + 角色好感度+5"},
    30: {"type": "fragment", "amount": 50,  "special": "cg_exclusive",    "title": "月满之约", "description": "连续签到 30 天 +50 碎片 + 独占CG解锁 + 成就 Day 30 Streak"},
}


def get_daily_base_reward(streak_days: int) -> int:
    """根据连续签到天数返回当日基础碎片奖励"""
    for start, end, amount in DAILY_BASE_REWARDS:
        if start <= streak_days <= end:
            return amount
    return 8  # 默认 Day 30+

router = APIRouter(prefix="/daily", tags=["daily"])


@router.post("/checkin")
async def checkin(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Perform daily check-in. Returns 409 if already checked in today."""
    uid = UUID(user_id)
    today = date.today()

    # Check if already checked in today
    stmt = select(DailyCheckin).where(
        DailyCheckin.user_id == uid,
        DailyCheckin.date == today,
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise AppException(ErrorCode.DAILY_ALREADY_CHECKED_IN, 409, "Already checked in today")

    # Create check-in record
    checkin_record = DailyCheckin(
        user_id=uid,
        date=today,
    )
    db.add(checkin_record)

    # Update or create streak record
    streak_stmt = select(StreakRecord).where(StreakRecord.user_id == uid)
    streak_result = await db.execute(streak_stmt)
    streak = streak_result.scalar_one_or_none()

    yesterday = date.fromordinal(today.toordinal() - 1)
    if streak:
        if streak.last_checkin_date == yesterday:
            streak.current_streak += 1
        elif streak.last_checkin_date != today:
            streak.current_streak = 1
        if streak.current_streak > streak.max_streak:
            streak.max_streak = streak.current_streak
        streak.last_checkin_date = today
    else:
        streak = StreakRecord(
            user_id=uid,
            current_streak=1,
            max_streak=1,
            last_checkin_date=today,
        )
        db.add(streak)

    await db.commit()

    # AC-028: Check if current streak hits a milestone
    milestone_reward = None
    if streak.current_streak in STREAK_MILESTONES:
        m = STREAK_MILESTONES[streak.current_streak]
        milestone_reward = {
            "milestone_day": streak.current_streak,
            "title": m["title"],
            "description": m["description"],
            "reward": {"type": m["type"], "amount": m["amount"]},
            "special_item": m["special"],
        }
        # Grant fragment reward
        frag_stmt = select(Fragment).where(Fragment.user_id == uid)
        frag_result = await db.execute(frag_stmt)
        frag = frag_result.scalar_one_or_none()
        if frag:
            frag.balance += m["amount"]
        else:
            frag = Fragment(user_id=uid, balance=m["amount"])
            db.add(frag)
        
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
    
    # Grant fragments
    frag_stmt = select(Fragment).where(Fragment.user_id == uid)
    frag_result = await db.execute(frag_stmt)
    frag = frag_result.scalar_one_or_none()
    if frag:
        frag.balance += fragments_earned
    else:
        frag = Fragment(user_id=uid, balance=fragments_earned)
        db.add(frag)
    
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
        "status": "ok",
        "fragments_earned": fragments_earned,
        "streak_days": streak.current_streak,
        "message": message,
    }


DAILY_TASKS = [
    {
        "id": "task_dialogue",
        "title": "完成 3 次对话",
        "description": "与角色进行 3 次对话",
        "progress": 3,
        "target": 3,
        "completed": True,
        "reward": {"type": "fragment", "amount": 10},
    },
    {
        "id": "task_choice",
        "title": "做出 5 次选择",
        "description": "在对话中做出 5 次选择",
        "progress": 5,
        "target": 5,
        "completed": True,
        "reward": {"type": "fragment", "amount": 10},
    },
    {
        "id": "task_profile",
        "title": "查看角色信息",
        "description": "查看任意角色的详细信息",
        "progress": 1,
        "target": 1,
        "completed": True,
        "reward": {"type": "fragment", "amount": 5},
    },
]


@router.get("/tasks")
async def get_tasks(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get daily tasks with progress. Tasks reset at UTC 0:00."""
    uid = UUID(user_id)
    today = date.today()

    # Check if we already have today's tasks
    stmt = select(DailyCheckin).where(
        DailyCheckin.user_id == uid,
        DailyCheckin.date == today,
    )
    result = await db.execute(stmt)
    checkin = result.scalar_one_or_none()

    # Return mock tasks (in production, read from task_progress table)
    all_completed = checkin is not None
    tasks = []
    for t in DAILY_TASKS:
        task = dict(t)
        if not all_completed:
            task["progress"] = 0
            task["completed"] = False
        tasks.append(task)

    total = len(tasks)
    completed = sum(1 for t in tasks if t["completed"])

    return {
        "tasks": tasks,
        "total": total,
        "completed": completed,
        "all_completed": completed == total,
        "reset_at": "UTC 00:00",
    }


@router.get("/stats")
async def get_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get daily check-in statistics."""
    uid = UUID(user_id)
    today = date.today()

    # Check today's check-in
    stmt = select(DailyCheckin).where(
        DailyCheckin.user_id == uid,
        DailyCheckin.date == today,
    )
    result = await db.execute(stmt)
    today_record = result.scalar_one_or_none()

    # Get streak record
    streak_stmt = select(StreakRecord).where(StreakRecord.user_id == uid)
    streak_result = await db.execute(streak_stmt)
    streak = streak_result.scalar_one_or_none()

    # Total check-in days
    total_stmt = select(func.count(DailyCheckin.id)).where(
        DailyCheckin.user_id == uid,
    )
    total_result = await db.execute(total_stmt)
    total_days = total_result.scalar() or 0

    return {
        "current_streak": streak.current_streak if streak else 0,
        "longest_streak": streak.max_streak if streak else 0,
        "total_days": total_days,
        "today_checked_in": today_record is not None,
    }
