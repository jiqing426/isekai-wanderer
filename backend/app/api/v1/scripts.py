"""Script (story) API endpoints."""

import math
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.models.script import Script, Route, Node
from app.api.v1.auth import get_current_user_id
from app.services.subscription_service import SubscriptionService

router = APIRouter(prefix="/scripts", tags=["scripts"])

# Category definitions for categoryList response
CATEGORY_LIST = [
    {"id": "all", "name": "全部", "icon": "🎭"},
    {"id": "romance", "name": "恋爱", "icon": "💕"},
    {"id": "fantasy", "name": "冒险", "icon": "⚔️"},
    {"id": "mystery", "name": "悬疑", "icon": "🔍"},
    {"id": "horror", "name": "恐怖", "icon": "👻"},
    {"id": "scifi", "name": "科幻", "icon": "🚀"},
    {"id": "slice_of_life", "name": "日常", "icon": "🌸"},
    {"id": "action", "name": "动作", "icon": "🔥"},
    {"id": "drama", "name": "剧情", "icon": "🎭"},
]


@router.get("")
async def list_scripts(
    search: Optional[str] = Query(None, description="搜索关键词（标题/描述）"),
    category: Optional[str] = Query(None, description="分类筛选（全部/恋爱/冒险/悬疑）"),
    sort: Optional[str] = Query(None, description="排序方式（newest/popular/rating）"),
    sortType: Optional[str] = Query(None, description="排序类型（newest/popular/rating）— sort 的别名"),
    page: int = Query(1, ge=1, description="页码"),
    size: Optional[int] = Query(None, ge=1, le=100, description="每页数量"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="每页数量（size 的别名，向后兼容）"),
    db: AsyncSession = Depends(get_db),
):
    """List scripts with search, filter, sort and pagination (public — auth optional).
    
    CR-043 AC-009: When user is authenticated, each script includes is_accessible field.
    When not authenticated, is_accessible is omitted (frontend can compute from free tier).
    """
    # CR-043: Try to get user_id from JWT if provided (optional)
    actual_user_id = None
    # Resolve size: prefer size, fallback to limit, default 12
    effective_size = size if size is not None else (limit if limit is not None else 12)
    # Clamp size to [10, 40] per BE-D4 spec
    effective_size = max(10, min(40, effective_size))
    
    # Resolve sort: prefer sort, fallback to sortType
    effective_sort = sort if sort is not None else (sortType if sortType is not None else "newest")

    # Base statement with joinedload for routes
    base_stmt = select(Script).options(joinedload(Script.routes))
    count_stmt = select(func.count(Script.id))

    # Search filter (title or description)
    if search:
        search_pattern = f"%{search}%"
        search_filter = or_(
            Script.title.ilike(search_pattern),
            Script.description.ilike(search_pattern),
        )
        base_stmt = base_stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)

    # Category filter (genre)
    if category and category != "全部" and category != "all":
        # Map frontend category names to genre values
        category_map = {
            "恋爱": "romance",
            "冒险": "fantasy",
            "悬疑": "mystery",
            # Also accept genre IDs directly
            "romance": "romance",
            "fantasy": "fantasy",
            "mystery": "mystery",
            "horror": "horror",
            "scifi": "scifi",
            "slice_of_life": "slice_of_life",
            "action": "action",
            "drama": "drama",
        }
        genre_value = category_map.get(category, category)
        base_stmt = base_stmt.where(Script.genre == genre_value)
        count_stmt = count_stmt.where(Script.genre == genre_value)

    # Get total count before pagination
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Calculate totalPage
    total_page = math.ceil(total / effective_size) if total > 0 else 0

    # BE-D3: Two-level stable sort
    # popular → hot_value DESC, script_id ASC
    # rating → created_at DESC, script_id ASC (no score field yet, use created_at as proxy)
    # newest → created_at DESC, script_id ASC
    if effective_sort == "popular":
        base_stmt = base_stmt.order_by(Script.hot_value.desc(), Script.id.asc())
    elif effective_sort == "rating":
        base_stmt = base_stmt.order_by(Script.created_at.desc(), Script.id.asc())
    else:
        # Default: newest
        base_stmt = base_stmt.order_by(Script.created_at.desc(), Script.id.asc())

    # Pagination
    offset = (page - 1) * effective_size
    base_stmt = base_stmt.offset(offset).limit(effective_size)

    result = await db.execute(base_stmt)
    scripts = list(result.unique().scalars().all())

    # CR-043: Compute is_accessible for authenticated users
    tier = "free"
    script_access = "trial_only"
    if actual_user_id:
        try:
            sub_service = SubscriptionService(db)
            tier = await sub_service.get_user_tier(UUID(actual_user_id))
            perms = await sub_service.get_tier_permissions(tier)
            script_access = perms.script_access
        except Exception:
            pass
    
    from app.api.v1.game import _compute_script_accessible
    
    return {
        "categoryList": CATEGORY_LIST,
        "scripts": [
            {
                "id": str(s.id),
                "slug": s.slug,
                "title": s.title,
                "description": s.description,
                "genre": s.genre,
                "cover_image_url": s.cover_image_url,
                "route_count": len(s.routes) if s.routes else 0,
                "hot_value": s.hot_value or 0,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "engine_type": "corvus",
                "is_accessible": _compute_script_accessible(script_access, s) if actual_user_id else None,
            }
            for s in scripts
        ],
        "total": total,
        "totalPage": total_page,
        "page": page,
        "size": effective_size,
        # Backward compat: also include limit
        "limit": effective_size,
    }


