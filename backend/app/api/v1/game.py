"""Game session API endpoints including SSE streaming dialogue."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException
from app.services.narrative import NarrativeEngine
from app.services.narrative.script_service import ScriptService
from app.api.v1.auth import get_current_user_id
from app.models.game import GameSession, GameProgress
from app.models.script import Script, Route, Node, NodeChoice, Character
from app.models.affection import Affection
from app.models.gift_record import GiftRecord
from sqlalchemy import select, func

router = APIRouter()


# ---- Request/Response Schemas ----

class StartGameRequest(BaseModel):
    script_id: str
    route_id: Optional[str] = None
    custom_name: Optional[str] = None


class ChoiceRequest(BaseModel):
    choice_id: str


class CustomInputRequest(BaseModel):
    text: str


class FreeChatRequest(BaseModel):
    message: str
    topic_id: Optional[str] = None


class DialogueResponse(BaseModel):
    type: str  # "dialogue", "choice", "ending"
    text: Optional[str] = None
    emotion: Optional[str] = None
    node_id: Optional[str] = None
    choices: Optional[list] = None
    character_id: Optional[str] = None
    ending_type: Optional[str] = None
    session_id: Optional[str] = None
    # BUG-022: 添加 current_node 字段
    current_node: Optional[dict] = None
    # BUG-023: 添加旁白字段
    narrator_text: Optional[str] = None
    narrator_visible: Optional[bool] = True


class AutoSaveRequest(BaseModel):
    session_id: str
    node_id: str
    choice_id: str


# ---- Endpoints ----

@router.post("/game/start")
async def start_game(
    request: StartGameRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Start a new game session."""
    from app.models.game import GameSession
    from app.services.narrative.script_service import ScriptService
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"[game/start] Received request: script_id={request.script_id}, route_id={request.route_id}")
    
    # Validate script_id UUID
    try:
        script_uuid = UUID(request.script_id)
    except (ValueError, AttributeError):
        raise AppException("INVALID_SCRIPT_ID", 400, f"Invalid script_id: {request.script_id}")
    
    script_service = ScriptService(db)
    
    # Get starting node
    if request.route_id:
        try:
            route_id = UUID(request.route_id)
        except (ValueError, AttributeError):
            raise AppException("INVALID_ROUTE_ID", 400, f"Invalid route_id: {request.route_id}")
    else:
        # Get first route of script
        from sqlalchemy import select
        from app.models.script import Route
        stmt = select(Route).where(Route.script_id == script_uuid).limit(1)
        result = await db.execute(stmt)
        route = result.scalar_one_or_none()
        if not route:
            raise AppException("SCRIPT_NO_ROUTES", 404, "Script has no routes")
        route_id = route.id
    
    logger.info(f"[game/start] Looking for starting node: route_id={route_id}")
    
    # Try to get starting node for the specified route
    try:
        starting_node = await script_service.get_starting_node(route_id)
    except AppException as e:
        if e.status_code == 404 and "No starting node found" in str(e):
            # Route has no nodes, fallback to first route with nodes
            logger.warning(f"[game/start] Route {route_id} has no nodes, trying fallback")
            
            # Find first route with nodes for this script
            from sqlalchemy import select
            from app.models.script import Route, Node
            from sqlalchemy import func
            
            stmt = (
                select(Route)
                .join(Node, Node.route_id == Route.id)
                .where(Route.script_id == script_uuid)
                .group_by(Route.id)
                .having(func.count(Node.id) > 0)
                .limit(1)
            )
            result = await db.execute(stmt)
            fallback_route = result.scalar_one_or_none()
            
            if not fallback_route:
                raise AppException(
                    "SCRIPT_NO_NODES",
                    404,
                    f"Script {script_uuid} has no routes with nodes"
                )
            
            route_id = fallback_route.id
            logger.info(f"[game/start] Using fallback route: {route_id}")
            starting_node = await script_service.get_starting_node(route_id)
        else:
            raise
    
    logger.info(f"[game/start] Starting node found: {starting_node.id}")
    
    # CR-018 P0 fix: Check if starting_node exists
    if not starting_node:
        raise AppException(
            "NO_STARTING_NODE",
            404,
            f"Route {route_id} has no starting node (parent_id IS NULL)"
        )
    
    # Create session
    session = GameSession(
        user_id=UUID(user_id),
        script_id=script_uuid,
        route_id=route_id,
        current_node_id=starting_node.id,
        custom_name=request.custom_name,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return {
        "session_id": str(session.id),
        "node_id": str(starting_node.id),
        "message": "Game started",
    }


async def _verify_session_ownership(session_id: UUID, user_id: str, db: AsyncSession) -> None:
    """CRIT-003 fix: Verify current user owns the game session."""
    from app.models.game import GameSession
    from sqlalchemy import select
    
    stmt = select(GameSession).where(GameSession.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise AppException("SESSION_NOT_FOUND", 404, "Game session not found")
    
    if str(session.user_id) != user_id:
        raise AppException("SESSION_FORBIDDEN", 403, "Access denied: you do not own this session")


@router.get("/game/{session_id}")
async def get_game_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get current game session state."""
    # CRIT-003: verify ownership
    await _verify_session_ownership(UUID(session_id), user_id, db)
    
    engine = NarrativeEngine(db)
    state = await engine.script_service.get_game_session_state(UUID(session_id))
    
    session = state["session"]
    node = state["current_node"]
    
    # BUG-022 修复：填充完整的 current_node 字段
    current_node_data = None
    if node:
        current_node_data = {
            "id": str(node.id),
            "type": node.node_type,
            "content": node.content,
            "route_id": str(node.route_id) if hasattr(node, 'route_id') else None,
        }
    
    return {
        "session_id": str(session.id),
        "status": session.status,
        "current_node_id": str(node.id) if node else None,
        "current_node": current_node_data,  # BUG-022: 添加完整节点信息
        "is_ended": state["is_ended"],
        "ending_type": session.ending_type,
    }


@router.get("/game/{session_id}/dialogue")
async def get_dialogue(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get dialogue for current node (non-streaming)."""
    # CRIT-003: verify ownership
    await _verify_session_ownership(UUID(session_id), user_id, db)
    
    engine = NarrativeEngine(db)
    result = await engine.generate_dialogue(
        session_id=UUID(session_id),
        user_id=UUID(user_id),
    )
    
    # BUG-022: 填充 current_node 字段
    # 获取当前节点信息
    state = await engine.script_service.get_game_session_state(UUID(session_id))
    current_node = state.get("current_node")
    
    if current_node:
        result["current_node"] = {
            "id": str(current_node.id),
            "type": current_node.node_type,
            "content": current_node.content,
        }
    
    # BUG-023: 填充旁白字段
    # 从节点内容中提取旁白文本
    if current_node and current_node.content:
        narrator_text = current_node.content.get("narration") or current_node.content.get("narrator_text")
        if narrator_text:
            result["narrator_text"] = narrator_text
            result["narrator_visible"] = True
        else:
            result["narrator_visible"] = False
    else:
        result["narrator_visible"] = False
    
    # CR-016: Add quota status to response (read-only, no deduction for pure reading)
    from app.services.quota_service import QuotaService
    quota_service = QuotaService(db)
    quota_status = await quota_service.get_user_quota_status(UUID(user_id))
    result["remaining_quota"] = quota_status["remaining"]
    result["quota_deducted"] = False  # No deduction for reading
    result["paywall_trigger"] = None  # No paywall for reading
    
    return result


@router.get("/game/{session_id}/dialogue/stream")
async def get_dialogue_stream(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    SSE streaming dialogue endpoint.
    
    Returns Server-Sent Events with dialogue text, emotions, choices, and metadata.
    """
    # CRIT-003: verify ownership
    await _verify_session_ownership(UUID(session_id), user_id, db)
    
    engine = NarrativeEngine(db)
    
    async def event_generator():
        async for event in engine.generate_dialogue_stream(
            session_id=UUID(session_id),
            user_id=UUID(user_id),
        ):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.post("/game/{session_id}/choice")
async def submit_choice(
    session_id: str,
    request: ChoiceRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Submit a player's choice and advance the game."""
    # CRIT-003: verify ownership
    await _verify_session_ownership(UUID(session_id), user_id, db)
    
    # CR-016: Check quota before processing choice (user action = deduct quota)
    from app.services.quota_service import QuotaService
    from app.services.paywall_service import PaywallService
    quota_service = QuotaService(db)
    paywall_service = PaywallService(db)
    
    # Check if user has quota remaining
    quota_status = await quota_service.get_user_quota_status(UUID(user_id))
    quota_exhausted = quota_status["remaining"] == 0 and not quota_status["is_exempt"]
    
    if quota_exhausted:
        # Check if should show paywall
        trigger_result = await paywall_service.check_trigger(UUID(user_id), "T1_quota")
        return {
            "error": "quota_exhausted",
            "message": "对话额度已用完",
            "remaining_quota": 0,
            "paywall_trigger": trigger_result,
        }
    
    engine = NarrativeEngine(db)
    result = await engine.process_choice(
        session_id=UUID(session_id),
        user_id=UUID(user_id),
        choice_id=UUID(request.choice_id),
    )
    
    # CR-016: Consume quota after successful choice
    quota_deducted = False
    if not quota_status["is_exempt"]:
        success = await quota_service.consume_quota(UUID(user_id))
        quota_deducted = success
    
    # Get updated quota status
    updated_quota_status = await quota_service.get_user_quota_status(UUID(user_id))
    result["remaining_quota"] = updated_quota_status["remaining"]
    result["quota_deducted"] = quota_deducted
    
    # Check if should trigger paywall for next action
    paywall_trigger = None
    if updated_quota_status["remaining"] == 0 and not updated_quota_status["is_exempt"]:
        paywall_trigger = await paywall_service.check_trigger(UUID(user_id), "T1_quota")
    result["paywall_trigger"] = paywall_trigger
    
    # DEV-BE-006: Check if convergence point is reached after choice
    from app.services.narrative.convergence_service import convergence_service
    from app.services.narrative.affection_service import AffectionService
    
    # Get session to find character_id
    from app.models.game import GameSession
    from sqlalchemy import select
    session_result = await db.execute(
        select(GameSession).where(GameSession.id == UUID(session_id))
    )
    game_session = session_result.scalar_one_or_none()
    
    if game_session:
        # Get current character (from session metadata or query database)
        character_id = game_session.metadata_json.get("character_id") if game_session.metadata_json else None
        
        if not character_id:
            # Query database for main character of this script
            from app.models.script import Character
            char_result = await db.execute(
                select(Character)
                .where(
                    Character.script_id == game_session.script_id,
                    Character.is_main == True
                )
                .limit(1)
            )
            main_char = char_result.scalar_one_or_none()
            
            if main_char:
                character_id = str(main_char.id)
            else:
                # Fallback: get first character of the script
                char_result = await db.execute(
                    select(Character)
                    .where(Character.script_id == game_session.script_id)
                    .limit(1)
                )
                first_char = char_result.scalar_one_or_none()
                character_id = str(first_char.id) if first_char else "default"
        
        # 收敛检查 - 添加超时保护，不阻塞选择流程
        try:
            import asyncio
            async def _check_and_generate():
                cp = await convergence_service.check_convergence(
                    db=db,
                    session_id=session_id,
                    user_id=user_id,
                    character_id=character_id,
                )
                if cp:
                    affection_svc = AffectionService(db)
                    aff = await affection_svc.get_affection(UUID(user_id), UUID(character_id))
                    affection_value = aff.value if aff else 0
                    convergence_scene = await convergence_service.generate_convergence_scene(
                        convergence_point=cp,
                        user_id=user_id,
                        character_id=character_id,
                        affection_value=affection_value,
                    )
                    result["convergence_reached"] = True
                    result["convergence_point"] = {
                        "id": str(cp.id),
                        "chapter": cp.chapter,
                        "title": cp.title,
                    }
                    result["convergence_narrative"] = convergence_scene.get("narrative", "")
                    result["convergence_choices"] = convergence_scene.get("choices", [])
            
            await asyncio.wait_for(_check_and_generate(), timeout=5.0)
        except asyncio.TimeoutError:
            # 收敛检查超时，跳过，不影响选择流程
            pass
        except Exception:
            # 收敛检查失败，跳过
            pass
    
    return result


@router.post("/game/{session_id}/free-chat")
async def free_chat(
    session_id: str,
    request: FreeChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR-002 AC-058: Free-form conversation endpoint.

    Accepts a user message and returns a contextual AI response with emotion tag.
    """
    from app.services.free_chat_service import get_free_chat_service
    from app.models.game import GameSession
    from sqlalchemy import select

    # Verify session ownership
    await _verify_session_ownership(UUID(session_id), user_id, db)

    # Get session to find character context
    session_result = await db.execute(
        select(GameSession).where(GameSession.id == UUID(session_id))
    )
    game_session = session_result.scalar_one_or_none()
    
    # BUG-020 修复：正确获取角色 ID
    # Route 没有 character_id 字段，应该通过 script_id 获取主角色
    character_id = None
    if game_session:
        from app.models.script import Character
        from sqlalchemy import select
        # 查询该剧本的主角色（is_main=True）
        char_stmt = select(Character).where(
            Character.script_id == game_session.script_id,
            Character.is_main == True
        ).limit(1)
        char_result = await db.execute(char_stmt)
        main_char = char_result.scalar_one_or_none()
        if main_char:
            character_id = str(main_char.id)
        else:
            # 降级：取该剧本的第一个角色
            fallback_stmt = select(Character).where(
                Character.script_id == game_session.script_id
            ).limit(1)
            fallback_result = await db.execute(fallback_stmt)
            fallback_char = fallback_result.scalar_one_or_none()
            if fallback_char:
                character_id = str(fallback_char.id)
            else:
                character_id = "default"
    else:
        character_id = "default"
    
    script_id = str(game_session.script_id) if game_session else None

    svc = get_free_chat_service()

    response = await svc.send_message(
        db=db,
        user_id=user_id,
        character_id=character_id,
        message=request.message,
        script_id=script_id,
        session_id=session_id,
    )

    if "error" in response:
        raise AppException("FREE_CHAT_ERROR", 400, response["error"])

    return {
        "session_id": session_id,
        "reply": response.get("reply", ""),
        "emotion": response.get("emotion", "neutral"),
        "character_id": response.get("character_id"),
    }


@router.get("/game/{session_id}/free-chat/topics")
async def get_free_chat_topics(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get available free chat topics."""
    await _verify_session_ownership(UUID(session_id), user_id, db)
    from app.services.free_chat_service import get_free_chat_service
    svc = get_free_chat_service()
    topics = svc.get_topics()
    return {
        "topics": [
            {"id": t["id"], "label": t["title"], "emoji": "💬", "description": t["description"]}
            for t in topics
        ]
    }


@router.get("/game/{session_id}/free-chat/history")
async def get_free_chat_history(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get free chat message history."""
    await _verify_session_ownership(UUID(session_id), user_id, db)
    from app.services.free_chat_service import get_free_chat_service
    svc = get_free_chat_service()
    
    # 从数据库获取历史记录
    messages = await svc._get_recent_messages(db, session_id, limit=50)
    
    return {
        "messages": [
            {"role": m.get("role"), "content": m.get("content"), "timestamp": m.get("timestamp")}
            for m in messages
        ]
    }


@router.post("/game/{session_id}/custom-input")
async def submit_custom_input(
    session_id: str,
    request: CustomInputRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    DEV-BE-002: 玩家自由输入（走陪伴Agent）。
    
    使用陪伴Agent而非剧情Agent，不推进剧情。
    """
    if not request.text.strip():
        raise AppException("EMPTY_INPUT", 400, "输入不能为空")

    await _verify_session_ownership(UUID(session_id), user_id, db)

    # DEV-BE-002: Use companion agent instead of narrative engine
    from app.services.free_chat_service import free_chat_service
    from app.models.game import GameSession
    from sqlalchemy import select
    
    # Get session to find character context
    session_result = await db.execute(
        select(GameSession).where(GameSession.id == UUID(session_id))
    )
    game_session = session_result.scalar_one_or_none()
    
    # Get character_id from metadata or query database
    character_id = game_session.metadata.get("character_id") if game_session and game_session.metadata else None
    
    if not character_id and game_session:
        # Query database for main character of this script
        from app.models.script import Character
        char_result = await db.execute(
            select(Character)
            .where(
                Character.script_id == game_session.script_id,
                Character.is_main == True
            )
            .limit(1)
        )
        main_char = char_result.scalar_one_or_none()
        
        if main_char:
            character_id = str(main_char.id)
        else:
            # Fallback: get first character of the script
            char_result = await db.execute(
                select(Character)
                .where(Character.script_id == game_session.script_id)
                .limit(1)
            )
            first_char = char_result.scalar_one_or_none()
            character_id = str(first_char.id) if first_char else "default"
    character_id = str(game_session.route_id) if game_session else "default"
    script_id = str(game_session.script_id) if game_session else None
    
    result = await free_chat_service.send_message(
        user_id=user_id,
        character_id=character_id,
        message=request.text.strip(),
        script_id=script_id,
        session_id=session_id,
    )
    
    # Add flag to indicate this doesn't advance plot
    result["advances_plot"] = False
    
    return result


@router.get("/game/{script_id}/route-map")
async def get_route_map(
    script_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR-002 AC-045: Get route exploration map for a script.

    Returns all routes with node graphs, marking explored vs unexplored.
    """
    try:
        script_uuid = UUID(script_id)
        user_uuid = UUID(user_id)
    except (ValueError, AttributeError):
        raise AppException("INVALID_ID", 400, "Invalid script_id or user_id")

    script_service = ScriptService(db)
    result = await script_service.get_route_map(script_uuid, user_uuid)
    return result


@router.post("/game/{session_id}/convergence/check")
async def check_convergence(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    DEV-BE-005: Check if current session has reached a convergence point.
    
    Returns convergence info if reached, otherwise returns reached=false.
    """
    await _verify_session_ownership(UUID(session_id), user_id, db)
    
    from app.services.narrative.convergence_service import convergence_service
    from app.models.game import GameSession
    from sqlalchemy import select
    
    # Get session
    session_result = await db.execute(
        select(GameSession).where(GameSession.id == UUID(session_id))
    )
    game_session = session_result.scalar_one_or_none()
    
    if not game_session:
        return {
            "reached": False,
            "convergence_point": None,
            "rounds_played": 0,
            "rounds_required": 0,
        }
    
    # Use route_id as character proxy
    character_id = str(game_session.route_id)
    
    cp = await convergence_service.check_convergence(
        db=db,
        session_id=session_id,
        user_id=user_id,
        character_id=character_id,
    )
    
    rounds_played = await convergence_service._count_rounds_in_segment(db, session_id)
    
    if cp:
        return {
            "reached": True,
            "convergence_point": {
                "id": str(cp.id),
                "chapter": cp.chapter,
                "title": cp.title,
                "description": cp.description,
            },
            "rounds_played": rounds_played,
            "rounds_required": cp.required_rounds.get(character_id, 4),
        }
    else:
        return {
            "reached": False,
            "convergence_point": None,
            "rounds_played": rounds_played,
            "rounds_required": 0,
        }


@router.post("/game/auto-save")
async def auto_save(
    request: AutoSaveRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """W06: Auto-save game state after choice."""
    from app.models.save import SaveSnapshot
    from app.models.game import GameSession
    from sqlalchemy import select
    from datetime import datetime
    
    # Verify session ownership
    await _verify_session_ownership(UUID(request.session_id), user_id, db)
    
    # Get current session state
    session_result = await db.execute(
        select(GameSession).where(GameSession.id == UUID(request.session_id))
    )
    game_session = session_result.scalar_one_or_none()
    
    if not game_session:
        raise AppException("SESSION_NOT_FOUND", 404, "Game session not found")
    
    # Create or update auto-save snapshot
    # Check if there's an existing auto-save for this session
    existing_save_result = await db.execute(
        select(SaveSnapshot).where(
            SaveSnapshot.user_id == UUID(user_id),
            SaveSnapshot.session_id == UUID(request.session_id),
            SaveSnapshot.label == "auto_save"
        )
    )
    existing_save = existing_save_result.scalar_one_or_none()
    
    if existing_save:
        # Update existing auto-save
        existing_save.current_node_id = UUID(request.node_id)
        existing_save.choice_history = game_session.choice_history or []
        existing_save.metadata_json = {
            "choice_id": request.choice_id,
            "saved_at": datetime.utcnow().isoformat()
        }
        await db.flush()
        save_id = str(existing_save.id)
        saved_at = existing_save.created_at
    else:
        # Create new auto-save
        new_save = SaveSnapshot(
            user_id=UUID(user_id),
            session_id=UUID(request.session_id),
            label="auto_save",
            current_node_id=UUID(request.node_id),
            choice_history=game_session.choice_history or [],
            metadata_json={
                "choice_id": request.choice_id,
                "saved_at": datetime.utcnow().isoformat()
            }
        )
        db.add(new_save)
        await db.flush()
        await db.refresh(new_save)
        save_id = str(new_save.id)
        saved_at = new_save.created_at
    
    return {
        "save_id": save_id,
        "saved_at": saved_at.isoformat() if saved_at else datetime.utcnow().isoformat(),
        "message": "自动存档成功"
    }


@router.post("/game/onboarding")
async def onboarding_dialogue(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    AC-034: First-play onboarding with AI fallback.
    
    Returns dialogue for new users. If AI generation fails (timeout/error),
    automatically uses preset guided script.
    """
    from app.services.onboarding_service import get_onboarding_service
    from app.llm.providers.mock_provider import MockProvider
    
    svc = get_onboarding_service()
    llm = MockProvider()
    
    result = await svc.generate_first_dialogue(
        user_id=user_id,
        llm_provider=llm,
        prompt="Generate welcoming onboarding dialogue for a new player",
        timeout_seconds=5.0,
        db=db,
    )
    
    return result


# ── CR-009 新增接口 ───────────────────────────────────────────────────────────


@router.get("/game/{session_id}/progress")
async def get_game_progress(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR-009: 获取游戏进度数据
    
    返回当前会话的进度信息，用于进度条展示
    """
    from sqlalchemy import select, func
    from app.models.game import GameSession, GameProgress
    from app.models.script import Script, Route, Node
    
    # 验证会话所有权
    stmt = select(GameSession).where(
        GameSession.id == session_id,
        GameSession.user_id == user_id
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise AppException("SESSION_NOT_FOUND", 404, "Game session not found")
    
    # 获取剧本总节点数
    stmt = select(func.count(Node.id)).join(Route).where(Route.script_id == session.script_id)
    result = await db.execute(stmt)
    total_nodes = result.scalar() or 0
    
    # 获取已探索节点数（从 choice_history 中提取）
    explored_nodes = len(session.choice_history) if session.choice_history else 0
    
    # 计算进度百分比
    progress_percentage = (explored_nodes / total_nodes * 100) if total_nodes > 0 else 0
    
    # Count choices from choice_history
    choice_count = explored_nodes  # each entry in choice_history is a choice made
    
    # Count dialogues from user_dialogue_counts
    from app.models.user_dialogue_count import UserDialogueCount
    dialogue_stmt = select(UserDialogueCount.dialogue_count).where(
        UserDialogueCount.user_id == UUID(user_id),
        UserDialogueCount.script_id == session.script_id,
    )
    dialogue_result = await db.execute(dialogue_stmt)
    dialogue_count = dialogue_result.scalar() or 0
    
    return {
        "session_id": str(session.id),
        "script_id": str(session.script_id),
        "current_node_id": str(session.current_node_id) if session.current_node_id else None,
        "total_nodes": total_nodes,
        "explored_nodes": explored_nodes,
        "completion_rate": round(progress_percentage, 2),
        "progress_percentage": round(progress_percentage, 2),
        "choice_count": choice_count,
        "dialogue_count": dialogue_count,
        "status": session.status
    }


@router.get("/game/{session_id}/status")
async def get_game_status(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    BE-O2: 获取游戏状态 — 返回剧本名称、角色名称、好感度。
    """
    from sqlalchemy import select
    from app.models.game import GameSession
    from app.models.script import Script, Character
    from app.models.affection import Affection
    
    # Verify session ownership
    stmt = select(GameSession).where(
        GameSession.id == UUID(session_id),
        GameSession.user_id == UUID(user_id)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise AppException("SESSION_NOT_FOUND", 404, "Game session not found")
    
    # Get script name
    stmt = select(Script.title).where(Script.id == session.script_id)
    result = await db.execute(stmt)
    script_name = result.scalar_one_or_none() or "未知剧本"
    
    # Get main character for this script
    stmt = select(Character).where(
        Character.script_id == session.script_id,
        Character.is_main == True
    ).limit(1)
    result = await db.execute(stmt)
    character = result.scalar_one_or_none()
    
    character_name = character.name if character else "未知角色"
    character_id = str(character.id) if character else None
    
    # Get affection for this character
    affection_value = 0
    affection_level = "neutral"
    if character_id:
        aff_stmt = select(Affection).where(
            Affection.user_id == UUID(user_id),
            Affection.character_id == character.id
        )
        aff_result = await db.execute(aff_stmt)
        aff = aff_result.scalar_one_or_none()
        if aff:
            affection_value = aff.value
            affection_level = aff.level
    
    return {
        "session_id": str(session.id),
        "script_id": str(session.script_id),
        "script_name": script_name,
        "character_id": character_id,
        "character_name": character_name,
        "affection_value": affection_value,
        "affection_level": affection_level,
        "status": session.status,
        "current_node_id": str(session.current_node_id) if session.current_node_id else None,
    }


@router.get("/game/{session_id}/history")
async def get_game_history(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR-009: 获取游戏历史记录
    
    返回当前会话的对话和选择历史
    """
    from sqlalchemy import select
    from app.models.game import GameSession
    
    # 验证会话所有权
    stmt = select(GameSession).where(
        GameSession.id == session_id,
        GameSession.user_id == user_id
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise AppException("SESSION_NOT_FOUND", 404, "Game session not found")
    
    # 从 choice_history 构建历史记录
    history = []
    if session.choice_history:
        for i, entry in enumerate(session.choice_history):
            history.append({
                "index": i,
                "node_id": entry.get("node_id"),
                "choice_id": entry.get("choice_id"),
                "choice_text": entry.get("choice_text"),
                "timestamp": entry.get("timestamp")
            })
    
    return {
        "session_id": str(session.id),
        "history": history,
        "total_entries": len(history)
    }


# ── BE-O3: Dialogue History Storage API ──────────────────────────────────────

from pydantic import BaseModel

class StoreDialogueRequest(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    character_id: str | None = None
    character_name: str | None = None
    emotion: str | None = None


@router.post("/game/{session_id}/dialogue")
async def store_dialogue(
    session_id: str,
    request: StoreDialogueRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    BE-O3: Store a dialogue message for a game session.
    Stores user input or AI reply with timestamp.
    """
    from sqlalchemy import select
    from app.models.game import GameSession, DialogueHistory
    
    # Verify session ownership
    stmt = select(GameSession).where(
        GameSession.id == UUID(session_id),
        GameSession.user_id == UUID(user_id)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise AppException("SESSION_NOT_FOUND", 404, "Game session not found")
    
    # Create dialogue record
    dialogue = DialogueHistory(
        session_id=UUID(session_id),
        user_id=UUID(user_id),
        role=request.role,
        content=request.content,
        character_id=UUID(request.character_id) if request.character_id else None,
        character_name=request.character_name,
        emotion=request.emotion,
    )
    db.add(dialogue)
    await db.commit()
    await db.refresh(dialogue)
    
    return {
        "id": str(dialogue.id),
        "session_id": str(dialogue.session_id),
        "role": dialogue.role,
        "content": dialogue.content,
        "character_id": str(dialogue.character_id) if dialogue.character_id else None,
        "character_name": dialogue.character_name,
        "emotion": dialogue.emotion,
        "created_at": dialogue.created_at.isoformat(),
    }


@router.get("/game/{session_id}/dialogues")
async def get_dialogues(
    session_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    BE-O3: Query dialogue history for a game session.
    Returns messages ordered by created_at ASC.
    """
    from sqlalchemy import select, func
    from app.models.game import GameSession, DialogueHistory
    
    # Verify session ownership
    stmt = select(GameSession).where(
        GameSession.id == UUID(session_id),
        GameSession.user_id == UUID(user_id)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise AppException("SESSION_NOT_FOUND", 404, "Game session not found")
    
    # Count total
    count_stmt = select(func.count(DialogueHistory.id)).where(
        DialogueHistory.session_id == UUID(session_id)
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0
    
    # Fetch dialogues
    stmt = (
        select(DialogueHistory)
        .where(DialogueHistory.session_id == UUID(session_id))
        .order_by(DialogueHistory.created_at.asc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    dialogues = result.scalars().all()
    
    return {
        "dialogues": [
            {
                "id": str(d.id),
                "session_id": str(d.session_id),
                "role": d.role,
                "content": d.content,
                "character_id": str(d.character_id) if d.character_id else None,
                "character_name": d.character_name,
                "emotion": d.emotion,
                "created_at": d.created_at.isoformat(),
            }
            for d in dialogues
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/users/me/game-stats")
async def get_user_game_stats(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR-009: 获取用户游戏统计
    
    返回用户的游戏统计数据，用于个人中心展示
    """
    from sqlalchemy import select, func
    from app.models.game import GameSession
    from datetime import datetime, timezone
    
    # 总会话数
    stmt = select(func.count(GameSession.id)).where(GameSession.user_id == user_id)
    result = await db.execute(stmt)
    total_sessions = result.scalar() or 0
    
    # 已完成会话数
    stmt = select(func.count(GameSession.id)).where(
        GameSession.user_id == user_id,
        GameSession.status == "completed"
    )
    result = await db.execute(stmt)
    completed_sessions = result.scalar() or 0
    
    # 总选择次数（从所有会话的 choice_history 累加）
    stmt = select(GameSession.choice_history).where(GameSession.user_id == user_id)
    result = await db.execute(stmt)
    total_choices = 0
    for row in result:
        if row[0]:
            total_choices += len(row[0])
    
    # 总游戏时长（估算：每个选择约2分钟）
    total_play_time_minutes = total_choices * 2
    
    # 总对话次数（从 user_dialogue_counts 累加）
    from app.models.user_dialogue_count import UserDialogueCount
    dialogue_stmt = select(func.sum(UserDialogueCount.dialogue_count)).where(
        UserDialogueCount.user_id == UUID(user_id)
    )
    dialogue_result = await db.execute(dialogue_stmt)
    total_dialogues = dialogue_result.scalar() or 0
    
    # 最喜欢的角色（按好感度）
    from app.models.affection import Affection
    from app.models.script import Character
    fav_stmt = (
        select(Affection.character_id, Affection.value)
        .where(Affection.user_id == UUID(user_id))
        .order_by(Affection.value.desc())
        .limit(1)
    )
    fav_result = await db.execute(fav_stmt)
    fav_row = fav_result.first()
    
    favorite_character_id = str(fav_row[0]) if fav_row else None
    favorite_character_name = None
    
    if fav_row:
        char_stmt = select(Character.name).where(Character.id == fav_row[0])
        char_result = await db.execute(char_stmt)
        favorite_character_name = char_result.scalar_one_or_none()
    
    # 最常玩的游戏（按会话数）
    stmt = select(
        GameSession.script_id,
        func.count(GameSession.id).label('count')
    ).where(
        GameSession.user_id == user_id
    ).group_by(
        GameSession.script_id
    ).order_by(
        func.count(GameSession.id).desc()
    ).limit(1)
    result = await db.execute(stmt)
    favorite_script_row = result.first()
    
    favorite_script_id = str(favorite_script_row[0]) if favorite_script_row else None
    favorite_script_name = None
    
    if favorite_script_id:
        from app.models.script import Script
        stmt = select(Script.title).where(Script.id == favorite_script_id)
        result = await db.execute(stmt)
        favorite_script_name = result.scalar_one_or_none()
    
    return {
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
        "total_choices": total_choices,
        "total_dialogues": total_dialogues,
        "total_play_time_minutes": total_play_time_minutes,
        "favorite_character_id": favorite_character_id,
        "favorite_character_name": favorite_character_name,
        "favorite_script_id": favorite_script_id,
        "favorite_script_name": favorite_script_name
    }


@router.get("/users/me/latest-session")
async def get_latest_session(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR-009: 获取最近的游戏会话
    
    返回用户最近的游戏会话，用于快速继续游戏
    """
    from sqlalchemy import select
    from app.models.game import GameSession
    from app.models.script import Script
    
    # 获取最近的活跃会话（未完成）
    stmt = select(GameSession).where(
        GameSession.user_id == user_id,
        GameSession.status == "active"
    ).order_by(
        GameSession.started_at.desc()
    ).limit(1)
    
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        return {
            "session_id": None,
            "script_id": None,
            "script_name": None,
            "current_node_id": None,
            "started_at": None
        }
    
    # 获取剧本信息
    stmt = select(Script.title).where(Script.id == session.script_id)
    result = await db.execute(stmt)
    script_name = result.scalar_one_or_none()
    
    return {
        "session_id": str(session.id),
        "script_id": str(session.script_id),
        "script_name": script_name,
        "current_node_id": str(session.current_node_id) if session.current_node_id else None,
        "started_at": session.started_at.isoformat() if session.started_at else None
    }
