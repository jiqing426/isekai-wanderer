"""Recap API endpoints (CR3-053 / AC-GAME-012).

GET /recap/{session_id} — returns adventure recap data
"""

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.services.recap_service import RecapService

router = APIRouter(prefix="/recap", tags=["recap"])


@router.get("/{session_id}")
async def get_recap(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Get adventure recap for a session.

    Returns key choices, AI summary, ending info, duration.
    """
    try:
        sid = UUID(session_id)
        uid = UUID(user_id)
    except ValueError:
        raise AppException(ErrorCode.INVALID_REQUEST, 400, "Invalid UUID format")

    svc = RecapService(db)
    recap = await svc.generate_recap(sid, uid)

    if "error" in recap:
        if recap["error"] == "Access denied":
            raise AppException(ErrorCode.ACCESS_DENIED, 403, recap["error"])
        raise AppException(ErrorCode.NOT_FOUND, 404, recap["error"])

    return recap
