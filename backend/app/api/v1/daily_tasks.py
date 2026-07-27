"""CR3-023: Extended daily task API with progress tracking and claim.

Extends the existing /daily/tasks endpoint with:
- Progress update API (called by game engine)
- Task completion check
- Reward claim API
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
from app.models.payment import Fragment, FragmentTransaction


router = APIRouter(prefix="/daily-tasks", tags=["daily-tasks"])


# ──────────────────────────────────────────────
# Task Definitions (MVP: hardcoded for today)
# ──────────────────────────────────────────────

TASK_DEFINITIONS = {
    "task_dialogue": {
        "id": "task_dialogue",
        "title": "完成 3 次对话",
        "description": "与角色进行 3 次对话",
        "target": 3,
        "reward_type": "fragments",
        "reward_amount": 10,
    },
    "task_choice": {
        "id": "task_choice",
        "title": "做出 5 次选择",
        "description": "在对话中做出 5 次选择",
        "target": 5,
        "reward_type": "fragments",
        "reward_amount": 10,
    },
    "task_profile": {
        "id": "task_profile",
        "title": "查看角色信息",
        "description": "查看任意角色的详细信息",
        "target": 1,
        "reward_type": "fragments",
        "reward_amount": 5,
    },
}


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
    """
    uid = uuid.UUID(user_id)
    today = date.today()

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

    return {
        "tasks": tasks,
        "total": len(tasks),
        "completed": completed_count,
        "claimed": claimed_count,
        "reset_at": "UTC 00:00",
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
    """
    uid = uuid.UUID(user_id)
    today = date.today()
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
    """
    uid = uuid.UUID(user_id)
    today = date.today()
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
