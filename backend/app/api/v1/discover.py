"""Script discovery API — CR-003 Wave 1a (CR3-003, CR3-004).

Provides:
- GET /discover/recommendations — Personalized script recommendations
- GET /discover/categories — Script genre/category list with counts
- GET /discover/tags — Tag list (extracted from script content)
- GET /discover/scripts — Filter scripts by category/tags/popularity
- GET /discover/trending — Trending/popular scripts
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.api.v1.auth import get_current_user_id
from app.models.script import Script, Route, Node
from app.models.game import GameSession
from app.models.user import User
from app.models.affection import Affection

router = APIRouter(prefix="/discover", tags=["discover"])


# ── Genre definitions (static for MVP) ──
GENRE_DEFINITIONS = [
    {"id": "fantasy", "name": "奇幻冒险", "description": "剑与魔法的异世界", "icon": "⚔️"},
    {"id": "romance", "name": "恋爱", "description": "甜蜜或虐心的情感故事", "icon": "💕"},
    {"id": "mystery", "name": "悬疑", "description": "烧脑解谜与真相追寻", "icon": "🔍"},
    {"id": "horror", "name": "恐怖", "description": "令人毛骨悚然的惊悚体验", "icon": "👻"},
    {"id": "scifi", "name": "科幻", "description": "星际旅行与未来科技", "icon": "🚀"},
    {"id": "slice_of_life", "name": "日常", "description": "轻松治愈的日常故事", "icon": "🌸"},
    {"id": "action", "name": "动作", "description": "热血战斗与冒险", "icon": "🔥"},
    {"id": "drama", "name": "剧情", "description": "深度剧情与角色发展", "icon": "🎭"},
]

# ── Tag definitions ──
TAG_DEFINITIONS = [
    {"id": "multiple_endings", "name": "多结局", "group": "gameplay"},
    {"id": "character_driven", "name": "角色驱动", "group": "gameplay"},
    {"id": "romance_options", "name": "恋爱选项", "group": "gameplay"},
    {"id": "dark_story", "name": "暗黑", "group": "tone"},
    {"id": "lighthearted", "name": "轻松", "group": "tone"},
    {"id": "emotional", "name": "感人", "group": "tone"},
    {"id": "short", "name": "短篇", "group": "length"},
    {"id": "medium", "name": "中篇", "group": "length"},
    {"id": "long", "name": "长篇", "group": "length"},
    {"id": "male_protagonist", "name": "男主", "group": "protagonist"},
    {"id": "female_protagonist", "name": "女主", "group": "protagonist"},
    {"id": "custom_protagonist", "name": "自定义主角", "group": "protagonist"},
]


def _get_script_tags(script: Script) -> list[str]:
    """Infer tags from script properties."""
    tags = []
    # Route count → length
    route_count = len(script.routes) if script.routes else 0
    if route_count <= 2:
        tags.append("short")
    elif route_count <= 5:
        tags.append("medium")
    else:
        tags.append("long")

    # Multiple routes → multiple_endings
    if route_count > 1:
        tags.append("multiple_endings")

    # From script content/metadata (stored in JSON or convention)
    if script.description:
        desc_lower = script.description.lower()
        if any(k in desc_lower for k in ("恋爱", "love", "romance", "恋")):
            tags.append("romance_options")
        if any(k in desc_lower for k in ("黑暗", "dark", "恐怖", "horror")):
            tags.append("dark_story")
        if any(k in desc_lower for k in ("治愈", "轻松", "日常", "relax")):
            tags.append("lighthearted")
        if any(k in desc_lower for k in ("感人", "催泪", "emotional")):
            tags.append("emotional")

    tags.append("character_driven")
    return list(set(tags))


def _script_to_card(script: Script, tags: Optional[list[str]] = None) -> dict:
    """Convert Script to a discover card dict."""
    return {
        "id": str(script.id),
        "slug": script.slug,
        "title": script.title,
        "description": script.description,
        "genre": script.genre,
        "cover_image_url": script.cover_image_url,
        "route_count": len(script.routes) if script.routes else 0,
        "tags": tags or _get_script_tags(script),
        "created_at": script.created_at.isoformat() if script.created_at else None,
    }


@router.get("/recommendations")
async def get_recommendations(
    limit: int = 10,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-003: Get personalized script recommendations.

    Algorithm (MVP):
    1. Get user's played scripts (from game_sessions)
    2. Get user's preferred genres (from preferences)
    3. Score scripts: genre match +3, not played +5, newer +1
    4. Return top N by score
    """
    uid = UUID(user_id)

    # Load user preferences
    user_result = await db.execute(select(User).where(User.id == uid))
    user = user_result.scalar_one_or_none()
    preferred_genre = None
    if user and hasattr(user, "preferences") and user.preferences:
        preferred_genre = user.preferences.get("preferred_genre")

    # Get played script IDs
    played_stmt = (
        select(GameSession.script_id)
        .where(GameSession.user_id == uid)
        .distinct()
    )
    played_result = await db.execute(played_stmt)
    played_ids = {row[0] for row in played_result.all()}

    # Load all scripts with routes
    stmt = (
        select(Script)
        .options(selectinload(Script.routes))
        .order_by(Script.created_at.desc())
    )
    result = await db.execute(stmt)
    scripts = list(result.scalars().all())

    # Score each script
    scored = []
    for s in scripts:
        score = 0
        if s.id not in played_ids:
            score += 5  # Not played bonus
        if preferred_genre and s.genre == preferred_genre:
            score += 3  # Genre match
        if s.routes and len(s.routes) > 2:
            score += 2  # Rich content bonus
        # Recency bonus (newer = higher)
        scored.append((score, s))

    # Sort by score desc, then by creation date desc
    scored.sort(key=lambda x: (x[0], x[1].created_at), reverse=True)

    cards = [_script_to_card(s) for _, s in scored[:limit]]
    return {"recommendations": cards, "total": len(cards)}


