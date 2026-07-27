"""CR3-014: Ending progress and completion statistics API."""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.game import GameSession
from app.models.script import Script, Route


router = APIRouter(prefix="/ending-progress", tags=["ending-progress"])


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────


async def _count_endings_for_route(route_id: uuid.UUID, db: AsyncSession) -> int:
    """Count distinct ending types achieved for a route."""
    stmt = (
        select(func.count(func.distinct(GameSession.ending_type)))
        .where(
            GameSession.route_id == route_id,
            GameSession.ending_type.isnot(None),
        )
    )
    result = await db.execute(stmt)
    return result.scalar() or 0


async def _total_endings_for_route(route_id: uuid.UUID, db: AsyncSession) -> int:
    """Estimate total endings for a route.
    MVP: use a fixed estimate of 3 endings per route (good/neutral/bad).
    In production, this would come from a route_endings config table.
    """
    return 3


# ──────────────────────────────────────────────
# CR3-014: Ending progress per script
# ──────────────────────────────────────────────


@router.get("/scripts/{script_id}")
async def get_script_ending_progress(
    script_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-014: Get ending completion progress for a specific script.
    """
    try:
        sid = uuid.UUID(script_id)
        uid = uuid.UUID(user_id)
    except ValueError:
        raise AppException(ErrorCode.INVALID_CHARACTER_ID, 400, "Invalid script_id format")

    # Load script
    script_result = await db.execute(select(Script).where(Script.id == sid))
    script = script_result.scalar_one_or_none()
    if not script:
        raise AppException(ErrorCode.SAVE_NOT_FOUND, 404, "Script not found")

    # Load routes for this script
    routes_result = await db.execute(
        select(Route).where(Route.script_id == sid)
    )
    routes = list(routes_result.scalars().all())

    route_progress = []
    total_achieved = 0
    total_possible = 0

    for route in routes:
        achieved = await _count_endings_for_route(route.id, db)
        possible = await _total_endings_for_route(route.id, db)
        total_achieved += achieved
        total_possible += possible

        route_progress.append({
            "route_id": str(route.id),
            "route_title": route.title,
            "endings_achieved": achieved,
            "endings_total": possible,
            "completion_pct": round(achieved / possible * 100, 1) if possible > 0 else 0,
        })

    return {
        "script_id": script_id,
        "script_title": script.title,
        "routes": route_progress,
        "total_achieved": total_achieved,
        "total_possible": total_possible,
        "overall_completion_pct": round(total_achieved / total_possible * 100, 1)
        if total_possible > 0
        else 0,
    }


@router.get("/summary")
async def get_ending_progress_summary(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-014: Get overall ending progress summary across all scripts.
    """
    uid = uuid.UUID(user_id)

    # Count completed sessions by script
    completed_result = await db.execute(
        select(GameSession.script_id, func.count(GameSession.id))
        .where(
            GameSession.user_id == uid,
            GameSession.ending_type.isnot(None),
        )
        .group_by(GameSession.script_id)
    )
    completed_by_script = dict(completed_result.all())

    # Count total sessions by script
    total_result = await db.execute(
        select(GameSession.script_id, func.count(GameSession.id))
        .where(GameSession.user_id == uid)
        .group_by(GameSession.script_id)
    )
    total_by_script = dict(total_result.all())

    # Load all scripts user has played
    played_ids = list(set(list(completed_by_script.keys()) + list(total_by_script.keys())))
    scripts = []
    if played_ids:
        scripts_result = await db.execute(
            select(Script).where(Script.id.in_(played_ids))
        )
        scripts = list(scripts_result.scalars().all())

    script_summaries = []
    for s in scripts:
        script_summaries.append({
            "script_id": str(s.id),
            "title": s.title,
            "sessions_completed": completed_by_script.get(s.id, 0),
            "sessions_total": total_by_script.get(s.id, 0),
        })

    return {
        "scripts_played": len(scripts),
        "total_completed_sessions": sum(completed_by_script.values()),
        "total_sessions": sum(total_by_script.values()),
        "scripts": script_summaries,
    }
