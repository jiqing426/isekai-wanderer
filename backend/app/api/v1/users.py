"""Users API endpoints — /api/v1/users/me/* series.

All endpoints require Bearer token authentication.
"""

import os
import uuid
from pathlib import Path
from uuid import UUID
from datetime import datetime, timezone, date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, status, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.core.security import verify_password, get_password_hash
from app.api.v1.auth import get_current_user_id
from app.models.user import User
from app.models.gallery import Achievement, Collection
from app.models.payment import Fragment, FragmentTransaction
from app.models.daily import DailyCheckin, StreakRecord
from app.models.save import SaveSnapshot
from app.models.memory import CharacterMemory
from app.models.affection import Affection
from app.models.game import GameSession
from app.models.script import Script, Character, Route, Node
from app.models.user_dialogue_count import UserDialogueCount

router = APIRouter(prefix="/users/me", tags=["users"])

# Avatar upload configuration
AVATAR_BASE_URL = "http://47.107.174.176"
AVATAR_UPLOAD_DIR = Path(__file__).parent.parent.parent.parent / "static" / "avatars"
AVATAR_MAX_SIZE = 5 * 1024 * 1024  # 5MB
AVATAR_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

# Ensure upload directory exists
AVATAR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ── Request / Response Schemas ──

class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = Field(None, min_length=2, max_length=100)
    avatar_url: Optional[str] = None
    signature: Optional[str] = Field(None, max_length=200)
    locale: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


# ── Helper ──