@router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-004: Get script categories with script counts.

    Public endpoint — no auth required.
    """
    # Count scripts per genre
    stmt = (
        select(Script.genre, func.count(Script.id))
        .group_by(Script.genre)
    )
    result = await db.execute(stmt)
    genre_counts = dict(result.all())

    categories = []
    for g in GENRE_DEFINITIONS:
        categories.append({
            **g,
            "script_count": genre_counts.get(g["id"], 0),
        })

    return {"categories": categories}


@router.get("/tags")
async def get_tags(
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-004: Get available tags with script counts.

    Public endpoint — no auth required.
    """
    # Load all scripts to compute tag counts
    stmt = select(Script).options(selectinload(Script.routes))
    result = await db.execute(stmt)
    scripts = list(result.scalars().all())

    # Count tag occurrences
    tag_counts: dict[str, int] = {}
    for s in scripts:
        for tag in _get_script_tags(s):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    tags = []
    for t in TAG_DEFINITIONS:
        tags.append({
            **t,
            "script_count": tag_counts.get(t["id"], 0),
        })

    return {"tags": tags}


@router.get("/scripts")
async def discover_scripts(
    category: Optional[str] = None,
    tags: Optional[str] = None,
    sort_by: str = "newest",
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    CR3-004: Discover scripts with category/tag filtering.

    Public endpoint — no auth required.
    """
    stmt = select(Script).options(selectinload(Script.routes))

    # Filter by category
    if category:
        stmt = stmt.where(Script.genre == category)

    result = await db.execute(stmt)
    scripts = list(result.scalars().all())

    # Filter by tags (post-query, since tags are computed)
    if tags and isinstance(tags, str):
        tag_set = set(t.strip() for t in tags.split(","))
        scripts = [
            s for s in scripts
            if tag_set.issubset(set(_get_script_tags(s)))
        ]

    # Sort
    if sort_by == "newest":
        scripts.sort(key=lambda s: s.created_at, reverse=True)
    elif sort_by == "title":
        scripts.sort(key=lambda s: s.title)
    elif sort_by == "popular":
        scripts.sort(key=lambda s: len(s.routes) if s.routes else 0, reverse=True)

    total = len(scripts)
    page = scripts[offset: offset + limit]

    return {
        "scripts": [_script_to_card(s) for s in page],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.get("/trending")
async def get_trending(
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
):
    """
    Trending scripts — most played in the last 7 days.

    Public endpoint — no auth required.
    """
    from datetime import datetime, timedelta

    since = datetime.utcnow() - timedelta(days=7)

    # Count game sessions per script in last 7 days
    stmt = (
        select(GameSession.script_id, func.count(GameSession.id).label("play_count"))
        .where(GameSession.started_at >= since)
        .group_by(GameSession.script_id)
        .order_by(desc("play_count"))
        .limit(limit)
    )
    result = await db.execute(stmt)
    trending_rows = result.all()

    # Load full scripts
    script_ids = [row[0] for row in trending_rows]
    if script_ids:
        stmt2 = (
            select(Script)
            .options(selectinload(Script.routes))
            .where(Script.id.in_(script_ids))
        )
        result2 = await db.execute(stmt2)
        scripts = list(result2.scalars().all())
    else:
        # Fallback: return newest scripts if no play data
        stmt2 = (
            select(Script)
            .options(selectinload(Script.routes))
            .order_by(Script.created_at.desc())
            .limit(limit)
        )
        result2 = await db.execute(stmt2)
        scripts = list(result2.scalars().all())

    cards = []
    for s in scripts:
        card = _script_to_card(s)
        # Attach play count
        for row in trending_rows:
            if row[0] == s.id:
                card["play_count_7d"] = row[1]
                break
        else:
            card["play_count_7d"] = 0
        cards.append(card)

    return {"trending": cards, "total": len(cards)}
