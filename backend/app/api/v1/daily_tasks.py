"""S017: Daily task API with progress tracking and claim.

Daily tasks reset at Beijing time (UTC+8) 00:00.
"""

import uuid
from datetime import datetime, date, timezone, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.daily import DailyTask
from app.models.payment import Fragment, FragmentTransaction


router = APIRouter(prefix="/daily-tasks", tags=["daily-tasks"])


# ──────────────────────────────────────────────
# Task Definitions (S017)
# ──────────────────────────────────────────────

TASK_DEFINITIONS = {
    "task_dialogue": {
        "id": "task_dialogue",
        "title": "💬 对话达人",
        "description": "完成1次对话",
        "icon": "💬",
        "target": 1,
        "reward_type": "fragments",
        "reward_amount": 3,
    },
    "task_choice": {
        "id": "task_choice",
        "title": "🎯 选择大师",
        "description": "做出1次选择",
        "icon": "🎯",
        "target": 1,
        "reward_type": "fragments",
        "reward_amount": 3,
    },
    "task_profile": {
        "id": "task_profile",
        "title": "👤 角色探索",
        "description": "查看1个角色档案",
        "icon": "👤",
        "target": 1,
        "reward_type": "fragments",
        "reward_amount": 2,
    },
}

# 全完成额外奖励
ALL_COMPLETE_BONUS = 5


def get_beijing_today() -> date:
    """获取北京时间的今天日期"""
    beijing_tz = timezone(timedelta(hours=8))
    return datetime.now(beijing_tz).date()


# ──────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────


class ProgressUpdateRequest(BaseModel):
    task_type: str
    increment: int = 1


class ClaimTaskRequest(BaseModel):
    task_type: str


# ──────────────────────────────────────────────
# CR3-023: List tasks with progress
# ──────────────────────────────────────────────