async def _get_user(db: AsyncSession, user_id: str) -> User:
    """Fetch user by id or raise 404."""
    stmt = select(User).where(User.id == UUID(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise AppException(
            error_code=ErrorCode.USER_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            message="User not found",
        )
    return user


def _user_to_profile(user: User) -> dict:
    """Serialize user to profile response."""
    return {
        "id": str(user.id),
        "email": user.email,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "signature": user.signature,
        "email_verified": user.email_verified,
        "subscription_tier": user.subscription_tier,
        "preferred_genre": user.preferred_genre,
        "locale": user.locale,
        "onboarding_completed": user.onboarding_completed,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


# ── 1. GET /users/me ──

@router.get("")
async def get_me(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current user profile."""
    user = await _get_user(db, user_id)
    return _user_to_profile(user)


# ── 2. PATCH /users/me ──

@router.patch("")
async def update_me(
    body: ProfileUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update current user profile (partial update)."""
    user = await _get_user(db, user_id)

    if body.display_name is not None:
        user.display_name = body.display_name
    if body.avatar_url is not None:
        user.avatar_url = body.avatar_url
    if body.signature is not None:
        user.signature = body.signature
    if body.locale is not None:
        user.locale = body.locale

    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    return _user_to_profile(user)


# ── 3. POST /users/me/change-password ──

@router.post("/change-password")
async def change_password(
    body: ChangePasswordRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Change current user's password."""
    user = await _get_user(db, user_id)

    # Verify old password
    if not user.password_hash or not verify_password(body.old_password, user.password_hash):
        raise AppException(
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Current password is incorrect",
        )

    # Update password
    user.password_hash = get_password_hash(body.new_password)
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {"status": "ok", "message": "Password changed successfully"}


# ── 4. DELETE /users/me ──

@router.delete("")
async def delete_account(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete current user account (hard delete for MVP)."""
    user = await _get_user(db, user_id)
    await db.delete(user)
    await db.commit()

    return {"status": "deleted", "message": "Account deleted successfully"}


# ── 5. GET /users/me/subscription ──

@router.get("/subscription")
async def get_subscription(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's subscription status."""
    user = await _get_user(db, user_id)

    # Determine subscription status
    now = datetime.now(timezone.utc)
    sub_status = "inactive"
    if user.subscription_tier == "free":
        sub_status = "active"
    elif user.trial_started_at and user.trial_ends_at:
        if now < user.trial_ends_at:
            sub_status = "trialing"
        else:
            sub_status = "inactive"
    else:
        # Assume active for paid tiers without trial info
        sub_status = "active"

    return {
        "tier": user.subscription_tier,
        "status": sub_status,
        "trial_started_at": user.trial_started_at.isoformat() if user.trial_started_at else None,
        "trial_ends_at": user.trial_ends_at.isoformat() if user.trial_ends_at else None,
        "renew_at": None,  # Not tracked yet; placeholder for future billing integration
    }


# ── 6. GET /users/me/achievements ──

# Master achievement definitions (all possible achievements)
MASTER_ACHIEVEMENTS = [
    {
        "id": "ach_first_dialogue",
        "name": "初见",
        "description": "完成第一次对话",
        "icon": "🎭",
        "icon_url": "/assets/achievements/first_dialogue.png",
        "target": 1,
        "reward_type": "fragments",
        "reward_amount": 20,
    },
    {
        "id": "ach_bond_60",
        "name": "羁绊",
        "description": "好感度达到 60",
        "icon": "💕",
        "icon_url": "/assets/achievements/bond_60.png",
        "target": 60,
        "reward_type": "fragments",
        "reward_amount": 50,
    },
    {
        "id": "ach_explorer",
        "name": "探索者",
        "description": "完成3个剧本",
        "icon": "🗺️",
        "icon_url": "/assets/achievements/explorer.png",
        "target": 3,
        "reward_type": "fragments",
        "reward_amount": 30,
    },
    {
        "id": "ach_collector",
        "name": "收藏家",
        "description": "收集10个CG",
        "icon": "📸",
        "icon_url": "/assets/achievements/collector.png",
        "target": 10,
        "reward_type": "fragments",
        "reward_amount": 40,
    },
    {
        "id": "ach_perfect_ending",
        "name": "完美结局",
        "description": "达成所有good ending",
        "icon": "🌟",
        "icon_url": "/assets/achievements/perfect_ending.png",
        "target": 1,
        "reward_type": "fragments",
        "reward_amount": 100,
    },
    {
        "id": "ach_daily_30",
        "name": "全勤",
        "description": "连续登录30天",
        "icon": "📅",
        "icon_url": "/assets/achievements/daily_30.png",
        "target": 30,
        "reward_type": "fragments",
        "reward_amount": 60,
    },
    {
        "id": "ach_bond_100",
        "name": "真爱",
        "description": "好感度达到100",
        "icon": "❤️",
        "icon_url": "/assets/achievements/bond_100.png",
        "target": 100,
        "reward_type": "fragments",
        "reward_amount": 80,
    },
    {
        "id": "ach_master",
        "name": "大师",
        "description": "解锁所有成就",
        "icon": "👑",
        "icon_url": "/assets/achievements/master.png",
        "target": 1,
        "reward_type": "fragments",
        "reward_amount": 200,
    },
]


@router.get("/achievements")
async def get_achievements(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get achievement list with progress and unlock status (card-style)."""
    uid = UUID(user_id)

    # Fetch user's unlocked achievements from DB
    stmt = select(Achievement).where(Achievement.user_id == uid)
    result = await db.execute(stmt)
    unlocked_achievements = {a.achievement_id: a for a in result.scalars().all()}

    # Fetch collection count for progress calculation (table may not exist yet)
    collection_count = 0
    try:
        coll_count_stmt = select(func.count()).select_from(Collection).where(Collection.user_id == uid)
        coll_count_result = await db.execute(coll_count_stmt)
        collection_count = coll_count_result.scalar() or 0
    except Exception:
        # collections table may not exist; skip gracefully
        collection_count = 0

    # Build achievement cards
    achievements = []
    unlocked_count = 0
    claimed_count = 0

    for master in MASTER_ACHIEVEMENTS:
        ach_id = master["id"]
        db_ach = unlocked_achievements.get(ach_id)
        is_unlocked = db_ach is not None

        if is_unlocked:
            unlocked_count += 1
            # For MVP, assume all unlocked achievements have claimed rewards
            claimed = True
            claimed_count += 1
            progress_current = master["target"]
        else:
            claimed = False
            # Estimate progress based on related data
            if ach_id == "ach_first_dialogue":
                progress_current = 0  # Would need dialogue count
            elif ach_id == "ach_bond_60":
                progress_current = 0  # Would need max affection
            elif ach_id == "ach_explorer":
                progress_current = 0  # Would need completed scripts count
            elif ach_id == "ach_collector":
                progress_current = min(collection_count, master["target"])
            else:
                progress_current = 0

        percentage = min(100, int((progress_current / master["target"]) * 100)) if master["target"] > 0 else 0

        achievements.append({
            "id": ach_id,
            "name": master["name"],
            "description": master["description"],
            "icon": master["icon"],
            "icon_url": master["icon_url"],
            "is_unlocked": is_unlocked,
            "unlocked_at": db_ach.unlocked_at.isoformat() if db_ach and db_ach.unlocked_at else None,
            "progress": {
                "current": progress_current,
                "target": master["target"],
                "percentage": percentage,
            },
            "reward": {
                "type": master["reward_type"],
                "amount": master["reward_amount"],
                "claimed": claimed,
            },
        })

    return {
        "achievements": achievements,
        "total": len(achievements),
        "unlocked_count": unlocked_count,
        "claimed_count": claimed_count,
    }


# ── 7. GET /users/me/stats ──

@router.get("/stats")
async def get_user_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get user gameplay statistics."""
    uid = UUID(user_id)
    
    # CR-018 T-009: Completed scripts = COUNT DISTINCT script_id
    # A script is "completed" if it has at least 1 session with status='completed'
    # Multiple completions of the same script (different endings) count as 1
    completed_stmt = select(func.count(func.distinct(GameSession.script_id))).where(
        GameSession.user_id == uid,
        GameSession.status == "completed"
    )
    completed_result = await db.execute(completed_stmt)
    scripts_completed = completed_result.scalar() or 0
    
    # Total play time (sum of session durations in minutes)
    # For MVP, estimate based on choice history length
    sessions_stmt = select(GameSession).where(GameSession.user_id == uid)
    sessions_result = await db.execute(sessions_stmt)
    sessions = sessions_result.scalars().all()
    total_play_time = sum(len(s.choice_history or []) * 2 for s in sessions)  # ~2 min per choice
    
    # Endings unlocked (completed sessions with ending_type)
    endings_stmt = select(func.count()).select_from(GameSession).where(
        GameSession.user_id == uid,
        GameSession.ending_type.isnot(None)
    )
    endings_result = await db.execute(endings_stmt)
    endings_unlocked = endings_result.scalar() or 0
    
    # CGs collected (from collections table)
    cgs_collected = 0
    try:
        cgs_stmt = select(func.count()).select_from(Collection).where(
            Collection.user_id == uid,
            Collection.item_type == "cg"
        )
        cgs_result = await db.execute(cgs_stmt)
        cgs_collected = cgs_result.scalar() or 0
    except Exception:
        pass
    
    # Total dialogues (from user_dialogue_counts)
    total_dialogues = 0
    try:
        dialogues_stmt = select(func.sum(UserDialogueCount.dialogue_count)).where(
            UserDialogueCount.user_id == uid
        )
        dialogues_result = await db.execute(dialogues_stmt)
        total_dialogues = dialogues_result.scalar() or 0
    except Exception:
        pass
    
    return {
        "scripts_completed": scripts_completed,
        "total_play_time_minutes": total_play_time,
        "endings_unlocked": endings_unlocked,
        "cgs_collected": cgs_collected,
        "total_dialogues": total_dialogues,
    }


# ── 8. GET /users/me/asset ──

@router.get("/asset")
async def get_user_asset(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get user fragment balance."""
    uid = UUID(user_id)
    
    # Get current balance
    balance_stmt = select(Fragment).where(Fragment.user_id == uid)
    balance_result = await db.execute(balance_stmt)
    fragment = balance_result.scalar_one_or_none()
    balance = fragment.balance if fragment else 0
    
    # Get total earned (sum of positive transactions)
    earned_stmt = select(func.sum(FragmentTransaction.amount)).where(
        FragmentTransaction.user_id == uid,
        FragmentTransaction.amount > 0
    )
    earned_result = await db.execute(earned_stmt)
    total_earned = earned_result.scalar() or 0
    
    # Get total spent (sum of negative transactions, absolute value)
    spent_stmt = select(func.sum(FragmentTransaction.amount)).where(
        FragmentTransaction.user_id == uid,
        FragmentTransaction.amount < 0
    )
    spent_result = await db.execute(spent_stmt)
    total_spent = abs(spent_result.scalar() or 0)
    
    return {
        "balance": balance,
        "total_earned": total_earned,
        "total_spent": total_spent,
    }


# ── 9. GET /users/me/latest-save ──

@router.get("/latest-save")
async def get_latest_save(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get user's most recent save snapshot."""
    uid = UUID(user_id)
    
    stmt = (
        select(SaveSnapshot)
        .where(SaveSnapshot.user_id == uid)
        .order_by(SaveSnapshot.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    save = result.scalar_one_or_none()
    
    if not save:
        return None
    
    # Get session info to find script and character
    session_stmt = select(GameSession).where(GameSession.id == save.session_id)
    session_result = await db.execute(session_stmt)
    session = session_result.scalar_one_or_none()
    
    script_id = None
    script_name = None
    character_name = None
    character_avatar = None
    
    if session:
        script_id = str(session.script_id)
        script_stmt = select(Script).where(Script.id == session.script_id)
        script_result = await db.execute(script_stmt)
        script = script_result.scalar_one_or_none()
        script_name = script.title if script else None
        
        # Get first character from script
        char_stmt = select(Character).where(Character.script_id == session.script_id).limit(1)
        char_result = await db.execute(char_stmt)
        character = char_result.scalar_one_or_none()
        if character:
            character_name = character.name
            character_avatar = character.avatar_url
    
    # Count choices
    choice_count = len(save.choice_history or []) if save.choice_history else 0
    
    return {
        "id": str(save.id),
        "session_id": str(save.session_id),
        "script_id": script_id,
        "script_name": script_name,
        "character_name": character_name,
        "character_avatar": character_avatar,
        "current_node_id": str(save.current_node_id) if save.current_node_id else None,
        "label": save.label,
        "choice_count": choice_count,
        "created_at": save.created_at.isoformat() if save.created_at else None,
        "updated_at": save.created_at.isoformat() if save.created_at else None,  # No updated_at field in model
    }


# ── 10. GET /users/me/memory/summary ──

@router.get("/memory/summary")
async def get_memory_summary(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get AI memory summary with preferences, bonds, and events (BE-FEAT-025)."""
    uid = UUID(user_id)
    
    # Count total memories
    count_stmt = select(func.count()).select_from(CharacterMemory).where(
        CharacterMemory.user_id == uid
    )
    count_result = await db.execute(count_stmt)
    total_memories = count_result.scalar() or 0
    
    # Get recent 5 memories with character names
    recent_stmt = (
        select(CharacterMemory, Character)
        .outerjoin(Character, Character.id == CharacterMemory.character_id)
        .where(CharacterMemory.user_id == uid)
        .order_by(CharacterMemory.created_at.desc())
        .limit(5)
    )
    recent_result = await db.execute(recent_stmt)
    rows = recent_result.all()
    
    # Check if full memory is available (standard/premium subscription)
    user = await _get_user(db, user_id)
    is_full_available = user.subscription_tier in ["standard", "premium"]
    
    # Build preferences from user profile
    preferences = []
    if user.preferred_genre:
        preferences.append({
            "category": "genre",
            "value": user.preferred_genre,
            "weight": 0.8,
            "description": f"喜欢{user.preferred_genre}题材"
        })
    if user.locale:
        preferences.append({
            "category": "language",
            "value": user.locale,
            "weight": 1.0,
            "description": f"偏好{user.locale}语言"
        })
    
    # Build bonds from affection data
    bonds_stmt = (
        select(Affection, Character)
        .join(Character, Character.id == Affection.character_id)
        .where(Affection.user_id == uid)
        .order_by(Affection.value.desc())
        .limit(10)
    )
    bonds_result = await db.execute(bonds_stmt)
    bonds_rows = bonds_result.all()
    
    bonds = [
        {
            "character_id": str(char.id),
            "character_name": char.name,
            "bond_level": aff.level,
            "bond_value": aff.value,
            "description": f"与{char.name}建立了{aff.level}关系"
        }
        for aff, char in bonds_rows
    ]
    
    # Build events from recent memories
    events = [
        {
            "event_id": str(mem.id),
            "event_type": "dialogue_memory",
            "description": mem.memory_text,
            "created_at": mem.created_at.isoformat() if mem.created_at else None
        }
        for mem, char in rows
    ]
    
    return {
        "preferences": preferences,
        "bonds": bonds,
        "events": events,
        "total_memories": total_memories,
        "recent": [
            {
                "id": str(mem.id),
                "character_id": str(mem.character_id) if mem.character_id else None,
                "character_name": char.name if char else None,
                "content": mem.memory_text,
                "created_at": mem.created_at.isoformat() if mem.created_at else None,
            }
            for mem, char in rows
        ],
        "is_full_available": is_full_available,
    }


# ── 11. GET /users/me/characters/bond ──

@router.get("/characters/bond")
async def get_characters_bond(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get character affection/bond list."""
    uid = UUID(user_id)
    
    # Get all affection records for user
    stmt = (
        select(Affection, Character)
        .join(Character, Character.id == Affection.character_id)
        .where(Affection.user_id == uid)
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    return {
        "characters": [
            {
                "id": str(char.id),
                "name": char.name,
                "avatar_url": char.avatar_url,
                "affection_value": aff.value,
                "affection_level": aff.level,
                "max_affection": 100,
            }
            for aff, char in rows
        ],
        "total": len(rows),
    }


# ── 12. GET /users/me/endings ──

@router.get("/endings")
async def get_endings(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get ending tracking per script."""
    uid = UUID(user_id)
    
    # Get all scripts
    scripts_stmt = select(Script)
    scripts_result = await db.execute(scripts_stmt)
    all_scripts = scripts_result.scalars().all()
    
    # Get all completed sessions with endings for this user
    stmt = (
        select(GameSession, Script)
        .join(Script, Script.id == GameSession.script_id)
        .where(
            GameSession.user_id == uid,
            GameSession.ending_type.isnot(None)
        )
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    # Group by script
    script_endings_map = {}
    for session, script in rows:
        script_id = str(script.id)
        if script_id not in script_endings_map:
            script_endings_map[script_id] = {
                "script_id": script_id,
                "script_name": script.title,
                "unlocked_endings": 0,
                "ending_types": [],
            }
        script_endings_map[script_id]["unlocked_endings"] += 1
        if session.ending_type not in script_endings_map[script_id]["ending_types"]:
            script_endings_map[script_id]["ending_types"].append(session.ending_type)
    
    # Build response with all scripts
    endings_list = []
    total_endings_unlocked = 0
    
    for script in all_scripts:
        script_id = str(script.id)
        # Estimate total endings per script (assume 3 per script for MVP)
        total_endings = 3
        
        if script_id in script_endings_map:
            unlocked = script_endings_map[script_id]["unlocked_endings"]
            ending_types = script_endings_map[script_id]["ending_types"]
        else:
            unlocked = 0
            ending_types = []
        
        total_endings_unlocked += unlocked
        completion_rate = int((unlocked / total_endings) * 100) if total_endings > 0 else 0
        
        endings_list.append({
            "script_id": script_id,
            "script_name": script.title,
            "total_endings": total_endings,
            "unlocked_endings": unlocked,
            "ending_types": ending_types,
            "completion_rate": completion_rate,
        })
    
    return {
        "endings": endings_list,
        "total_scripts": len(all_scripts),
        "total_endings_unlocked": total_endings_unlocked,
    }


# ── 13. GET /users/me/endings/recent ──

@router.get("/endings/recent")
async def get_recent_endings(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get recently unlocked endings (last 3)."""
    uid = UUID(user_id)
    
    stmt = (
        select(GameSession, Script, Character)
        .join(Script, Script.id == GameSession.script_id)
        .outerjoin(Character, Character.script_id == Script.id)
        .where(
            GameSession.user_id == uid,
            GameSession.ending_type.isnot(None)
        )
        .order_by(GameSession.completed_at.desc())
        .limit(3)
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    return {
        "recent_endings": [
            {
                "id": str(session.id),
                "script_name": script.title,
                "character_name": char.name if char else None,
                "ending_type": session.ending_type,
                "ending_title": f"{script.title} - {session.ending_type} ending",  # Generate title
                "ended_at": session.completed_at.isoformat() if session.completed_at else None,
            }
            for session, script, char in rows
        ],
        "total": len(rows),
    }


# ── 14. GET /users/me/memory/full ──

@router.get("/memory/full")
async def get_memory_full(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get full AI memory (premium subscription required)."""
    uid = UUID(user_id)
    
    # Check subscription tier
    user = await _get_user(db, user_id)
    if user.subscription_tier not in ["standard", "premium"]:
        raise AppException(
            error_code="SUBSCRIPTION_REQUIRED",
            status_code=status.HTTP_403_FORBIDDEN,
            message="Full memory access requires Standard or Premium subscription",
        )
    
    # Get all memories with character names
    stmt = (
        select(CharacterMemory, Character)
        .outerjoin(Character, Character.id == CharacterMemory.character_id)
        .where(CharacterMemory.user_id == uid)
        .order_by(CharacterMemory.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    return {
        "memories": [
            {
                "id": str(mem.id),
                "character_id": str(mem.character_id) if mem.character_id else None,
                "character_name": char.name if char else None,
                "content": mem.memory_text,
                "source": mem.source,
                "created_at": mem.created_at.isoformat() if mem.created_at else None,
            }
            for mem, char in rows
        ],
        "total": len(rows),
    }


# ── 15. POST /users/me/avatar ──

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Upload user avatar to local storage."""
    # Validate file type
    if file.content_type not in AVATAR_ALLOWED_TYPES:
        raise AppException(
            error_code="INVALID_FILE_TYPE",
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"Invalid file type: {file.content_type}. Allowed: {', '.join(AVATAR_ALLOWED_TYPES)}",
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > AVATAR_MAX_SIZE:
        raise AppException(
            error_code="FILE_TOO_LARGE",
            status_code=status.HTTP_400_BAD_REQUEST,
            message=f"File size {len(content)} bytes exceeds maximum {AVATAR_MAX_SIZE} bytes (5MB)",
        )
    
    # Generate unique filename
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = AVATAR_UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Generate URL
    avatar_url = f"{AVATAR_BASE_URL}/static/avatars/{unique_filename}"
    
    # Update user profile
    user = await _get_user(db, user_id)
    user.avatar_url = avatar_url
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    
    return {
        "avatar_url": avatar_url,
        "filename": unique_filename,
        "size": len(content),
    }


# ── 16. GET /users/me/avatar/{filename} ──

@router.get("/avatar/{filename}")
async def get_avatar(filename: str):
    """Serve avatar file."""
    file_path = AVATAR_UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise AppException(
            error_code="AVATAR_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            message="Avatar file not found",
        )
    
    return FileResponse(file_path)


# ── 17. GET /users/me/transactions ──

@router.get("/transactions")
async def get_transactions(
    page: int = 1,
    page_size: int = 20,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get user fragment transaction history with pagination."""
    uid = UUID(user_id)
    
    # Get total count
    count_stmt = select(func.count()).select_from(FragmentTransaction).where(
        FragmentTransaction.user_id == uid
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0
    
    # Get transactions with pagination
    offset = (page - 1) * page_size
    stmt = (
        select(FragmentTransaction)
        .where(FragmentTransaction.user_id == uid)
        .order_by(FragmentTransaction.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    transactions = result.scalars().all()
    
    # 交易类型中文映射
    reason_labels = {
        'daily_checkin': '每日签到',
        'streak_milestone': '连续签到奖励',
        'gift_send': '送礼支出',
        'gift_receive': '收到礼物',
        'dialogue_quota_purchase': '碎片兑换对话',
        'shop_purchase': '商城购买',
        'refund': '退款',
        'admin_adjustment': '管理员调整',
        'system_reward': '系统奖励',
        'achievement_reward': '成就奖励',
    }
    
    return {
        "transactions": [
            {
                "id": str(tx.id),
                "type": "income" if tx.amount > 0 else "spend",
                "amount": abs(tx.amount),
                "source": reason_labels.get(tx.reason, tx.reason),
                "description": reason_labels.get(tx.reason, tx.reason),
                "created_at": tx.created_at.isoformat() if tx.created_at else None,
            }
            for tx in transactions
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }
