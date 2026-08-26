"""CR3-012/013: Save snapshot and fork API endpoints."""

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.save import SaveSnapshot
from app.models.game import GameSession


router = APIRouter(prefix="/saves", tags=["saves"])


# ──────────────────────────────────────────────
# Schemas
# ──────────────────────────────────────────────


class SnapshotCreateRequest(BaseModel):
    label: Optional[str] = None


class ForkRequest(BaseModel):
    snapshot_id: str
    custom_name: Optional[str] = None


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────


def _snapshot_to_card(snap: SaveSnapshot, session: GameSession = None) -> dict:
    """Convert snapshot to card response.
    
    CR-028: Include character info from associated GameSession if available.
    """
    card = {
        "id": str(snap.id),
        "session_id": str(snap.session_id),
        "label": snap.label or f"Auto Save {snap.created_at.strftime('%Y-%m-%d %H:%M')}",
        "current_node_id": str(snap.current_node_id) if snap.current_node_id else None,
        "choice_count": len(snap.choice_history) if snap.choice_history else 0,
        "created_at": snap.created_at.isoformat() if snap.created_at else None,
    }
    
    # CR-028: Add character info from GameSession
    if session:
        card["character_id"] = str(session.character_id) if session.character_id else None
        card["character_name"] = session.character_name or "默认角色"
    else:
        card["character_id"] = None
        card["character_name"] = "默认角色"
    
    return card


# ──────────────────────────────────────────────
# CR3-012: List save snapshots
# ──────────────────────────────────────────────


@router.get("")
async def list_snapshots(
    limit: int = 50,
    offset: int = 0,
    character_id: Optional[str] = None,  # CR-028: Filter by character
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-012: List user's save snapshots.
    CR-028: Support filtering by character_id.
    """
    uid = uuid.UUID(user_id)
    
    # Build base query
    base_query = select(SaveSnapshot).where(SaveSnapshot.user_id == uid)
    
    # CR-028: Filter by character_id if provided
    if character_id:
        try:
            char_uuid = uuid.UUID(character_id)
        except ValueError:
            raise AppException(ErrorCode.INVALID_CHARACTER_ID, 400, "Invalid character_id format")
        
        # Join with GameSession to filter by character_id
        base_query = (
            base_query
            .join(GameSession, SaveSnapshot.session_id == GameSession.id)
            .where(GameSession.character_id == char_uuid)
        )
    
    # Total count — must use the same filtered base_query so total reflects
    # the character_id filter when provided (BUG-001 fix).
    # Use func.count() (no column arg) to avoid cartesian product with JOIN columns.
    count_query = select(func.count()).select_from(base_query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0
    
    stmt = (
        base_query
        .order_by(SaveSnapshot.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    snapshots = list(result.scalars().all())
    
    # CR-028: Load associated GameSessions for character info
    session_ids = [snap.session_id for snap in snapshots]
    sessions = {}
    if session_ids:
        session_result = await db.execute(
            select(GameSession).where(GameSession.id.in_(session_ids))
        )
        for session in session_result.scalars().all():
            sessions[session.id] = session
    
    return {
        "snapshots": [_snapshot_to_card(s, sessions.get(s.session_id)) for s in snapshots],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("")
async def create_snapshot(
    request: SnapshotCreateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-012: Create a new save snapshot from the user's active session.
    """
    uid = uuid.UUID(user_id)

    # Find active session
    active_result = await db.execute(
        select(GameSession)
        .where(GameSession.user_id == uid, GameSession.status == "active")
        .order_by(GameSession.started_at.desc())
        .limit(1)
    )
    session = active_result.scalar_one_or_none()
    if not session:
        raise AppException(
            ErrorCode.SAVE_SESSION_NOT_FOUND,
            404,
            "No active game session to snapshot",
        )

    snapshot = SaveSnapshot(
        user_id=uid,
        session_id=session.id,
        label=request.label,
        choice_history=session.choice_history or [],
        current_node_id=session.current_node_id,
        metadata_json={"session_status": session.status},
    )
    db.add(snapshot)
    await db.commit()
    await db.refresh(snapshot)

    # BUG-002 fix: pass session so character_id / character_name are populated
    return {"snapshot": _snapshot_to_card(snapshot, session)}


@router.delete("/{snapshot_id}")
async def delete_snapshot(
    snapshot_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-012: Delete a save snapshot (owner only).
    """
    try:
        sid = uuid.UUID(snapshot_id)
        uid = uuid.UUID(user_id)
    except ValueError:
        raise AppException(ErrorCode.SAVE_NOT_FOUND, 400, "Invalid snapshot_id format")

    result = await db.execute(
        select(SaveSnapshot).where(
            SaveSnapshot.id == sid, SaveSnapshot.user_id == uid
        )
    )
    snapshot = result.scalar_one_or_none()
    if not snapshot:
        raise AppException(ErrorCode.SAVE_NOT_FOUND, 404, "Snapshot not found")

    await db.delete(snapshot)
    await db.commit()
    return {"deleted": True, "snapshot_id": snapshot_id}


# ──────────────────────────────────────────────
# CR3-013: Fork from snapshot
# ──────────────────────────────────────────────


@router.post("/fork")
async def fork_session(
    request: ForkRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-013: Create a new game session by forking from a save snapshot.
    """
    try:
        snap_id = uuid.UUID(request.snapshot_id)
        uid = uuid.UUID(user_id)
    except ValueError:
        raise AppException(ErrorCode.SAVE_NOT_FOUND, 400, "Invalid snapshot_id format")

    # Load snapshot
    snap_result = await db.execute(
        select(SaveSnapshot).where(
            SaveSnapshot.id == snap_id, SaveSnapshot.user_id == uid
        )
    )
    snapshot = snap_result.scalar_one_or_none()
    if not snapshot:
        raise AppException(ErrorCode.SAVE_NOT_FOUND, 404, "Snapshot not found")

    # Load original session for script/route context
    orig_result = await db.execute(
        select(GameSession).where(GameSession.id == snapshot.session_id)
    )
    orig_session = orig_result.scalar_one_or_none()
    if not orig_session:
        raise AppException(
            ErrorCode.SAVE_SESSION_NOT_FOUND,
            404,
            "Original session for this snapshot no longer exists",
        )

    # Create forked session
    forked = GameSession(
        user_id=uid,
        script_id=orig_session.script_id,
        route_id=orig_session.route_id,
        current_node_id=snapshot.current_node_id,
        status="active",
        custom_name=request.custom_name or f"Fork from {snapshot.label or snap_id}",
        choice_history=snapshot.choice_history or [],
        metadata_json={"forked_from_snapshot": str(snap_id)},
    )
    db.add(forked)
    await db.commit()
    await db.refresh(forked)

    return {
        "forked_session_id": str(forked.id),
        "from_snapshot_id": request.snapshot_id,
        "script_id": str(orig_session.script_id),
        "route_id": str(orig_session.route_id),
        "current_node_id": str(forked.current_node_id) if forked.current_node_id else None,
        "status": forked.status,
    }