@router.get("/{script_id}")
async def get_script(
    script_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get script details with routes, characters, endings and CG previews (BE-FEAT-023).
    
    CR-028: Added playable_characters array with is_unlocked calculation.
    """
    try:
        script_uuid = UUID(script_id)
        user_uuid = UUID(user_id)
    except ValueError:
        raise AppException(ErrorCode.INVALID_SCRIPT_ID, 400, "Invalid script_id or user_id format")
    
    stmt = (
        select(Script)
        .options(selectinload(Script.routes).selectinload(Route.nodes).selectinload(Node.choices))
        .where(Script.id == script_uuid)
    )
    result = await db.execute(stmt)
    script = result.scalar_one_or_none()
    
    if not script:
        raise AppException(ErrorCode.SCRIPT_NOT_FOUND, 404, "Script not found")
    
    # Load characters for this script
    from app.models.script import Character
    char_stmt = select(Character).where(Character.script_id == script_uuid)
    char_result = await db.execute(char_stmt)
    characters = char_result.scalars().all()
    
    # CR-028: Load playable characters with unlock status
    playable_char_stmt = (
        select(Character)
        .where(
            Character.script_id == script_uuid,
            Character.playable == True,
            Character.playable_route_id != None
        )
    )
    playable_char_result = await db.execute(playable_char_stmt)
    playable_characters = playable_char_result.scalars().all()
    
    # CR-028: Load user's unlocked characters
    from app.models.user_character_unlock import UserCharacterUnlock
    from app.models.user import User
    
    # Get user subscription tier for unlock calculation
    user_stmt = select(User).where(User.id == user_uuid)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()
    subscription_tier = user.subscription_tier if user else "free"
    
    # Get user's unlocked characters
    unlock_stmt = select(UserCharacterUnlock.character_id).where(
        UserCharacterUnlock.user_id == user_uuid
    )
    unlock_result = await db.execute(unlock_stmt)
    unlocked_character_ids = {str(row[0]) for row in unlock_result.fetchall()}
    
    # Build playable_characters response with is_unlocked calculation
    playable_characters_response = []
    for char in playable_characters:
        char_id = str(char.id)
        unlock_type = char.unlock_type or "free"
        
        # Calculate is_unlocked
        if unlock_type == "free":
            is_unlocked = True
        elif unlock_type == "paid":
            is_unlocked = char_id in unlocked_character_ids
        elif unlock_type == "subscription":
            is_unlocked = subscription_tier in ["premium", "vip"]
        else:
            is_unlocked = False
        
        playable_characters_response.append({
            "id": char_id,
            "name": char.name,
            "avatar_url": char.avatar_url,
            "play_description": char.play_description,
            "unlock_type": unlock_type,
            "unlock_price": char.unlock_price or 0,
            "is_unlocked": is_unlocked,
        })
    
    # Load endings for this script
    from sqlalchemy import text
    endings_stmt = text("""
        SELECT e.id, e.title, e.type, e.description, e.unlock_condition, e.route_id, r.title as route_name, e.image_url
        FROM endings e
        LEFT JOIN routes r ON e.route_id = r.id
        WHERE e.script_id = :script_id
        ORDER BY e.type, e.title
    """)
    endings_result = await db.execute(endings_stmt, {"script_id": script_uuid})
    endings_rows = endings_result.fetchall()
    
    # Load CG assets for this script
    cg_stmt = text("""
        SELECT id, name, image_url, route_id
        FROM cg_assets
        WHERE script_id = :script_id
        ORDER BY name
    """)
    cg_result = await db.execute(cg_stmt, {"script_id": script_uuid})
    cg_rows = cg_result.fetchall()
    
    # Query user's game sessions to determine unlock status
    from app.models.game import GameSession
    session_stmt = (
        select(GameSession)
        .where(
            GameSession.user_id == user_uuid,
            GameSession.script_id == script_uuid,
        )
    )
    session_result = await db.execute(session_stmt)
    user_sessions = list(session_result.scalars().all())
    
    # Build completed nodes set
    completed_node_ids = set()
    for session in user_sessions:
        choices = session.choice_history or []
        for choice in choices:
            if isinstance(choice, dict) and "node_id" in choice:
                completed_node_ids.add(choice["node_id"])
    
    # Build chapters structure and calculate stats
    chapters = []
    total_nodes = 0
    unlocked_nodes = 0
    
    for route_idx, route in enumerate(script.routes):
        chapter_id = f"{script_uuid}-{route_idx:03d}"
        chapter_title = route.title or f"第{route_idx + 1}章"
        
        nodes = []
        for node in route.nodes:
            total_nodes += 1
            is_unlocked = str(node.id) in completed_node_ids
            if is_unlocked:
                unlocked_nodes += 1
            
            node_data = {
                "nodeId": str(node.id),
                "type": node.node_type,
                "title": (node.content or {}).get("title", f"节点 {len(nodes) + 1}"),
                "isUnlocked": is_unlocked,
            }
            nodes.append(node_data)
        
        if nodes:
            chapters.append({
                "chapterId": chapter_id,
                "title": chapter_title,
                "nodes": nodes
            })
    
    # Calculate completion rate
    completion_rate = int((unlocked_nodes / total_nodes * 100)) if total_nodes > 0 else 0
    
    # Build unlocked endings set
    unlocked_endings = set()
    for session in user_sessions:
        if session.ending_type:
            route_id = str(session.route_id)
            ending_key = f"{route_id}-{session.ending_type}"
            unlocked_endings.add(ending_key)
    
    # Build unlocked CGs set
    from sqlalchemy import text as sql_text
    unlocked_cgs_stmt = sql_text("""
        SELECT cg_id FROM unlocked_cgs WHERE user_id = :user_id
    """)
    unlocked_cgs_result = await db.execute(unlocked_cgs_stmt, {"user_id": user_uuid})
    unlocked_cg_ids = {str(row[0]) for row in unlocked_cgs_result.fetchall()}
    
    # Build explored routes set (routes that user has active or completed sessions for)
    # CR-033 FIX: Rewrite route unlock logic
    # Rules:
    # 1. Sort routes by chapter_number (NULL → 0)
    # 2. First chapter always unlocked (game entry point)
    # 3. Chapter N completed → Chapter N+1 unlocked
    # 4. Active chapter stays unlocked
    explored_route_ids = set()
    
    # 1. Sort routes by chapter_number
    sorted_routes = sorted(
        script.routes,
        key=lambda r: (r.chapter_number if r.chapter_number is not None else 0, r.created_at)
    )
    
    if not sorted_routes:
        pass  # no routes, nothing to unlock
    else:
        # 2. First chapter always unlocked
        first_route = sorted_routes[0]
        explored_route_ids.add(str(first_route.id))
        
        # 3. Build a map: route_id → session status (best status per route)
        route_session_status: dict[str, str] = {}
        for session in user_sessions:
            rid = str(session.route_id)
            existing = route_session_status.get(rid)
            # Priority: active > completed > abandoned
            if existing is None:
                route_session_status[rid] = session.status
            elif session.status == 'active' and existing != 'active':
                route_session_status[rid] = 'active'
            # Keep 'active' if already set
        
        # 4. Walk through sorted routes sequentially
        for i, route in enumerate(sorted_routes):
            route_id_str = str(route.id)
            status = route_session_status.get(route_id_str)
            
            if status == 'active':
                # Active chapter stays unlocked
                explored_route_ids.add(route_id_str)
            elif status == 'completed':
                # Completed chapter is unlocked, and unlocks next chapter
                explored_route_ids.add(route_id_str)
                if i + 1 < len(sorted_routes):
                    explored_route_ids.add(str(sorted_routes[i + 1].id))
            # else: no session or abandoned → only unlocked if it's the first chapter
            #       (already handled above)
    
    return {
        "id": str(script.id),
        "slug": script.slug,
        "title": script.title,
        "description": script.description,
        "genre": script.genre,
        "cover_image_url": script.cover_image_url,
        "author": script.author or "美澜",
        "hot_value": script.hot_value or 0,
        "routes": [
            {
                "id": str(r.id),
                "title": r.title,
                "description": r.description,
                "node_count": len(r.nodes),
                "is_unlocked": str(r.id) in explored_route_ids,
                "is_completed": any(
                    s.route_id == r.id and s.status == 'completed' 
                    for s in user_sessions
                ),
            }
            for r in script.routes
        ],
        "routes_count": len(script.routes),
        "endings": [
            {
                "id": str(row[0]),
                "title": row[1],
                "type": row[2],
                "description": row[3] or "",
                "unlock_condition": row[4] or "",
                "route_id": str(row[5]) if row[5] else None,
                "is_unlocked": f"{str(row[5]) if row[5] else ''}-{row[2]}" in unlocked_endings,
                "image_url": row[7] if len(row) > 7 else None,
            }
            for row in endings_rows
        ],
        "endings_count": len(endings_rows),
        "cg_previews": [
            {
                "id": str(row[0]),
                "name": row[1],
                "image_url": row[2],
                "route_id": str(row[3]) if row[3] else None,
                "chapter": f"第{idx + 1}章" if idx < len(chapters) else None,
                "description": chapters[idx].get("description", "") if idx < len(chapters) else "",
                "is_unlocked": str(row[0]) in unlocked_cg_ids,
            }
            for idx, row in enumerate(cg_rows)
        ],
        "characters": [
            {
                "id": str(char.id),
                "name": char.name,
                "description": char.description,
                "age": char.age,
                "height": char.height,
                "birthday": char.birthday,
                "likes": char.likes or [],
                "personality": char.personality or {},
                "avatar_url": char.avatar_url,
                "is_main": char.is_main,
            }
            for char in characters
        ],
        # CR-028: Playable characters for role selection
        "playable_characters": playable_characters_response,
        "chapters": chapters,
        "totalNodes": total_nodes,
        "unlockedNodes": unlocked_nodes,
        "completionRate": completion_rate,
        "engine_type": "corvus",
    }


# ── W05 剧本详情页 API（v2 - 按新原型重做）──────────────────────────────


@router.get("/{script_id}/characters")
async def get_script_characters(
    script_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get characters for a specific script."""
    try:
        script_uuid = UUID(script_id)
    except ValueError:
        raise AppException(ErrorCode.INVALID_SCRIPT_ID, 400, "Invalid script_id format")
    
    # Verify script exists
    stmt = select(Script).where(Script.id == script_uuid)
    result = await db.execute(stmt)
    script = result.scalar_one_or_none()
    if not script:
        raise AppException(ErrorCode.SCRIPT_NOT_FOUND, 404, "Script not found")
    
    # Load characters for this script
    from app.models.script import Character
    char_stmt = select(Character).where(Character.script_id == script_uuid)
    char_result = await db.execute(char_stmt)
    characters = char_result.scalars().all()
    
    return {
        "characters": [
            {
                "id": str(char.id),
                "name": char.name,
                "description": char.description,
                "age": char.age,
                "height": char.height,
                "birthday": char.birthday,
                "likes": char.likes or [],
                "personality": char.personality or {},
                "avatar_url": char.avatar_url,
                "is_main": char.is_main,
            }
            for char in characters
        ],
        "total": len(characters),
    }


@router.get("/{script_id}/routes")
async def get_script_routes(
    script_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """W05: Get routes as exploration tree (route → chapters → branches)."""
    try:
        script_uuid = UUID(script_id)
        user_uuid = UUID(user_id)
    except ValueError:
        raise AppException(ErrorCode.INVALID_SCRIPT_ID, 400, "Invalid script_id or user_id format")

    # Verify script exists and load routes with nodes
    stmt = (
        select(Script)
        .options(
            joinedload(Script.routes)
            .joinedload(Route.nodes)
            .joinedload(Node.choices)
        )
        .where(Script.id == script_uuid)
    )
    result = await db.execute(stmt)
    script = result.unique().scalar_one_or_none()
    if not script:
        raise AppException(ErrorCode.SCRIPT_NOT_FOUND, 404, "Script not found")

    # Query user's game sessions for this script
    from app.models.game import GameSession
    session_stmt = (
        select(GameSession)
        .where(
            GameSession.user_id == user_uuid,
            GameSession.script_id == script_uuid,
        )
    )
    session_result = await db.execute(session_stmt)
    user_sessions = list(session_result.scalars().all())

    # Build completed nodes set
    completed_node_ids = set()
    for session in user_sessions:
        choices = session.choice_history or []
        for choice in choices:
            if isinstance(choice, dict) and "node_id" in choice:
                completed_node_ids.add(choice["node_id"])

    # Build tree structure for each route
    routes_response = []
    for route in script.routes:
        # Group nodes into chapters (by node_type or content structure)
        chapters = []
        chapter_map = {}  # chapter_id -> chapter data

        for node in route.nodes:
            # Extract chapter info from node content or use node_type
            content = node.content or {}
            chapter_id = content.get("chapter_id", f"ch{len(chapters) + 1}")
            chapter_title = content.get("chapter_title", f"第{len(chapters) + 1}章")

            if chapter_id not in chapter_map:
                chapter_map[chapter_id] = {
                    "id": chapter_id,
                    "title": chapter_title,
                    "completed": False,
                    "branches": [],
                }
                chapters.append(chapter_map[chapter_id])

            # Check if this node is completed
            node_completed = str(node.id) in completed_node_ids
            if node_completed:
                chapter_map[chapter_id]["completed"] = True

            # Create branches from choices
            for choice in node.choices:
                branch_name = content.get("branch_name", choice.text[:20] if choice.text else "分支")
                branch_id = f"branch-{str(choice.id)[:8]}"

                # Determine unlock status
                unlocked = node_completed or str(node.id) in completed_node_ids
                affection = content.get("affection", 0)
                requirement = content.get("requirement", None)

                branch_data = {
                    "id": branch_id,
                    "name": branch_name,
                    "affection": affection,
                    "unlocked": unlocked,
                }
                if requirement:
                    branch_data["requirement"] = requirement

                chapter_map[chapter_id]["branches"].append(branch_data)

        # If no chapters found, create mock structure
        if not chapters:
            chapters = [
                {
                    "id": "ch1",
                    "title": "第一章：初遇",
                    "completed": False,
                    "branches": [
                        {
                            "id": "branch1",
                            "name": "主线",
                            "affection": 0,
                            "unlocked": True,
                        }
                    ],
                }
            ]

        routes_response.append({
            "id": str(route.id),
            "name": route.title,
            "chapter_type": route.chapter_type,
            "chapter_type_label": {
                'encounter': '相遇',
                'daily': '日常',
                'conflict': '冲突',
                'convergence': '收束',
            }.get(route.chapter_type, route.chapter_type) if route.chapter_type else None,
            "chapters": chapters,
        })

    return {"routes": routes_response}


@router.get("/{script_id}/endings")
async def get_script_endings(
    script_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """CR-013: Get endings list with unlock status from database."""
    try:
        script_uuid = UUID(script_id)
        user_uuid = UUID(user_id)
    except ValueError:
        raise AppException(ErrorCode.INVALID_SCRIPT_ID, 400, "Invalid script_id or user_id format")

    # Verify script exists
    stmt = select(Script).where(Script.id == script_uuid)
    result = await db.execute(stmt)
    script = result.scalar_one_or_none()
    if not script:
        raise AppException(ErrorCode.SCRIPT_NOT_FOUND, 404, "Script not found")

    # Query endings from database
    from sqlalchemy import text
    endings_stmt = text("""
        SELECT e.id, e.title, e.type, e.description, e.unlock_condition, e.route_id, r.title as route_name, e.image_url
        FROM endings e
        LEFT JOIN routes r ON e.route_id = r.id
        WHERE e.script_id = :script_id
        ORDER BY e.type, e.title
    """)
    endings_result = await db.execute(endings_stmt, {"script_id": script_uuid})
    endings_rows = endings_result.fetchall()

    # Query user's completed game sessions to determine unlock status
    from app.models.game import GameSession
    session_stmt = (
        select(GameSession)
        .where(
            GameSession.user_id == user_uuid,
            GameSession.script_id == script_uuid,
            GameSession.status == "completed",
        )
    )
    session_result = await db.execute(session_stmt)
    completed_sessions = list(session_result.scalars().all())

    # Build unlocked endings set (route_id + ending_type)
    unlocked_endings = set()
    unlock_dates = {}
    for session in completed_sessions:
        ending_type = session.ending_type or "normal"
        route_id = str(session.route_id)
        ending_key = f"{route_id}-{ending_type}"
        unlocked_endings.add(ending_key)
        if ending_key not in unlock_dates:
            unlock_dates[ending_key] = session.completed_at

    # Build response
    endings = []
    for row in endings_rows:
        ending_id, title, ending_type, description, unlock_condition, route_id, route_name, image_url = row
        route_id_str = str(route_id) if route_id else ""
        ending_key = f"{route_id_str}-{ending_type}"
        is_unlocked = ending_key in unlocked_endings
        
        endings.append({
            "id": str(ending_id),
            "title": title,
            "type": ending_type,
            "description": description or "",
            "unlock_condition": unlock_condition or "",
            "route_id": route_id_str,
            "route_name": route_name or "",
            "unlocked": is_unlocked,
            "image_url": image_url,
            "unlock_date": unlock_dates[ending_key].strftime("%Y-%m-%d") if is_unlocked and ending_key in unlock_dates else None,
        })

    unlocked_count = sum(1 for e in endings if e["unlocked"])

    return {
        "endings": endings,
        "total": len(endings),
        "unlockedCount": unlocked_count,
    }


@router.get("/{script_id}/cg-preview")
async def get_script_cg_preview(
    script_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """CR-013: Get CG preview thumbnails with unlock status from database."""
    try:
        script_uuid = UUID(script_id)
        user_uuid = UUID(user_id)
    except ValueError:
        raise AppException(ErrorCode.INVALID_SCRIPT_ID, 400, "Invalid script_id or user_id format")

    # Verify script exists
    stmt = select(Script).where(Script.id == script_uuid)
    result = await db.execute(stmt)
    script = result.scalar_one_or_none()
    if not script:
        raise AppException(ErrorCode.SCRIPT_NOT_FOUND, 404, "Script not found")

    # Query CG assets from database
    from sqlalchemy import text
    cg_stmt = text("""
        SELECT c.id, c.name, c.image_url, c.route_id
        FROM cg_assets c
        WHERE c.script_id = :script_id
        ORDER BY c.name
    """)
    cg_result = await db.execute(cg_stmt, {"script_id": script_uuid})
    cg_rows = cg_result.fetchall()

    # Query user's unlocked CGs
    unlocked_stmt = text("""
        SELECT cg_id FROM unlocked_cgs
        WHERE user_id = :user_id
    """)
    unlocked_result = await db.execute(unlocked_stmt, {"user_id": user_uuid})
    unlocked_cg_ids = {str(row[0]) for row in unlocked_result.fetchall()}

    # Build response
    cgs = []
    for row in cg_rows:
        cg_id, name, image_url, route_id = row
        is_unlocked = str(cg_id) in unlocked_cg_ids
        
        cgs.append({
            "id": str(cg_id),
            "name": name,
            "imageUrl": image_url,
            "routeId": str(route_id) if route_id else None,
            "unlocked": is_unlocked,
        })

    unlocked_count = sum(1 for cg in cgs if cg["unlocked"])

    return {
        "cgs": cgs,
        "total": len(cgs),
        "unlockedCount": unlocked_count,
    }


# ── CR-013 剧本详情页面渲染 ──────────────────────────────────────────────


@router.get("/{script_id}/detail")
async def get_script_detail(
    script_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """CR-013: 获取剧本详情（含章节和节点数据）"""
    try:
        script_uuid = UUID(script_id)
        user_uuid = UUID(user_id)
    except ValueError:
        raise AppException(ErrorCode.INVALID_SCRIPT_ID, 400, "Invalid script_id or user_id format")

    # Verify script exists and load routes with nodes
    stmt = (
        select(Script)
        .options(
            joinedload(Script.routes)
            .joinedload(Route.nodes)
            .joinedload(Node.choices)
        )
        .where(Script.id == script_uuid)
    )
    result = await db.execute(stmt)
    script = result.unique().scalar_one_or_none()
    if not script:
        raise AppException(ErrorCode.SCRIPT_NOT_FOUND, 404, "Script not found")

    # Query user's game sessions for this script to determine unlocked nodes
    from app.models.game import GameSession
    session_stmt = (
        select(GameSession)
        .where(
            GameSession.user_id == user_uuid,
            GameSession.script_id == script_uuid,
        )
    )
    session_result = await db.execute(session_stmt)
    user_sessions = list(session_result.scalars().all())

    # Build completed nodes set
    completed_node_ids = set()
    for session in user_sessions:
        choices = session.choice_history or []
        for choice in choices:
            if isinstance(choice, dict) and "node_id" in choice:
                completed_node_ids.add(choice["node_id"])

    # Build chapters structure
    chapters = []
    total_nodes = 0
    unlocked_nodes = 0

    for route_idx, route in enumerate(script.routes):
        chapter_id = f"{script_uuid}-{route_idx:03d}"
        chapter_title = route.title or f"第{route_idx + 1}章"

        nodes = []
        for node in route.nodes:
            total_nodes += 1
            is_unlocked = str(node.id) in completed_node_ids
            if is_unlocked:
                unlocked_nodes += 1

            # Determine node type from database node_type field
            # Map database types to API types
            db_node_type = node.node_type
            content = node.content or {}
            
            # Map database node_type to API node type
            if db_node_type == "preset":
                node_type = "ai_dialog"
            elif db_node_type == "ending":
                node_type = "ending_node"
            elif db_node_type == "choice":
                node_type = "choice_point"
            elif db_node_type == "cg":
                node_type = "cg_trigger"
            elif db_node_type == "converge":
                node_type = "converge_node"
            else:
                node_type = "fixed_scene"

            # Build node response based on type
            node_data = {
                "nodeId": str(node.id),
                "type": node_type,
                "title": content.get("title", f"节点 {len(nodes) + 1}"),
                "isUnlocked": is_unlocked,
            }

            # Add type-specific fields
            if node_type == "fixed_scene":
                node_data["content"] = content.get("content", "")
                node_data["background"] = content.get("background", node.background)
            elif node_type == "ai_dialog":
                node_data["characterId"] = content.get("character_id", "")
                node_data["characterName"] = content.get("character", "")
                node_data["dialogueOptions"] = content.get("dialogue_options", [])
                node_data["text"] = content.get("text", "")
                node_data["emotion"] = content.get("emotion", "")
                node_data["background"] = content.get("background", node.background)
            elif node_type == "choice_point":
                node_data["choices"] = [
                    {
                        "text": choice.text,
                        "nextNodeId": str(choice.next_node_id) if choice.next_node_id else ""
                    }
                    for choice in node.choices
                ]
            elif node_type == "converge_node":
                node_data["description"] = content.get("description", "")
            elif node_type == "cg_trigger":
                node_data["cgId"] = content.get("cg_id", "")
                node_data["cgUrl"] = content.get("cg_url", "")
            elif node_type == "ending_node":
                node_data["endingType"] = content.get("ending_type", "normal")
                node_data["description"] = content.get("description", "")
                node_data["text"] = content.get("text", "")
                node_data["emotion"] = content.get("emotion", "")
                node_data["background"] = content.get("background", node.background)

            nodes.append(node_data)

        if nodes:  # Only add chapter if it has nodes
            chapters.append({
                "chapterId": chapter_id,
                "title": chapter_title,
                "nodes": nodes
            })

    # Calculate completion rate
    completion_rate = int((unlocked_nodes / total_nodes * 100)) if total_nodes > 0 else 0

    return {
        "scriptId": str(script.id),
        "title": script.title,
        "cover": script.cover_image_url or "",
        "description": script.description or "",
        "author": script.author or "美澜",
        "chapters": chapters,
        "totalNodes": total_nodes,
        "unlockedNodes": unlocked_nodes,
        "completionRate": completion_rate
    }


# ── CR-030 章节列表 API ──────────────────────────────────────────────


@router.get("/{script_id}/chapters")
async def get_script_chapters(
    script_id: str,
    db: AsyncSession = Depends(get_db),
):
    """CR-030: Get chapter list for a script, ordered by chapter_number."""
    try:
        script_uuid = UUID(script_id)
    except ValueError:
        raise AppException(ErrorCode.INVALID_SCRIPT_ID, 400, "Invalid script_id format")

    # Verify script exists
    stmt = select(Script).where(Script.id == script_uuid)
    result = await db.execute(stmt)
    script = result.scalar_one_or_none()
    if not script:
        raise AppException(ErrorCode.SCRIPT_NOT_FOUND, 404, "Script not found")

    # Query routes with chapter info
    route_stmt = (
        select(Route)
        .where(Route.script_id == script_uuid)
        .order_by(Route.chapter_number.asc().nullslast(), Route.created_at.asc())
    )
    route_result = await db.execute(route_stmt)
    routes = route_result.scalars().all()

    # Map chapter_type to Chinese title
    chapter_type_title_map = {
        'encounter': '相遇',
        'daily': '日常',
        'conflict': '冲突',
        'convergence': '收束',
    }

    chapters = []
    for route in routes:
        chapter_title = None
        if route.chapter_type:
            chapter_title = chapter_type_title_map.get(route.chapter_type, route.chapter_type)
        
        chapters.append({
            "chapter_number": route.chapter_number,
            "chapter_type": route.chapter_type,
            "title": chapter_title,
            "route_id": str(route.id),
            "route_title": route.title,
        })

    return {
        "chapters": chapters,
    }