@router.get("")
async def list_daily_tasks(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-023: List daily tasks with progress for today.
    Auto-creates task records if not exist.
    S017: Uses Beijing time (UTC+8) for date calculation.
    """
    uid = uuid.UUID(user_id)
    today = get_beijing_today()

    # Get or create today's tasks
    result = await db.execute(
        select(DailyTask).where(
            DailyTask.user_id == uid,
            DailyTask.date == today,
        )
    )
    existing = {t.task_type: t for t in result.scalars().all()}

    tasks = []
    for task_id, defn in TASK_DEFINITIONS.items():
        task = existing.get(task_id)
        if not task:
            # Auto-create
            task = DailyTask(
                user_id=uid,
                date=today,
                task_type=task_id,
                progress=0,
                target=defn["target"],
                completed=False,
                claimed=False,
            )
            db.add(task)
            await db.flush()

        tasks.append({
            "id": task_id,
            "title": defn["title"],
            "description": defn["description"],
            "progress": task.progress,
            "target": task.target,
            "completed": task.completed,
            "claimed": task.claimed,
            "reward_type": defn["reward_type"],
            "reward_amount": defn["reward_amount"],
        })

    await db.commit()

    completed_count = sum(1 for t in tasks if t["completed"])
    claimed_count = sum(1 for t in tasks if t["claimed"])
    
    # 检查全完成奖励是否已领取
    all_complete_reason = "task_claim:all_complete"
    bonus_result = await db.execute(
        select(FragmentTransaction).where(
            FragmentTransaction.user_id == uid,
            FragmentTransaction.reason == all_complete_reason,
            func.date(FragmentTransaction.created_at) == today,
        )
    )
    all_complete_claimed = bonus_result.scalar_one_or_none() is not None

    return {
        "tasks": tasks,
        "total": len(tasks),
        "completed": completed_count,
        "claimed": claimed_count,
        "all_completed": completed_count == 3,
        "all_claimed": claimed_count == 3,
        "all_complete_claimed": all_complete_claimed,
        "reset_at": "北京时间 00:00",
    }


# ──────────────────────────────────────────────
# CR3-023: Update task progress
# ──────────────────────────────────────────────


@router.post("/progress")
async def update_progress(
    request: ProgressUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-023: Update task progress. Called by game engine when action occurs.
    Auto-marks task as completed when progress >= target.
    S017: Uses Beijing time (UTC+8) for date calculation.
    """
    uid = uuid.UUID(user_id)
    today = get_beijing_today()
    task_type = request.task_type

    if task_type not in TASK_DEFINITIONS:
        raise AppException(
            ErrorCode.TASK_NOT_FOUND,
            404,
            f"Task '{task_type}' not defined",
        )

    # Get or create task
    result = await db.execute(
        select(DailyTask).where(
            DailyTask.user_id == uid,
            DailyTask.date == today,
            DailyTask.task_type == task_type,
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        defn = TASK_DEFINITIONS[task_type]
        task = DailyTask(
            user_id=uid,
            date=today,
            task_type=task_type,
            progress=0,
            target=defn["target"],
            completed=False,
            claimed=False,
        )
        db.add(task)

    # Increment progress
    task.progress += request.increment
    if task.progress >= task.target:
        task.completed = True

    await db.commit()
    await db.refresh(task)

    defn = TASK_DEFINITIONS[task_type]
    return {
        "task_type": task_type,
        "progress": task.progress,
        "target": task.target,
        "completed": task.completed,
        "claimed": task.claimed,
        "reward_type": defn["reward_type"],
        "reward_amount": defn["reward_amount"],
    }


# ──────────────────────────────────────────────
# CR3-023: Claim task reward
# ──────────────────────────────────────────────


@router.post("/claim")
async def claim_task(
    request: ClaimTaskRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-023: Claim reward for completed task.
    Returns 400 if not completed, 409 if already claimed.
    S017: Uses Beijing time (UTC+8) for date calculation.
    """
    uid = uuid.UUID(user_id)
    today = get_beijing_today()
    task_type = request.task_type

    if task_type not in TASK_DEFINITIONS:
        raise AppException(
            ErrorCode.TASK_NOT_FOUND,
            404,
            f"Task '{task_type}' not defined",
        )

    # Get task
    result = await db.execute(
        select(DailyTask).where(
            DailyTask.user_id == uid,
            DailyTask.date == today,
            DailyTask.task_type == task_type,
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise AppException(
            ErrorCode.TASK_NOT_FOUND,
            404,
            f"Task '{task_type}' not found for today",
        )

    if not task.completed:
        raise AppException(
            ErrorCode.TASK_NOT_COMPLETED,
            400,
            f"Task '{task_type}' not yet completed",
        )

    if task.claimed:
        raise AppException(
            ErrorCode.TASK_ALREADY_CLAIMED,
            409,
            f"Task '{task_type}' reward already claimed",
        )

    defn = TASK_DEFINITIONS[task_type]
    reward_amount = defn["reward_amount"]

    # Mark claimed
    task.claimed = True

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
        reason=f"task_claim:{task_type}",
    )
    db.add(tx)

    await db.commit()

    return {
        "task_type": task_type,
        "claimed": True,
        "reward": {"type": defn["reward_type"], "amount": reward_amount},
    }


# ──────────────────────────────────────────────
# S017: Claim all-complete bonus
# ──────────────────────────────────────────────


@router.post("/claim-all")
async def claim_all_tasks(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    S017: 领取全完成奖励 — 3个任务全部完成时，额外+5碎片。
    不可重复领取。
    """
    uid = uuid.UUID(user_id)
    today = get_beijing_today()

    # 检查今日3个任务是否全部完成
    result = await db.execute(
        select(DailyTask).where(
            DailyTask.user_id == uid,
            DailyTask.date == today,
        )
    )
    tasks = result.scalars().all()
    task_map = {t.task_type: t for t in tasks}

    # 确保3个任务都存在且已完成
    for task_id in TASK_DEFINITIONS:
        task = task_map.get(task_id)
        if not task or not task.completed:
            raise AppException(
                ErrorCode.TASK_NOT_COMPLETED,
                400,
                "Not all tasks are completed yet",
            )

    # 检查是否已领取过（用 FragmentTransaction reason 判断）
    all_complete_reason = "task_claim:all_complete"
    bonus_result = await db.execute(
        select(FragmentTransaction).where(
            FragmentTransaction.user_id == uid,
            FragmentTransaction.reason == all_complete_reason,
            func.date(FragmentTransaction.created_at) == today,
        )
    )
    if bonus_result.scalar_one_or_none() is not None:
        raise AppException(
            ErrorCode.TASK_ALREADY_CLAIMED,
            409,
            "All-complete bonus already claimed today",
        )

    # 发放5碎片
    frag_result = await db.execute(
        select(Fragment).where(Fragment.user_id == uid)
    )
    frag = frag_result.scalar_one_or_none()
    if frag:
        frag.balance += ALL_COMPLETE_BONUS
    else:
        frag = Fragment(user_id=uid, balance=ALL_COMPLETE_BONUS)
        db.add(frag)

    # 记录交易
    tx = FragmentTransaction(
        user_id=uid,
        amount=ALL_COMPLETE_BONUS,
        reason=all_complete_reason,
    )
    db.add(tx)

    await db.commit()

    return {
        "claimed": True,
        "reward": ALL_COMPLETE_BONUS,
    }
