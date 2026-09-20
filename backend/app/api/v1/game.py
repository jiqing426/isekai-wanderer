"""Game session API endpoints including SSE streaming dialogue."""

import json
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException, ErrorCode
from app.services.narrative import NarrativeEngine
from app.services.narrative.script_service import ScriptService
from app.services.subscription_service import SubscriptionService
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
    character_id: Optional[str] = None  # CR-028: Optional character for role-playing


class ChoiceRequest(BaseModel):
    choice_id: str


class CustomInputRequest(BaseModel):
    text: str


class FreeChatRequest(BaseModel):
    message: str
    topic_id: Optional[str] = None


async def _run_deferred(data: dict) -> None:
    """Run deferred DB operations after Corvus SSE stream completes."""
    from app.core.database import async_session_factory
    from app.services.corvus_adapter import CorvusAdapter
    import logging
    log = logging.getLogger(__name__)
    log.info(f"[Deferred] Starting: {len(data.get('gm_updates',[]))} gm_updates, {len(data.get('done_texts',[]))} done_texts")
    try:
        # Restore NPC knownInfo
        if data.get("restore_list") and data.get("corvus_game_id"):
            try:
                async with async_session_factory() as db:
                    adapter = CorvusAdapter(db)
                    await adapter.restore_npc_knowninfo(data["corvus_game_id"], data["restore_list"])
                    await db.commit()
                    log.info("[Deferred] NPC knownInfo restored")
            except Exception as e:
                log.error(f"[Deferred] restore_npc_knowninfo: {e}", exc_info=True)
        # Sync world state
        for gm_event in data.get("gm_updates", []):
            try:
                async with async_session_factory() as db:
                    adapter = CorvusAdapter(db)
                    await adapter.sync_world_state(data["session_id"], gm_event)
                    await db.commit()
                    log.info("[Deferred] sync_world_state done")
            except Exception as e:
                log.error(f"[Deferred] sync_world_state: {e}", exc_info=True)
        # Write memories
        for done_text in data.get("done_texts", []):
            try:
                async with async_session_factory() as db:
                    adapter = CorvusAdapter(db)
                    await adapter.write_memory(
                        user_id=data["user_id"],
                        character_id=data["char_id"],
                        dialogue_text=done_text,
                        game_session_id=data["session_id"],
                    )
                    await db.commit()
                    log.info("[Deferred] write_memory done")
            except Exception as e:
                log.error(f"[Deferred] write_memory: {e}", exc_info=True)
    except Exception as e:
        log.error(f"[Deferred] failed: {e}", exc_info=True)


def _stream_corvus_turn(
    session_uuid: UUID,
    user_uuid: UUID,
    text: str,
    db: AsyncSession,
):
    """CR-037 DEV-004: Stream a Corvus game turn via SSE.

    Returns a StreamingResponse with text/event-stream content type.
    Translates Corvus SSE events to frontend format via SSETranslator.
    This is a sync function that returns a StreamingResponse wrapping an
    async generator — FastAPI handles the async iteration internally.
    """
    from app.services.corvus_adapter import CorvusAdapter
    import asyncio

    adapter = CorvusAdapter(db)

    deferred_data = {"gm_updates": [], "done_texts": [], "char_id": None, "user_id": user_uuid, "session_id": session_uuid, "restore_list": [], "corvus_game_id": None}

    async def event_generator():
        try:
            async for sse_line in adapter.stream_turn(
                game_session_id=session_uuid,
                user_id=user_uuid,
                user_input=text,
            ):
                yield sse_line
        finally:
            import asyncio
            import logging as _lg
            _lg = _lg.getLogger(__name__)
            try:
                if hasattr(adapter, '_collected_gm_updates'):
                    deferred_data["gm_updates"] = adapter._collected_gm_updates
                if hasattr(adapter, '_collected_done_texts'):
                    deferred_data["done_texts"] = adapter._collected_done_texts
                if hasattr(adapter, '_char_id'):
                    deferred_data["char_id"] = adapter._char_id
                if hasattr(adapter, '_restore_list'):
                    deferred_data["restore_list"] = adapter._restore_list
                if hasattr(adapter, '_corvus_game_id'):
                    deferred_data["corvus_game_id"] = adapter._corvus_game_id
                _lg.info("[SSE-FINALLY] Scheduling _run_deferred")
                loop = asyncio.get_event_loop()
                loop.create_task(_run_deferred(deferred_data))
            except Exception as e:
                _lg.error(f"[SSE-FINALLY] Error: {e}", exc_info=True)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---- CR-043 Script access permission helpers ----

def _compute_script_accessible(script_access: str, script) -> bool:
    """CR-043 AC-005~008: Compute whether a script is accessible based on user's tier.
    
    Mapping (ADR-042-02):
    - trial_only (free): genre == 'romance' AND hot_value >= 50
    - all_normal (basic/standard): all scripts (no exclusive scripts currently exist)
    - all_including_exclusive (premium): all scripts
    """
    if script_access == "all_including_exclusive":
        return True
    if script_access == "all_normal":
        return True  # Currently no exclusive scripts; future: AND NOT script.is_exclusive
    if script_access == "trial_only":
        genre = getattr(script, 'genre', None) or ''
        hot_value = getattr(script, 'hot_value', None) or 0
        return genre == 'romance' and hot_value >= 50
    return False  # Unknown access level — safe deny


# ---- CR-042 Legacy SSE streaming helpers ----

import json as _json
import logging as _logging

_legacy_log = _logging.getLogger(__name__)


def _stream_legacy_turn(
    session_uuid: UUID,
    user_uuid: UUID,
    choice_result: dict,
    next_node: Node,
    db: AsyncSession,
) -> StreamingResponse:
    """CR-042 AC-001: Stream a Legacy engine turn via SSE for transition/ai_dialog nodes.

    Calls llm_gateway.stream_dialogue() to get tokens and wraps them as SSE events.
    DB writes happen in a deferred task after the stream completes.
    """
    from app.services.llm.gateway import llm_gateway
    import asyncio

    # Pre-extract node data to avoid DB access inside the async generator (greenlet safe)
    _node_id_str = str(next_node.id) if next_node else None
    _node_content = dict(next_node.content) if next_node and next_node.content else {}
    _node_choices = _node_content.get('choices', []) if _node_content else []

    deferred_data = {
        "session_id": session_uuid,
        "user_id": user_uuid,
        "choice_result": choice_result,
        "next_node_id": next_node.id if next_node else None,
        "text_chunks": [],
        "char_id": None,
        "char_name": None,
    }

    async def event_generator():
        try:
            # Get character info — use db execute which is safe in this context
            character = await _get_node_character(next_node, db)
            if character:
                deferred_data["char_id"] = character.id
                deferred_data["char_name"] = character.name
                # Push emotion event
                yield f'data: {_json.dumps({"type":"emotion","emotion":"neutral","character_id":str(character.id)})}\n\n'

            # Stream dialogue tokens
            if character:
                # Get conversation history — use try/except for test env safety
                try:
                    conv_history = await _get_conversation_history(db, session_uuid, limit=5)
                except Exception:
                    conv_history = []

                async for chunk in llm_gateway.stream_dialogue(
                    character_name=character.name,
                    character_personality=str(character.personality or ""),
                    context=_node_content.get("context", ""),
                    user_input=choice_result.get("choice_text", ""),
                    conversation_history=conv_history,
                ):
                    deferred_data["text_chunks"].append(chunk)
                    yield f'data: {_json.dumps({"type":"text","content":chunk})}\n\n'
            else:
                # No character — use narrator text from pre-extracted content
                narrator_text = _node_content.get("text", "")
                if narrator_text:
                    # Yield narrator text as a single chunk
                    deferred_data["text_chunks"].append(narrator_text)
                    yield f'data: {_json.dumps({"type":"text","content":narrator_text})}\n\n'

            # Done event with metadata
            done_payload = {
                "type": "done",
                "session_id": str(session_uuid),
                "node_id": _node_id_str,
            }
            # Add affection_change if present
            if choice_result.get("affection_change"):
                done_payload["affection_change"] = choice_result["affection_change"]
            # Add choices if available (pre-extracted to avoid lazy-loading)
            if _node_choices:
                done_payload["choices"] = _node_choices

            yield f'data: {_json.dumps(done_payload, default=str)}\n\n'

        except Exception as e:
            _legacy_log.error(f"[Legacy SSE choice] Error: {e}", exc_info=True)
            yield f'data: {_json.dumps({"type":"error","message":str(e)})}\n\n'
        finally:
            # Deferred DB write — happens after stream completes
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(_run_legacy_deferred(deferred_data))
            except Exception as e:
                _legacy_log.error(f"[Legacy SSE choice] Failed to schedule deferred: {e}", exc_info=True)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _get_node_character(node: Node, db: AsyncSession) -> Optional[Character]:
    """Get the character associated with a node (via route → script → main character)."""
    try:
        # Get route to find script_id
        route_stmt = select(Route).where(Route.id == node.route_id)
        route_result = await db.execute(route_stmt)
        route = route_result.scalar_one_or_none()
        if not route:
            return None

        # Find main character for this script
        char_stmt = (
            select(Character)
            .where(
                Character.script_id == route.script_id,
                Character.is_main == True,
            )
            .limit(1)
        )
        char_result = await db.execute(char_stmt)
        return char_result.scalar_one_or_none()
    except Exception as e:
        _legacy_log.warning(f"[_get_node_character] Error: {e}")
        return None


async def _get_conversation_history(db: AsyncSession, session_uuid: UUID, limit: int = 5) -> list:
    """Get recent conversation history for context."""
    try:
        from app.models.game import DialogueHistory
        stmt = (
            select(DialogueHistory)
            .where(DialogueHistory.session_id == session_uuid)
            .order_by(DialogueHistory.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        messages = result.scalars().all()
        # Return in chronological order (reversed)
        messages = list(reversed(messages))
        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
    except Exception as e:
        _legacy_log.warning(f"[_get_conversation_history] Error: {e}")
        return []


def _format_legacy_choices(choices) -> list:
    """Format node choices for SSE done event."""
    formatted = []
    if isinstance(choices, list):
        for c in choices:
            if isinstance(c, dict):
                formatted.append(c)
            elif hasattr(c, 'id') and hasattr(c, 'text'):
                formatted.append({"id": str(c.id), "text": c.text})
    return formatted


async def _run_legacy_deferred(data: dict) -> None:
    """CR-042 AC-004: Deferred DB write after Legacy SSE stream completes.

    Writes dialogue history, affection updates, and achievement checks
    in an independent DB session so it doesn't block the SSE stream.
    """
    from app.core.database import async_session_factory
    from app.models.game import DialogueHistory

    try:
        async with async_session_factory() as db:
            session_uuid = data["session_id"]
            user_uuid = data["user_id"]
            char_id = data.get("char_id")
            char_name = data.get("char_name")
            text_chunks = data.get("text_chunks", [])
            choice_result = data.get("choice_result", {})

            # Write user choice as dialogue history
            choice_text = choice_result.get("choice_text", "")
            if choice_text:
                db.add(DialogueHistory(
                    session_id=session_uuid,
                    user_id=user_uuid,
                    role="user",
                    content=choice_text,
                    character_id=char_id,
                    character_name=char_name,
                ))

            # Write assistant response
            full_text = "".join(text_chunks)
            if full_text:
                db.add(DialogueHistory(
                    session_id=session_uuid,
                    user_id=user_uuid,
                    role="assistant",
                    content=full_text,
                    character_id=char_id,
                    character_name=char_name,
                ))

            # Update affection if change is present
            affection_change = choice_result.get("affection_change")
            if affection_change and char_id:
                try:
                    from app.services.narrative.affection_service import AffectionService
                    affection_svc = AffectionService(db)
                    value = affection_change.get("value", 0)
                    if value:
                        await affection_svc.update_affection(
                            user_id=user_uuid,
                            character_id=char_id,
                            change=value,
                        )
                except Exception as e:
                    _legacy_log.warning(f"[Deferred] Affection update failed: {e}")

            # Update session current_node_id
            next_node_id = data.get("next_node_id")
            if next_node_id:
                session_stmt = select(GameSession).where(GameSession.id == session_uuid)
                session_result = await db.execute(session_stmt)
                game_session = session_result.scalar_one_or_none()
                if game_session:
                    game_session.current_node_id = next_node_id

            await db.commit()
            _legacy_log.info(f"[Deferred] Legacy choice DB write done for session {session_uuid}")

    except Exception as e:
        _legacy_log.error(f"[Deferred] Legacy choice failed: {e}", exc_info=True)


def _stream_legacy_custom_input(
    session_uuid: UUID,
    user_uuid: UUID,
    user_text: str,
    node: Node,
    character: Optional[Character],
    db: AsyncSession,
) -> StreamingResponse:
    """CR-042 AC-006: Stream Legacy custom input response via SSE.

    Uses llm_gateway.stream_dialogue() instead of _generate_custom_response().
    DB writes happen in a deferred task after the stream completes.
    """
    from app.services.llm.gateway import llm_gateway
    import asyncio

    deferred_data = {
        "session_id": session_uuid,
        "user_id": user_uuid,
        "user_text": user_text,
        "node_id": node.id if node else None,
        "text_chunks": [],
        "char_id": character.id if character else None,
        "char_name": character.name if character else None,
    }

    async def event_generator():
        try:
            if character:
                # Push emotion event
                yield f'data: {_json.dumps({"type":"emotion","emotion":"neutral","character_id":str(character.id)})}\n\n'

                # Get conversation history
                conv_history = await _get_conversation_history(db, session_uuid, limit=5)

                # AC-007: Use stream_dialogue() instead of _generate_custom_response()
                async for chunk in llm_gateway.stream_dialogue(
                    character_name=character.name,
                    character_personality=str(character.personality or ""),
                    context=str(node.content.get("context", "")) if node and node.content else "",
                    user_input=user_text,
                    conversation_history=conv_history,
                ):
                    deferred_data["text_chunks"].append(chunk)
                    yield f'data: {_json.dumps({"type":"text","content":chunk})}\n\n'
            else:
                # No character — use narrator stream via provider
                from app.services.llm.gateway import LLMMessage
                messages = [
                    LLMMessage(role="system", content="You are a narrator in an interactive story."),
                    LLMMessage(role="user", content=user_text),
                ]
                async for chunk in llm_gateway.provider.stream_complete(
                    messages, temperature=0.7, max_tokens=500
                ):
                    deferred_data["text_chunks"].append(chunk)
                    yield f'data: {_json.dumps({"type":"text","content":chunk})}\n\n'

            # Done event
            done_payload = {
                "type": "done",
                "session_id": str(session_uuid),
                "node_id": str(node.id) if node else None,
            }
            yield f'data: {_json.dumps(done_payload, default=str)}\n\n'

        except Exception as e:
            _legacy_log.error(f"[Legacy SSE custom-input] Error: {e}", exc_info=True)
            yield f'data: {_json.dumps({"type":"error","message":str(e)})}\n\n'
        finally:
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(_run_legacy_custom_input_deferred(deferred_data))
            except Exception as e:
                _legacy_log.error(f"[Legacy SSE custom-input] Failed to schedule deferred: {e}", exc_info=True)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


async def _run_legacy_custom_input_deferred(data: dict) -> None:
    """CR-042 AC-009: Deferred DB write after Legacy custom-input SSE stream.

    Writes user message and assistant response to DialogueHistory,
    and updates affection if applicable.
    """
    from app.core.database import async_session_factory
    from app.models.game import DialogueHistory

    try:
        async with async_session_factory() as db:
            session_uuid = data["session_id"]
            user_uuid = data["user_id"]
            user_text = data.get("user_text", "")
            text_chunks = data.get("text_chunks", [])
            char_id = data.get("char_id")
            char_name = data.get("char_name")

            # Write user message
            if user_text:
                db.add(DialogueHistory(
                    session_id=session_uuid,
                    user_id=user_uuid,
                    role="user",
                    content=user_text,
                    character_id=char_id,
                    character_name=char_name,
                ))

            # Write assistant response
            full_text = "".join(text_chunks)
            if full_text:
                db.add(DialogueHistory(
                    session_id=session_uuid,
                    user_id=user_uuid,
                    role="assistant",
                    content=full_text,
                    character_id=char_id,
                    character_name=char_name,
                ))

            await db.commit()
            _legacy_log.info(f"[Deferred] Legacy custom-input DB write done for session {session_uuid}")

    except Exception as e:
        _legacy_log.error(f"[Deferred] Legacy custom-input failed: {e}", exc_info=True)


async def _get_corvus_dialogue(corvus_session, user_id: str):
    """CR-037 DEV-007: Get dialogue for a Corvus session (non-streaming).
    
    Maps CorvusClient.get_game() result to a frontend-compatible DialogueResponse.
    Used by GET /game/{session_id}/dialogue when engine_type=corvus.
    """
    from app.services.corvus_client import get_corvus_client
    from app.core.exceptions import AppException
    
    # Verify ownership
    if corvus_session.user_id != UUID(user_id):
        raise AppException("SESSION_FORBIDDEN", 403, "Access denied: you do not own this session")
    if corvus_session.status != "playing":
        raise AppException("SESSION_INVALID_STATUS", 400, f"Session status is '{corvus_session.status}', expected 'playing'")
    if not corvus_session.corvus_internal_game_id:
        raise AppException("CORVUS_GAME_ID_MISSING", 500, "Session has no corvus_internal_game_id")
    
    client = get_corvus_client()
    try:
        game_state = await client.get_game(corvus_session.corvus_internal_game_id)
    except Exception as e:
        raise AppException("CORVUS_GET_GAME_FAILED", 503, f"Failed to get Corvus game state: {e}")
    
    # Map Corvus game state to frontend-compatible response
    config = game_state.get("config", {})
    world = game_state.get("world", {})
    
    return {
        "type": "dialogue",
        "text": None,  # Corvus doesn't have preset dialogue; text comes via SSE
        "session_id": str(corvus_session.id),
        "status": corvus_session.status,
        "engine_type": "corvus",
        "corvus_game_id": corvus_session.corvus_internal_game_id,
        "world_setting": world.get("setting", ""),
        "world_tone": world.get("tone", ""),
        "game_name": config.get("name", ""),
        # Corvus sessions don't have preset choices — free input
        "choices": [],
        # No node-based progress for Corvus
        "current_node": None,
        "narrator_visible": False,
    }


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
    logger.info(f"[game/start] Received request: script_id={request.script_id}, route_id={request.route_id}, character_id={request.character_id}")
    
    # Validate script_id UUID
    try:
        script_uuid = UUID(request.script_id)
    except (ValueError, AttributeError):
        raise AppException("INVALID_SCRIPT_ID", 400, f"Invalid script_id: {request.script_id}")
    
    script_service = ScriptService(db)
    
    # CR-043 AC-005/AC-015: Check script_access permission before starting game
    sub_service = SubscriptionService(db)
    user_tier = await sub_service.get_user_tier(UUID(user_id))
    user_perms = await sub_service.get_tier_permissions(user_tier)
    script_access = user_perms.script_access
    
    # Get script to check accessibility
    script_stmt = select(Script).where(Script.id == script_uuid)
    script_result = await db.execute(script_stmt)
    script_obj = script_result.scalar_one_or_none()
    
    if not script_obj:
        raise AppException("SCRIPT_NOT_FOUND", 404, f"Script {request.script_id} not found")
    
    if not _compute_script_accessible(script_access, script_obj):
        import logging
        logging.getLogger(__name__).warning(
            f"[SCRIPT_ACCESS_DENIED] user={user_id}, script={script_uuid}, tier={user_tier}, access={script_access}"
        )
        raise AppException(
            "SCRIPT_ACCESS_DENIED", 403,
            "当前订阅等级无法游玩此剧本，请升级订阅"
        )
    
    # CR-028: Handle character_id for role-playing
    character_id = None
    character_name = None
    if request.character_id:
        try:
            character_id = UUID(request.character_id)
        except (ValueError, AttributeError):
            raise AppException("INVALID_CHARACTER_ID", 400, f"Invalid character_id: {request.character_id}")
        
        # Validate character exists and is playable
        from app.models.script import Character
        char_stmt = select(Character).where(Character.id == character_id)
        char_result = await db.execute(char_stmt)
        character = char_result.scalar_one_or_none()
        
        if not character:
            raise AppException("CHARACTER_NOT_FOUND", 404, f"Character {character_id} not found")
        
        if not character.playable:
            raise AppException("CHARACTER_NOT_PLAYABLE", 400, f"Character {character_id} is not playable")
        
        if not character.playable_route_id:
            raise AppException("CHARACTER_NO_ROUTE", 400, f"Character {character_id} has no playable route")
        
        # Use character's playable_route_id
        route_id = character.playable_route_id
        character_name = character.name
        logger.info(f"[game/start] Using character {character_name} with route {route_id}")
    
    # Get starting node
    if request.route_id and not character_id:
        # If character_id is provided, ignore route_id parameter
        try:
            route_id = UUID(request.route_id)
        except (ValueError, AttributeError):
            raise AppException("INVALID_ROUTE_ID", 400, f"Invalid route_id: {request.route_id}")
    elif not character_id:
        # Get first route of script
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
    
    # 检查是否已有活跃会话（支持进度恢复）
    from app.models.game import GameSession
    
    stmt = (
        select(GameSession)
        .where(
            GameSession.user_id == UUID(user_id),
            GameSession.script_id == script_uuid,
            GameSession.status == 'active'
        )
        .order_by(GameSession.started_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    existing_session = result.scalar_one_or_none()
    
    # 如果指定了 route_id 或 character_id 且与现有会话不同，创建新会话
    if existing_session and (request.route_id or character_id):
        route_changed = request.route_id and str(existing_session.route_id) != request.route_id
        character_changed = character_id and str(existing_session.character_id) != str(character_id)
        if route_changed or character_changed:
            # 标记旧会话为 completed（保存进度）
            existing_session.status = 'completed'
            existing_session.completed_at = datetime.utcnow()
            await db.commit()
            logger.info(f"[game/start] Marked old session {existing_session.id} as completed, creating new session")
            existing_session = None
    
    if existing_session:
        # 恢复已有会话
        logger.info(f"[game/start] Resuming existing session: {existing_session.id}")
        return {
            "session_id": str(existing_session.id),
            "node_id": str(existing_session.current_node_id),
            "message": "Game resumed",
            "resumed": True
        }
    
    # Create session
    session = GameSession(
        user_id=UUID(user_id),
        script_id=script_uuid,
        route_id=route_id,
        current_node_id=starting_node.id,
        custom_name=request.custom_name,
        character_id=character_id,  # CR-028: Store character_id
        character_name=character_name,  # CR-028: Store character_name snapshot
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return {
        "session_id": str(session.id),
        "node_id": str(starting_node.id),
        "message": "Game started",
        "resumed": False,
        "character_id": str(character_id) if character_id else None,  # CR-028
        "character_name": character_name,  # CR-028
    }


async def _verify_session_ownership(session_id: UUID, user_id: str, db: AsyncSession) -> None:
    """CRIT-003 fix: Verify current user owns the game session.

    CR-039 D8: Also checks CorvusGameSession table for Corvus engine sessions.
    """
    from app.models.game import GameSession
    from app.models.corvus import CorvusGameSession

    # First check CorvusGameSession (Corvus engine sessions)
    corvus_stmt = select(CorvusGameSession).where(
        CorvusGameSession.id == session_id
    )
    corvus_result = await db.execute(corvus_stmt)
    corvus_session = corvus_result.scalar_one_or_none()

    if corvus_session:
        # Corvus session found — verify ownership
        if str(corvus_session.user_id) != user_id:
            raise AppException("SESSION_FORBIDDEN", 403, "Access denied: you do not own this session")
        return

    # Fallback: check Legacy GameSession table
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
    """Get current game session state.
    
    CR-038 BUG-038-005: Check both GameSession (legacy) and CorvusGameSession tables.
    """
    # CR-038: First check if this is a Corvus engine session
    from app.models.corvus import CorvusGameSession
    try:
        session_uuid = UUID(session_id)
        corvus_stmt = select(CorvusGameSession).where(
            CorvusGameSession.id == session_uuid
        )
        corvus_result = await db.execute(corvus_stmt)
        corvus_session = corvus_result.scalar_one_or_none()
        
        if corvus_session and corvus_session.engine_type == "corvus":
            # Verify ownership
            if corvus_session.user_id != UUID(user_id):
                raise AppException("AUTH_FORBIDDEN", 403, "Not your session")
            
            return {
                "session_id": str(corvus_session.id),
                "script_id": None,
                "character_id": None,
                "character_name": None,
                "route_id": None,
                "status": corvus_session.status,
                "current_node_id": None,
                "current_node": None,
                "is_ended": corvus_session.status == "completed",
                "ending_type": None,
                "engine_type": "corvus",
            }
    except (ValueError, AttributeError):
        pass  # Not a UUID, fallback to legacy
    
    # Legacy session path
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
        "script_id": str(session.script_id) if session.script_id else None,
        "character_id": str(session.character_id) if session.character_id else None,
        "character_name": session.character_name,
        "route_id": str(session.route_id) if hasattr(session, 'route_id') and session.route_id else None,
        "status": session.status,
        "current_node_id": str(node.id) if node else None,
        "current_node": current_node_data,  # BUG-022: 添加完整节点信息
        "is_ended": state["is_ended"],
        "ending_type": session.ending_type,
        "engine_type": "legacy",
    }


@router.get("/game/{session_id}/dialogue")
async def get_dialogue(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get dialogue for current node (non-streaming).
    
    CR-037 DEV-007: Engine Dispatcher — Corvus sessions use CorvusClient.get_game()
    to map to DialogueResponse. Legacy sessions use NarrativeEngine.
    """
    # CR-037: Check if this is a Corvus engine session
    from app.models.corvus import CorvusGameSession
    try:
        session_uuid = UUID(session_id)
        corvus_stmt = select(CorvusGameSession).where(
            CorvusGameSession.id == session_uuid
        )
        corvus_result = await db.execute(corvus_stmt)
        corvus_session = corvus_result.scalar_one_or_none()
        
        if corvus_session and corvus_session.engine_type == "corvus":
            # AC-020: Corvus engine path
            return await _get_corvus_dialogue(corvus_session, user_id)
    except (ValueError, AttributeError):
        pass  # Not a UUID, fallback to legacy
    
    # AC-019: Legacy engine path (unchanged)
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
    
    # 添加章节信息（从当前节点所属 route 获取）
    if current_node:
        # 获取当前节点所属 route
        from app.models.script import Route
        route_stmt = select(Route).where(Route.id == current_node.route_id)
        route_result = await db.execute(route_stmt)
        route = route_result.scalar_one_or_none()
        if route:
            result["chapter"] = route.title
            result["chapter_id"] = str(route.id)
            
            # 检查是否有下一章节
            all_routes_stmt = select(Route).where(Route.script_id == route.script_id).order_by(Route.created_at)
            all_routes_result = await db.execute(all_routes_stmt)
            all_routes = all_routes_result.scalars().all()
            
            current_route_index = next((i for i, r in enumerate(all_routes) if r.id == route.id), None)
            if current_route_index is not None and current_route_index < len(all_routes) - 1:
                next_route = all_routes[current_route_index + 1]
                result["has_next_chapter"] = True
                result["next_chapter"] = str(next_route.id)
                result["next_chapter_title"] = next_route.title
            else:
                result["has_next_chapter"] = False
    
    # 添加进度信息
    session = state.get("session")
    if session:
        # BUG-029-005: 获取当前 route 中有选项的节点数（= 对话轮数/决策点数）
        from sqlalchemy import func
        from app.models.script import NodeChoice
        total_stmt = (
            select(func.count(func.distinct(Node.id)))
            .join(NodeChoice, NodeChoice.node_id == Node.id)
            .where(Node.route_id == session.route_id)
        )
        total_result = await db.execute(total_stmt)
        total_turns = total_result.scalar() or 0
        
        # 获取已探索节点数 = 已做选择数 = 当前对话轮数
        explored_nodes = len(session.choice_history) if session.choice_history else 0
        
        # 计算进度百分比
        progress_percentage = (explored_nodes / total_turns * 100) if total_turns > 0 else 0
        result["progress"] = round(progress_percentage, 2)
        result["total_nodes"] = total_turns  # backward compat
        result["total_turns"] = total_turns  # BUG-029-005: explicit field
        result["current_turn"] = explored_nodes  # BUG-029-005: explicit field
        result["explored_nodes"] = explored_nodes
    
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
    """Submit a player's choice and advance the game.
    
    CR-037 DEV-007: Engine Dispatcher — Corvus sessions stream via SSE
    (choice_text as user input). Legacy sessions use NarrativeEngine.
    """
    # CR-037: Check if this is a Corvus engine session
    from app.models.corvus import CorvusGameSession
    try:
        session_uuid = UUID(session_id)
        corvus_stmt = select(CorvusGameSession).where(
            CorvusGameSession.id == session_uuid
        )
        corvus_result = await db.execute(corvus_stmt)
        corvus_session = corvus_result.scalar_one_or_none()
        
        if corvus_session and corvus_session.engine_type == "corvus":
            # AC-020: Corvus engine — choice_text as user input, SSE streaming
            # Verify ownership
            if corvus_session.user_id != UUID(user_id):
                raise AppException("SESSION_FORBIDDEN", 403, "Access denied: you do not own this session")
            if corvus_session.status != "playing":
                raise AppException("SESSION_INVALID_STATUS", 400, f"Session status is '{corvus_session.status}', expected 'playing'")
            if not corvus_session.corvus_internal_game_id:
                raise AppException("CORVUS_GAME_ID_MISSING", 500, "Session has no corvus_internal_game_id")
            
            # Get choice text from NodeChoice (may not exist for Corvus)
            from app.models.script import NodeChoice
            choice_text = request.choice_id  # Fallback to raw ID
            try:
                choice_stmt = select(NodeChoice).where(NodeChoice.id == UUID(request.choice_id))
                choice_result = await db.execute(choice_stmt)
                choice = choice_result.scalar_one_or_none()
                if choice:
                    choice_text = choice.text
            except (ValueError, AttributeError):
                pass  # Not a valid UUID, use raw choice_id as text
            
            # Stream via SSE (same as custom-input but with choice text)
            return _stream_corvus_turn(
                session_uuid, UUID(user_id), choice_text, db
            )
    except (ValueError, AttributeError):
        pass  # Not a UUID, fallback to legacy
    
    # AC-019: Legacy engine path (unchanged)
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
    
    # CR-021: 获取当前节点和选择信息（用于存储对话历史）
    from app.models.game import GameSession, DialogueHistory
    from app.models.script import Node, NodeChoice, Character
    
    _choice_text = ""
    _char_id = None
    _char_name = None
    
    _sess_stmt = select(GameSession).where(GameSession.id == UUID(session_id))
    _sess_res = await db.execute(_sess_stmt)
    _sess = _sess_res.scalar_one_or_none()
    
    if _sess and _sess.current_node_id:
        # 获取选择文本
        _choice_stmt = select(NodeChoice).where(NodeChoice.id == UUID(request.choice_id))
        _choice_res = await db.execute(_choice_stmt)
        _choice = _choice_res.scalar_one_or_none()
        if _choice:
            _choice_text = _choice.text
        
        # 获取角色信息（优先从 session metadata，fallback 到剧本主角色）
        if _sess.metadata_json and _sess.metadata_json.get("character_id"):
            try:
                _char_id = UUID(_sess.metadata_json["character_id"])
            except (ValueError, AttributeError):
                pass
        
        if not _char_id:
            _char_stmt = select(Character).where(
                Character.script_id == _sess.script_id,
                Character.is_main == True
            ).limit(1)
            _char_res = await db.execute(_char_stmt)
            _char = _char_res.scalar_one_or_none()
            if _char:
                _char_id = _char.id
                _char_name = _char.name
        elif _char_id:
            _char_name_stmt = select(Character.name).where(Character.id == _char_id)
            _char_name_res = await db.execute(_char_name_stmt)
            _char_name = _char_name_res.scalar_one_or_none()
    
    engine = NarrativeEngine(db)
    result = await engine.process_choice(
        session_id=UUID(session_id),
        user_id=UUID(user_id),
        choice_id=UUID(request.choice_id),
    )
    
    # CR-042 AC-001: Check next node type — transition/ai_dialog → SSE, preset/choice → JSON
    if result.get("next_node_id"):
        _next_node_stmt = select(Node).where(Node.id == UUID(result["next_node_id"]))
        _next_node_res = await db.execute(_next_node_stmt)
        _next_node = _next_node_res.scalar_one_or_none()
        if _next_node and _next_node.node_type in ("transition", "ai_dialog"):
            # AC-001: Return SSE streaming response for transition/ai_dialog nodes
            return _stream_legacy_turn(
                session_uuid=UUID(session_id),
                user_uuid=UUID(user_id),
                choice_result={
                    **result,
                    "choice_text": _choice_text,
                },
                next_node=_next_node,
                db=db,
            )
    
    # AC-002: preset/choice node — keep JSON response (fall through)
    
    try:
        _next_text = ""
        if result.get("next_node_id"):
            _next_stmt = select(Node).where(Node.id == UUID(result["next_node_id"]))
            _next_res = await db.execute(_next_stmt)
            _next_node = _next_res.scalar_one_or_none()
            if _next_node and _next_node.content:
                _next_text = _next_node.content.get("text", "")
        
        if _choice_text:
            db.add(DialogueHistory(
                session_id=UUID(session_id),
                user_id=UUID(user_id),
                role="user",
                content=_choice_text,
                character_id=_char_id,
                character_name=_char_name,
            ))
        
        if _next_text:
            db.add(DialogueHistory(
                session_id=UUID(session_id),
                user_id=UUID(user_id),
                role="assistant",
                content=_next_text,
                character_id=_char_id,
                character_name=_char_name,
            ))
        
        await db.flush()
    except Exception as e:
        import logging
        logging.warning(f"Failed to store choice dialogue: {e}")
    
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
    
    # Get session to find character_id (GameSession and select already imported at module level)
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
    
    # Achievement trigger logic
    new_achievements = []
    try:
        from app.models.gallery import Achievement
        from app.api.v1.achievements import ACHIEVEMENT_CATALOG
        
        # ACH-001: First dialogue completion
        # Check if this is the first dialogue for this user
        dialogue_count_result = await db.execute(
            select(func.count()).select_from(GameSession).where(
                GameSession.user_id == UUID(user_id)
            )
        )
        dialogue_count = dialogue_count_result.scalar() or 0
        
        if dialogue_count == 1:  # First dialogue
            ach_001_check = await db.execute(
                select(Achievement).where(
                    Achievement.user_id == UUID(user_id),
                    Achievement.achievement_id == "ACH-001"
                )
            )
            if not ach_001_check.scalar_one_or_none():
                # Unlock ACH-001
                new_ach = Achievement(
                    user_id=UUID(user_id),
                    achievement_id="ACH-001",
                    title=ACHIEVEMENT_CATALOG["ACH-001"]["name"],
                    description=ACHIEVEMENT_CATALOG["ACH-001"]["description"],
                    icon_url=ACHIEVEMENT_CATALOG["ACH-001"]["icon"],
                    unlocked_at=datetime.utcnow()
                )
                db.add(new_ach)
                await db.flush()
                new_achievements.append({
                    "id": "ACH-001",
                    "name": ACHIEVEMENT_CATALOG["ACH-001"]["name"],
                    "description": ACHIEVEMENT_CATALOG["ACH-001"]["description"]
                })
        
        # ACH-002: Affection reaches 60
        if game_session and character_id:
            from app.services.narrative.affection_service import AffectionService
            affection_service = AffectionService(db)
            affection = await affection_service.get_affection(
                UUID(user_id),
                UUID(character_id)
            )
            if affection and affection.value >= 60:
                ach_002_check = await db.execute(
                    select(Achievement).where(
                        Achievement.user_id == UUID(user_id),
                        Achievement.achievement_id == "ACH-002"
                    )
                )
                if not ach_002_check.scalar_one_or_none():
                    # Unlock ACH-002
                    new_ach = Achievement(
                        user_id=UUID(user_id),
                        achievement_id="ACH-002",
                        title=ACHIEVEMENT_CATALOG["ACH-002"]["name"],
                        description=ACHIEVEMENT_CATALOG["ACH-002"]["description"],
                        icon_url=ACHIEVEMENT_CATALOG["ACH-002"]["icon"],
                        unlocked_at=datetime.utcnow()
                    )
                    db.add(new_ach)
                    await db.flush()
                    new_achievements.append({
                        "id": "ACH-002",
                        "name": ACHIEVEMENT_CATALOG["ACH-002"]["name"],
                        "description": ACHIEVEMENT_CATALOG["ACH-002"]["description"]
                    })
        
        # ACH-003: Complete 3 scripts
        # Count completed scripts (sessions with status='completed')
        completed_scripts_result = await db.execute(
            select(func.count(func.distinct(GameSession.script_id))).where(
                GameSession.user_id == UUID(user_id),
                GameSession.status == 'completed'
            )
        )
        completed_scripts = completed_scripts_result.scalar() or 0
        
        if completed_scripts >= 3:
            ach_003_check = await db.execute(
                select(Achievement).where(
                    Achievement.user_id == UUID(user_id),
                    Achievement.achievement_id == "ACH-003"
                )
            )
            if not ach_003_check.scalar_one_or_none():
                # Unlock ACH-003
                new_ach = Achievement(
                    user_id=UUID(user_id),
                    achievement_id="ACH-003",
                    title=ACHIEVEMENT_CATALOG["ACH-003"]["name"],
                    description=ACHIEVEMENT_CATALOG["ACH-003"]["description"],
                    icon_url=ACHIEVEMENT_CATALOG["ACH-003"]["icon"],
                    unlocked_at=datetime.utcnow()
                )
                db.add(new_ach)
                await db.flush()
                new_achievements.append({
                    "id": "ACH-003",
                    "name": ACHIEVEMENT_CATALOG["ACH-003"]["name"],
                    "description": ACHIEVEMENT_CATALOG["ACH-003"]["description"]
                })
        
        await db.commit()
    except Exception as e:
        # Achievement check failed, don't block the response
        import logging
        logging.error(f"Achievement check failed: {e}")
        await db.rollback()
    
    # Add new achievements to result
    if new_achievements:
        result["new_achievements"] = new_achievements
    
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
    
    CR-042 AC-015: This endpoint is deprecated. Use POST /game/{id}/free-chat/stream instead.
    Behavior is unchanged — still returns synchronous JSON. Deprecation header added.

    Accepts a user message and returns a contextual AI response with emotion tag.
    CR-039 D8: Support Corvus engine sessions (CorvusGameSession table).
    """
    from app.services.free_chat_service import get_free_chat_service
    from app.models.game import GameSession
    from app.models.corvus import CorvusGameSession

    # CR-039 D8: Check if this is a Corvus engine session first
    try:
        session_uuid = UUID(session_id)
        corvus_stmt = select(CorvusGameSession).where(
            CorvusGameSession.id == session_uuid
        )
        corvus_result = await db.execute(corvus_stmt)
        corvus_session = corvus_result.scalar_one_or_none()

        if corvus_session and corvus_session.engine_type == "corvus":
            # Verify ownership
            if str(corvus_session.user_id) != user_id:
                raise AppException("SESSION_FORBIDDEN", 403, "Access denied: you do not own this session")
            if corvus_session.status != "playing":
                raise AppException("SESSION_INVALID_STATUS", 400, f"Session status is '{corvus_session.status}', expected 'playing'")

            # Get character_id from CorvusGameSession (D6 field)
            character_id = str(corvus_session.character_id) if corvus_session.character_id else None

            if not character_id:
                # Fallback: get first playable character
                from app.models.script import Character
                char_stmt = select(Character).where(Character.playable == True).limit(1)
                char_result = await db.execute(char_stmt)
                fallback_char = char_result.scalar_one_or_none()
                if fallback_char:
                    character_id = str(fallback_char.id)
                else:
                    character_id = "default"

            # For Corvus sessions, use the session's character as script context
            script_id = None
            if corvus_session.character_id:
                from app.models.script import Character
                char_obj = await db.execute(
                    select(Character).where(Character.id == corvus_session.character_id)
                )
                char_data = char_obj.scalar_one_or_none()
                if char_data and char_data.script_id:
                    script_id = str(char_data.script_id)

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

            # 更新每日任务进度（对话达人）
            try:
                from app.api.v1.daily_tasks import update_progress, ProgressUpdateRequest
                await update_progress(
                    request=ProgressUpdateRequest(task_type="task_dialogue", increment=1),
                    user_id=user_id,
                    db=db
                )
            except Exception as e:
                import logging
                logging.debug(f"Daily task progress update skipped: {e}")

            # Achievement trigger logic
            new_achievements = []
            try:
                from app.models.gallery import Achievement
                from app.api.v1.achievements import ACHIEVEMENT_CATALOG

                dialogue_count_result = await db.execute(
                    select(func.count()).select_from(GameSession).where(
                        GameSession.user_id == UUID(user_id)
                    )
                )
                dialogue_count = dialogue_count_result.scalar() or 0

                if dialogue_count >= 1:
                    ach_001_check = await db.execute(
                        select(Achievement).where(
                            Achievement.user_id == UUID(user_id),
                            Achievement.achievement_id == "ACH-001"
                        )
                    )
                    if not ach_001_check.scalar_one_or_none():
                        new_ach = Achievement(
                            user_id=UUID(user_id),
                            achievement_id="ACH-001",
                            title=ACHIEVEMENT_CATALOG["ACH-001"]["name"],
                            description=ACHIEVEMENT_CATALOG["ACH-001"]["description"],
                            icon_url=ACHIEVEMENT_CATALOG["ACH-001"]["icon"],
                            unlocked_at=datetime.utcnow()
                        )
                        db.add(new_ach)
                        await db.flush()
                        new_achievements.append({
                            "id": "ACH-001",
                            "name": ACHIEVEMENT_CATALOG["ACH-001"]["name"],
                            "description": ACHIEVEMENT_CATALOG["ACH-001"]["description"]
                        })

                await db.commit()
            except Exception as e:
                import logging
                logging.error(f"Achievement check failed in free-chat: {e}")
                await db.rollback()

            return {
                "session_id": session_id,
                "reply": response.get("reply", ""),
                "emotion": response.get("emotion", "neutral"),
                "character_id": response.get("character_id"),
                "new_achievements": new_achievements,
            }
    except (ValueError, AttributeError):
        pass  # Not a UUID, fallback to legacy

    # Legacy engine path
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

    # 更新每日任务进度（对话达人）
    try:
        from app.api.v1.daily_tasks import update_progress, ProgressUpdateRequest
        await update_progress(
            request=ProgressUpdateRequest(task_type="task_dialogue", increment=1),
            user_id=user_id,
            db=db
        )
    except Exception as e:
        import logging
        logging.debug(f"Daily task progress update skipped: {e}")

    # Achievement trigger logic (same as submit_choice and custom-input)
    new_achievements = []
    try:
        from app.models.gallery import Achievement
        from app.api.v1.achievements import ACHIEVEMENT_CATALOG
        
        # ACH-001: First dialogue completion
        dialogue_count_result = await db.execute(
            select(func.count()).select_from(GameSession).where(
                GameSession.user_id == UUID(user_id)
            )
        )
        dialogue_count = dialogue_count_result.scalar() or 0
        
        if dialogue_count >= 1:
            ach_001_check = await db.execute(
                select(Achievement).where(
                    Achievement.user_id == UUID(user_id),
                    Achievement.achievement_id == "ACH-001"
                )
            )
            if not ach_001_check.scalar_one_or_none():
                new_ach = Achievement(
                    user_id=UUID(user_id),
                    achievement_id="ACH-001",
                    title=ACHIEVEMENT_CATALOG["ACH-001"]["name"],
                    description=ACHIEVEMENT_CATALOG["ACH-001"]["description"],
                    icon_url=ACHIEVEMENT_CATALOG["ACH-001"]["icon"],
                    unlocked_at=datetime.utcnow()
                )
                db.add(new_ach)
                await db.flush()
                new_achievements.append({
                    "id": "ACH-001",
                    "name": ACHIEVEMENT_CATALOG["ACH-001"]["name"],
                    "description": ACHIEVEMENT_CATALOG["ACH-001"]["description"]
                })
        
        await db.commit()
    except Exception as e:
        import logging
        logging.error(f"Achievement check failed in free-chat: {e}")
        await db.rollback()

    from fastapi import Response as _FastResponse
    _resp_body = {
        "session_id": session_id,
        "reply": response.get("reply", ""),
        "emotion": response.get("emotion", "neutral"),
        "character_id": response.get("character_id"),
        "new_achievements": new_achievements,
    }
    # CR-042 AC-015: Add deprecation header to old free-chat endpoint
    _deprecated_resp = _FastResponse(
        content=json.dumps(_resp_body, default=str),
        media_type="application/json",
        headers={"Deprecation": "true"},
    )
    return _deprecated_resp


@router.post("/game/{session_id}/free-chat/stream")
async def free_chat_stream(
    session_id: str,
    request: FreeChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """CR-042 AC-011: Stream free chat response via SSE.

    New endpoint for CR-042 REQ-003.
    Old POST /game/{session_id}/free-chat remains for backward compatibility (deprecated).
    """
    from app.services.free_chat_service import get_free_chat_service
    from app.models.game import GameSession
    from app.models.corvus import CorvusGameSession
    from app.services.llm.gateway import LLMMessage
    import asyncio
    import logging as _fc_log
    _fc_logger = _fc_log.getLogger(__name__)

    # Verify session ownership
    await _verify_session_ownership(UUID(session_id), user_id, db)

    # Get game session for character/script info
    session_result = await db.execute(
        select(GameSession).where(GameSession.id == UUID(session_id))
    )
    game_session = session_result.scalar_one_or_none()

    character_id = None
    script_id = None
    if game_session:
        # Get character
        if game_session.character_id:
            character_id = str(game_session.character_id)
        else:
            from app.models.script import Character
            char_stmt = select(Character).where(
                Character.script_id == game_session.script_id,
                Character.is_main == True,
            ).limit(1)
            char_result = await db.execute(char_stmt)
            main_char = char_result.scalar_one_or_none()
            if main_char:
                character_id = str(main_char.id)
        script_id = str(game_session.script_id) if game_session.script_id else None

    if not character_id:
        character_id = "default"

    deferred_data = {
        "session_id": session_id,
        "user_id": user_id,
        "character_id": character_id,
        "message": request.message,
        "script_id": script_id,
        "text_chunks": [],
    }

    async def event_generator():
        try:
            svc = get_free_chat_service()
            # AC-013: Stream using send_message_stream()
            async for chunk in svc.send_message_stream(
                db=db,
                user_id=user_id,
                character_id=character_id,
                message=request.message,
                script_id=script_id,
                session_id=session_id,
            ):
                deferred_data["text_chunks"].append(chunk)
                yield f'data: {json.dumps({"type":"text","content":chunk})}\n\n'

            # Done event
            done_payload = {
                "type": "done",
                "session_id": str(session_id),
            }
            yield f'data: {json.dumps(done_payload, default=str)}\n\n'

        except Exception as e:
            _fc_logger.error(f"[Free chat SSE] Error: {e}", exc_info=True)
            yield f'data: {json.dumps({"type":"error","message":str(e)})}\n\n'
        finally:
            # AC-014: Deferred DB write for free-chat stream
            try:
                from app.core.database import async_session_factory
                from app.models.free_chat import FreeChatSession
                loop = asyncio.get_event_loop()

                async def _deferred_free_chat():
                    try:
                        async with async_session_factory() as deferred_db:
                            svc = get_free_chat_service()
                            # Save messages using the service
                            full_text = "".join(deferred_data["text_chunks"])
                            await svc._save_message(deferred_db, session_id, user_id, "user", request.message)
                            await svc._save_message(deferred_db, session_id, user_id, "assistant", full_text)
                            await deferred_db.commit()
                            _fc_logger.info(f"[Deferred] Free chat DB write done for session {session_id}")
                    except Exception as de:
                        _fc_logger.error(f"[Deferred] Free chat failed: {de}", exc_info=True)

                loop.create_task(_deferred_free_chat())
            except Exception as fe:
                _fc_logger.error(f"[Free chat SSE] Failed to schedule deferred: {fe}", exc_info=True)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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
    """Get free chat message history.
    
    CR-039 D8: Support Corvus engine sessions.
    """
    await _verify_session_ownership(UUID(session_id), user_id, db)
    
    # CR-039 D8: Check if this is a Corvus engine session
    from app.models.corvus import CorvusGameSession
    try:
        session_uuid = UUID(session_id)
        corvus_stmt = select(CorvusGameSession).where(
            CorvusGameSession.id == session_uuid
        )
        corvus_result = await db.execute(corvus_stmt)
        corvus_session = corvus_result.scalar_one_or_none()

        if corvus_session and corvus_session.engine_type == "corvus":
            # Get character_id from CorvusGameSession (D6 field)
            character_id = str(corvus_session.character_id) if corvus_session.character_id else None

            if not character_id:
                # Fallback: get first playable character
                from app.models.script import Character
                char_stmt = select(Character).where(Character.playable == True).limit(1)
                char_result = await db.execute(char_stmt)
                fallback_char = char_result.scalar_one_or_none()
                if fallback_char:
                    character_id = str(fallback_char.id)
        else:
            corvus_session = None
    except (ValueError, AttributeError):
        corvus_session = None
        character_id = None

    # Legacy GameSession path (if not a Corvus session)
    if not corvus_session:
        from app.models.game import GameSession
        session_result = await db.execute(
            select(GameSession).where(GameSession.id == UUID(session_id))
        )
        game_session = session_result.scalar_one_or_none()
        
        if not game_session:
            return {"messages": []}
        
        # CR-036 FIX: 使用 session 中的角色（玩家选择的角色），而非固定查 is_main
        character_id = str(game_session.character_id) if game_session.character_id else None
        
        if not character_id:
            # fallback: 获取该剧本的主角色
            from app.models.script import Character
            char_stmt = select(Character).where(
                Character.script_id == game_session.script_id,
                Character.is_main == True
            ).limit(1)
            char_result = await db.execute(char_stmt)
            main_char = char_result.scalar_one_or_none()
            if main_char:
                character_id = str(main_char.id)
    
    # 查找该用户与该角色的最近 FreeChatSession
    from app.models.free_chat import FreeChatSession
    stmt = select(FreeChatSession).where(
        FreeChatSession.user_id == UUID(user_id),
        FreeChatSession.character_id == UUID(character_id) if character_id else True
    ).order_by(FreeChatSession.created_at.desc()).limit(1)
    
    result = await db.execute(stmt)
    free_chat_session = result.scalar_one_or_none()
    
    if not free_chat_session or not free_chat_session.messages:
        return {"messages": []}
    
    # 返回最近 50 条消息
    messages = free_chat_session.messages[-50:] if len(free_chat_session.messages) > 50 else free_chat_session.messages
    
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
    DEV-BE-002: 玩家自由输入推进剧情。
    
    CR-037: For Corvus engine sessions, returns SSE streaming response.
    For legacy engine sessions, uses narrative_engine (synchronous JSON).
    """
    if not request.text.strip():
        raise AppException("EMPTY_INPUT", 400, "输入不能为空")

    # Check if this is a Corvus engine session
    from app.models.corvus import CorvusGameSession
    from sqlalchemy import select as sa_select

    try:
        session_uuid = UUID(session_id)
    except (ValueError, AttributeError):
        # Not a UUID — fallback to legacy behavior
        session_uuid = None

    if session_uuid:
        corvus_stmt = sa_select(CorvusGameSession).where(
            CorvusGameSession.id == session_uuid
        )
        corvus_result = await db.execute(corvus_stmt)
        corvus_session = corvus_result.scalar_one_or_none()

        if corvus_session and corvus_session.engine_type == "corvus":
            # CR-037: Corvus engine — validate before SSE streaming
            # Verify ownership
            if corvus_session.user_id != UUID(user_id):
                raise AppException("SESSION_FORBIDDEN", 403, "Access denied: you do not own this session")
            # Verify status
            if corvus_session.status != "playing":
                raise AppException("SESSION_INVALID_STATUS", 400, f"Session status is '{corvus_session.status}', expected 'playing'")
            # Verify corvus_internal_game_id exists
            if not corvus_session.corvus_internal_game_id:
                raise AppException("CORVUS_GAME_ID_MISSING", 500, "Session has no corvus_internal_game_id")
            # CR-037: Corvus engine — return SSE streaming response
            return _stream_corvus_turn(
                session_uuid, UUID(user_id), request.text.strip(), db
            )

    # Legacy engine path (original behavior)
    await _verify_session_ownership(UUID(session_id), user_id, db)

    # CR-016: Check quota before processing (user action = deduct quota)
    from app.services.quota_service import QuotaService
    from app.services.paywall_service import PaywallService
    quota_service = QuotaService(db)
    
    quota_status = await quota_service.get_user_quota_status(UUID(user_id))
    quota_exhausted = quota_status["remaining"] == 0 and not quota_status["is_exempt"]
    
    if quota_exhausted:
        trigger_result = await paywall_service.check_trigger(UUID(user_id), "T1_quota")
        return {
            "error": "quota_exhausted",
            "message": "对话额度已用完",
            "remaining_quota": 0,
            "paywall_trigger": trigger_result,
        }

    # CR-042 AC-006: Legacy custom-input → SSE streaming
    # Get current node and character for streaming
    from app.models.game import GameSession as _GS
    _gs_stmt = select(_GS).where(_GS.id == UUID(session_id))
    _gs_res = await db.execute(_gs_stmt)
    _gs = _gs_res.scalar_one_or_none()

    _current_node = None
    _character = None
    if _gs and _gs.current_node_id:
        _node_stmt = select(Node).where(Node.id == _gs.current_node_id)
        _node_res = await db.execute(_node_stmt)
        _current_node = _node_res.scalar_one_or_none()

    if _gs:
        # Get character for this session
        if _gs.character_id:
            _char_stmt = select(Character).where(Character.id == _gs.character_id)
            _char_res = await db.execute(_char_stmt)
            _character = _char_res.scalar_one_or_none()
        if not _character:
            # Fallback: main character of the script
            _mc_stmt = select(Character).where(
                Character.script_id == _gs.script_id,
                Character.is_main == True,
            ).limit(1)
            _mc_res = await db.execute(_mc_stmt)
            _character = _mc_res.scalar_one_or_none()

    # AC-006: Return SSE streaming response
    return _stream_legacy_custom_input(
        session_uuid=UUID(session_id),
        user_uuid=UUID(user_id),
        user_text=request.text.strip(),
        node=_current_node,
        character=_character,
        db=db,
    )

    # --- Legacy JSON path below is kept but unreachable after SSE return ---
    # (preserved for rollback safety — git revert restores JSON path)

    # Use narrative_engine to process custom input and get response with choices
    engine = NarrativeEngine(db)
    result = await engine.process_custom_input(
        session_id=UUID(session_id),
        user_id=UUID(user_id),
        user_text=request.text.strip(),
    )
    
    # CR-020 T-001: Auto-store dialogue for custom input
    # Store user input
    try:
        from app.models.game import DialogueHistory
        # Determine character_id for this session
        _char_id = None
        _char_name = None
        if result.get("character_id"):
            try:
                _char_uuid = UUID(result["character_id"])
                from app.models.script import Character as _CharModel
                _char_check = await db.execute(
                    select(_CharModel).where(_CharModel.id == _char_uuid)
                )
                if _char_check.scalar_one_or_none():
                    _char_id = _char_uuid
                    _char_name = result.get("character_name")
                    if not _char_name:
                        _char_obj_result = await db.execute(
                            select(_CharModel.name).where(_CharModel.id == _char_uuid)
                        )
                        _char_name = _char_obj_result.scalar_one_or_none()
            except (ValueError, AttributeError):
                pass
        
        # Store user message
        user_dialogue = DialogueHistory(
            session_id=UUID(session_id),
            user_id=UUID(user_id),
            role="user",
            content=request.text.strip(),
            character_id=_char_id,
            character_name=_char_name,
            emotion=None,
        )
        db.add(user_dialogue)
        
        # Store assistant/character response
        response_text = result.get("text", "")
        if response_text:
            assistant_dialogue = DialogueHistory(
                session_id=UUID(session_id),
                user_id=UUID(user_id),
                role="assistant",
                content=response_text,
                character_id=_char_id,
                character_name=_char_name,
                emotion=result.get("emotion"),
            )
            db.add(assistant_dialogue)
        
        await db.flush()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Failed to store custom-input dialogue: {e}")
    
    # CR-016: Consume quota after successful custom input
    if not quota_status["is_exempt"]:
        await quota_service.consume_quota(UUID(user_id))
    
    # Get updated quota status
    updated_quota_status = await quota_service.get_user_quota_status(UUID(user_id))
    result["remaining_quota"] = updated_quota_status["remaining"]
    
    # Achievement trigger logic (same as submit_choice)
    new_achievements = []
    try:
        from app.models.gallery import Achievement
        from app.api.v1.achievements import ACHIEVEMENT_CATALOG
        from app.models.game import GameSession
        
        # ACH-001: First dialogue completion
        dialogue_count_result = await db.execute(
            select(func.count()).select_from(GameSession).where(
                GameSession.user_id == UUID(user_id)
            )
        )
        dialogue_count = dialogue_count_result.scalar() or 0
        
        if dialogue_count >= 1:
            ach_001_check = await db.execute(
                select(Achievement).where(
                    Achievement.user_id == UUID(user_id),
                    Achievement.achievement_id == "ACH-001"
                )
            )
            if not ach_001_check.scalar_one_or_none():
                new_ach = Achievement(
                    user_id=UUID(user_id),
                    achievement_id="ACH-001",
                    title=ACHIEVEMENT_CATALOG["ACH-001"]["name"],
                    description=ACHIEVEMENT_CATALOG["ACH-001"]["description"],
                    icon_url=ACHIEVEMENT_CATALOG["ACH-001"]["icon"],
                    unlocked_at=datetime.utcnow()
                )
                db.add(new_ach)
                await db.flush()
                new_achievements.append({
                    "id": "ACH-001",
                    "name": ACHIEVEMENT_CATALOG["ACH-001"]["name"],
                    "description": ACHIEVEMENT_CATALOG["ACH-001"]["description"]
                })
        
        await db.commit()
    except Exception as e:
        import logging
        logging.error(f"Achievement check failed in custom-input: {e}")
        await db.rollback()
    
    # Add new_achievements to result
    result["new_achievements"] = new_achievements
    
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


@router.get("/game/scripts/{script_id}/characters")
async def get_script_characters(
    script_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR-038 AC-038-026: Get playable characters for a script.

    Returns characters from the Character table where playable=True.
    Each character returns: id / name / description / avatar_url / play_description.
    Response format: {"code": 0, "data": [...]}
    Empty array if script has no playable characters.
    """
    from app.models.script import Character as CharModel

    # Validate script_id is a UUID
    try:
        script_uuid = UUID(script_id)
    except (ValueError, AttributeError):
        raise AppException("INVALID_SCRIPT_ID", 400, f"Invalid script_id: {script_id}")

    # Verify script exists
    script_stmt = select(Script).where(Script.id == script_uuid)
    script_result = await db.execute(script_stmt)
    script = script_result.scalar_one_or_none()
    if not script:
        raise AppException("SCRIPT_NOT_FOUND", 404, f"Script {script_id} not found")

    # Query playable characters
    char_stmt = (
        select(CharModel)
        .where(
            CharModel.script_id == script_uuid,
            CharModel.playable == True,
        )
        .order_by(CharModel.created_at)
    )
    char_result = await db.execute(char_stmt)
    characters = char_result.scalars().all()

    data = [
        {
            "id": str(c.id),
            "name": c.name,
            "description": c.description,
            "avatar_url": c.avatar_url,
            "play_description": c.play_description,
        }
        for c in characters
    ]

    return {
        "code": 0,
        "data": data,
    }


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


@router.get("/game/{session_id}/ai-dialogue")
async def generate_ai_dialogue(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """CR-036: Async AI dialogue generation for preset nodes.
    
    Frontend calls this after receiving preset text to get AI-enhanced content.
    Uses _generate_validated_dialogue (PromptBuilder 6-layer prompt).
    Timeout: 15 seconds.
    """
    import asyncio
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Verify session ownership
    await _verify_session_ownership(UUID(session_id), user_id, db)
    
    # Get session state
    engine = NarrativeEngine(db)
    state = await engine.script_service.get_game_session_state(UUID(session_id))
    
    session = state.get("session")
    current_node = state.get("current_node")
    
    if not session or not current_node:
        return {"text": "", "emotion": "neutral"}
    
    # Only generate AI dialogue for preset nodes
    if current_node.node_type not in ("preset", "fixed_scene"):
        return {"text": "", "emotion": "neutral"}
    
    # Get character info
    character_id = engine.script_service.get_node_character_id(current_node)
    if not character_id:
        return {"text": "", "emotion": "neutral"}
    
    character = await engine.script_service.get_character(character_id)
    if not character:
        return {"text": "", "emotion": "neutral"}
    
    # Generate AI dialogue with 30s timeout
    try:
        result = await asyncio.wait_for(
            engine._generate_validated_dialogue(
                node=current_node,
                character=character,
                session=session,
                user_id=UUID(user_id),
            ),
            timeout=15.0,
        )
        return {
            "text": result.get("text", ""),
            "emotion": result.get("emotion", "neutral"),
            "node_id": str(current_node.id),
            "character_id": str(character.id),
        }
    except asyncio.TimeoutError:
        logger.warning(f"AI dialogue timeout for session {session_id}, node {current_node.id}")
        return {"text": "", "emotion": "neutral", "timeout": True}
    except Exception as e:
        logger.warning(f"AI dialogue failed for session {session_id}: {e}")
        return {"text": "", "emotion": "neutral", "error": str(e)}


@router.post("/game/auto-save")
async def auto_save(
    request: AutoSaveRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """W06: Auto-save game state after choice."""
    from app.models.save import SaveSnapshot
    from app.models.game import GameSession
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
    CR-038: 支持 Corvus engine 会话
    """
    from sqlalchemy import select, func
    from app.models.game import GameSession, GameProgress
    from app.models.script import Script, Route, Node
    from app.models.corvus import CorvusGameSession
    
    # CR-038: 先检查是否为 Corvus 会话
    try:
        session_uuid = UUID(session_id)
        corvus_stmt = select(CorvusGameSession).where(
            CorvusGameSession.id == session_uuid,
            CorvusGameSession.user_id == UUID(user_id)
        )
        corvus_result = await db.execute(corvus_stmt)
        corvus_session = corvus_result.scalar_one_or_none()
        
        if corvus_session:
            # Corvus 会话：返回简化进度信息
            return {
                "session_id": str(corvus_session.id),
                "script_id": None,
                "current_node_id": None,
                "current_chapter": None,
                "total_nodes": 0,
                "total_turns": 0,
                "explored_nodes": 0,
                "current_turn": 0,
                "completion_rate": 0.0,
                "progress_percentage": 0.0,
                "choice_count": 0,
                "dialogue_count": 0,
                "status": corvus_session.status,
            }
    except (ValueError, AttributeError):
        pass  # Not a UUID, fallback to legacy
    
    # 验证会话所有权
    stmt = select(GameSession).where(
        GameSession.id == session_id,
        GameSession.user_id == user_id
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise AppException("SESSION_NOT_FOUND", 404, "Game session not found")
    
    # BUG-029-005: 获取当前 route 中有选项的节点数（= 对话轮数/决策点数）
    # 进度 = 已做选择数 / 总决策点数
    from app.models.script import NodeChoice
    stmt = (
        select(func.count(func.distinct(Node.id)))
        .join(NodeChoice, NodeChoice.node_id == Node.id)
        .where(Node.route_id == session.route_id)
    )
    result = await db.execute(stmt)
    total_turns = result.scalar() or 0
    
    # 获取已探索节点数（从 choice_history 中提取）= 已做选择数 = 当前对话轮数
    explored_nodes = len(session.choice_history) if session.choice_history else 0
    
    # 计算进度百分比
    # CR-020: 如果游戏已完成，进度为 100%
    if session.status == "completed":
        progress_percentage = 100.0
    else:
        progress_percentage = (explored_nodes / total_turns * 100) if total_turns > 0 else 0
    
    # CR-020: 获取当前章节信息
    current_chapter = None
    if session.current_node_id:
        from app.models.script import Node
        node_stmt = select(Node).where(Node.id == session.current_node_id)
        node_result = await db.execute(node_stmt)
        current_node = node_result.scalar_one_or_none()
        if current_node:
            route_stmt = select(Route).where(Route.id == current_node.route_id)
            route_result = await db.execute(route_stmt)
            current_route = route_result.scalar_one_or_none()
            if current_route:
                current_chapter = current_route.title
    
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
        "current_chapter": current_chapter,  # CR-020: 添加章节信息
        "total_nodes": total_turns,  # BUG-029-005: now represents decision points (dialogue turns)
        "total_turns": total_turns,  # BUG-029-005: explicit field for FE
        "explored_nodes": explored_nodes,
        "current_turn": explored_nodes,  # BUG-029-005: explicit field for FE
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
    CR-038: 支持 Corvus engine 会话
    """
    from app.models.game import GameSession
    from app.models.script import Script, Character
    from app.models.affection import Affection
    from app.models.corvus import CorvusGameSession
    
    # CR-038: 先检查是否为 Corvus 会话
    try:
        session_uuid = UUID(session_id)
        corvus_stmt = select(CorvusGameSession).where(
            CorvusGameSession.id == session_uuid,
            CorvusGameSession.user_id == UUID(user_id)
        )
        corvus_result = await db.execute(corvus_stmt)
        corvus_session = corvus_result.scalar_one_or_none()
        
        if corvus_session:
            # CR-039 D6: Read character_id from session, query Character table for name
            character_name = ""
            character_id_str = None
            if corvus_session.character_id:
                char_stmt = select(Character).where(Character.id == corvus_session.character_id)
                char_result = await db.execute(char_stmt)
                char = char_result.scalar_one_or_none()
                if char:
                    character_name = char.name
                    character_id_str = str(char.id)
            
            # AC-014: Read affinity from SessionNpc table
            from app.models.corvus import SessionNpc
            npc_stmt = select(SessionNpc).where(
                SessionNpc.game_session_id == corvus_session.id
            ).order_by(SessionNpc.affinity.desc()).limit(1)
            npc_result = await db.execute(npc_stmt)
            npc = npc_result.scalar_one_or_none()
            
            affection_value = 0
            affinity_level = "neutral"
            if npc and npc.affinity is not None:
                affection_value = npc.affinity
                if affection_value >= 50:
                    affinity_level = "close"
                elif affection_value >= 20:
                    affinity_level = "friendly"
                elif affection_value >= -10:
                    affinity_level = "neutral"
                elif affection_value >= -30:
                    affinity_level = "distant"
                else:
                    affinity_level = "hostile"
            
            return {
                "session_id": str(corvus_session.id),
                "script_id": None,
                "script_name": "",
                "character_id": character_id_str,
                "character_name": character_name,
                "affection_value": affection_value,
                "affinity_level": affinity_level,
                "status": corvus_session.status,
                "current_node_id": None,
                "chapter_number": None,
                "chapter_type": None,
                "chapter_title": None,
            }
    except (ValueError, AttributeError):
        pass  # Not a UUID, fallback to legacy
    
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
    
    # CR-028: Get character - prefer session's character_id, fallback to is_main
    character = None
    if session.character_id:
        # Use the character stored in session (player's choice)
        stmt = select(Character).where(Character.id == session.character_id)
        result = await db.execute(stmt)
        character = result.scalar_one_or_none()
    
    if not character:
        # Fallback to is_main character for this script
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
    
    # CR-030: Get chapter info from route
    chapter_number = None
    chapter_type = None
    chapter_title = None
    if session.route_id:
        route_stmt = select(Route).where(Route.id == session.route_id)
        route_result = await db.execute(route_stmt)
        route = route_result.scalar_one_or_none()
        if route:
            chapter_number = route.chapter_number
            chapter_type = route.chapter_type
            # 优先使用路线的真实标题，fallback 到 chapter_type 映射
            if route.title:
                chapter_title = route.title
            elif chapter_type:
                chapter_type_title_map = {
                    'encounter': '相遇',
                    'daily': '日常',
                    'conflict': '冲突',
                    'convergence': '收束',
                }
                chapter_title = chapter_type_title_map.get(chapter_type, chapter_type)

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
        # CR-030: Chapter information
        "chapter_number": chapter_number,
        "chapter_type": chapter_type,
        "chapter_title": chapter_title,
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
    CR-038: 支持 Corvus engine 会话
    """
    from app.models.game import GameSession
    from app.models.corvus import CorvusGameSession
    
    # CR-038: 先检查是否为 Corvus 会话
    try:
        session_uuid = UUID(session_id)
        corvus_stmt = select(CorvusGameSession).where(
            CorvusGameSession.id == session_uuid,
            CorvusGameSession.user_id == UUID(user_id)
        )
        corvus_result = await db.execute(corvus_stmt)
        corvus_session = corvus_result.scalar_one_or_none()
        
        if corvus_session:
            # Corvus 会话：返回空历史（Corvus 对话历史由 SSE 流式处理）
            return {
                "session_id": str(corvus_session.id),
                "history": [],
                "total_entries": 0,
                "total": 0,
                "page": 1,
                "page_size": 50,
            }
    except (ValueError, AttributeError):
        pass  # Not a UUID, fallback to legacy
    
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
    CR-039 D8: Support Corvus sessions (no GameSession record, skip DB insert).
    """
    from app.models.game import GameSession, DialogueHistory
    from app.models.corvus import CorvusGameSession
    
    # CR-039 D8: Check if this is a Corvus session first
    try:
        session_uuid = UUID(session_id)
        corvus_stmt = select(CorvusGameSession).where(
            CorvusGameSession.id == session_uuid,
            CorvusGameSession.user_id == UUID(user_id)
        )
        corvus_result = await db.execute(corvus_stmt)
        corvus_session = corvus_result.scalar_one_or_none()
        
        if corvus_session:
            # Corvus session: dialogue is already stored via write_memory in SSE stream.
            # Return a mock success response — no GameSession FK needed.
            import uuid as _uuid
            from datetime import datetime as _dt
            mock_id = _uuid.uuid4()
            return {
                "id": str(mock_id),
                "session_id": session_id,
                "role": request.role,
                "content": request.content,
                "character_id": request.character_id,
                "character_name": request.character_name,
                "emotion": request.emotion,
                "created_at": _dt.utcnow().isoformat(),
            }
    except (ValueError, AttributeError):
        pass  # Not a UUID, fallback to legacy
    
    # Verify session ownership (Legacy)
    stmt = select(GameSession).where(
        GameSession.id == UUID(session_id),
        GameSession.user_id == UUID(user_id)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise AppException("SESSION_NOT_FOUND", 404, "Game session not found")
    
    # Validate character_id exists in characters table (foreign key constraint)
    valid_character_id = None
    if request.character_id:
        from app.models.script import Character
        char_result = await db.execute(
            select(Character).where(Character.id == UUID(request.character_id))
        )
        if char_result.scalar_one_or_none():
            valid_character_id = UUID(request.character_id)
    
    # Create dialogue record
    dialogue = DialogueHistory(
        session_id=UUID(session_id),
        user_id=UUID(user_id),
        role=request.role,
        content=request.content,
        character_id=valid_character_id,
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
    from app.models.corvus import CorvusGameSession
    
    # CR-039 D8: Check if this is a Corvus session first
    try:
        session_uuid = UUID(session_id)
        corvus_stmt = select(CorvusGameSession).where(
            CorvusGameSession.id == session_uuid,
            CorvusGameSession.user_id == UUID(user_id)
        )
        corvus_result = await db.execute(corvus_stmt)
        corvus_session = corvus_result.scalar_one_or_none()
        
        if corvus_session:
            # Corvus session: no legacy dialogue_history records.
            # Dialogue is stored via write_memory in SSE stream.
            return {"dialogues": [], "total": 0, "limit": limit, "offset": offset}
    except (ValueError, AttributeError):
        pass  # Not a UUID, fallback to legacy
    
    # Verify session ownership (Legacy)
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


# ── CR-037 Corvus-Story-Core Endpoints (DEV-002) ─────────────────────────────

from app.models.corvus import PlayerCandidate, CorvusGameSession
from app.schemas.game import PlayerCandidateCreate


class CreateCorvusSessionRequest(BaseModel):
    """Request body for POST /game/session/create."""
    user_id: Optional[str] = None  # Optional: if not provided, use authenticated user


@router.get("/game/player/candidates")
async def get_player_candidates(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR-037 AC-005: Get player character candidates for the current user.

    Returns at most 3 candidate characters with name, personality, backstory,
    appearance, and initial_inventory.
    """
    user_uuid = UUID(user_id)

    stmt = (
        select(PlayerCandidate)
        .where(PlayerCandidate.user_id == user_uuid)
        .order_by(PlayerCandidate.created_at.asc())
        .limit(3)
    )
    result = await db.execute(stmt)
    candidates = result.scalars().all()

    data = [
        {
            "id": str(c.id),
            "name": c.name,
            "personality": c.personality,
            "backstory": c.backstory,
            "appearance": c.appearance,
            "initial_inventory": c.initial_inventory or [],
        }
        for c in candidates
    ]

    return {
        "code": 0,
        "data": data,
    }


@router.post("/game/player/candidates")
async def create_player_candidate(
    request: PlayerCandidateCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR-038 AC-038-003~006: Create a player character candidate.

    Creates a new player_candidates record for the authenticated user.
    - name is required (≤100 chars)
    - personality, backstory, appearance are optional
    - initial_inventory is managed by backend (not accepted from user)
    - Maximum 3 candidates per user; 4th returns 400
    """
    from sqlalchemy import func as sa_func

    user_uuid = UUID(user_id)

    # Check candidate count limit (max 3)
    count_stmt = (
        select(sa_func.count(PlayerCandidate.id))
        .where(PlayerCandidate.user_id == user_uuid)
    )
    count_result = await db.execute(count_stmt)
    current_count = count_result.scalar() or 0

    if current_count >= 3:
        raise AppException(
            ErrorCode.VALIDATION_ERROR,
            400,
            "CANDIDATE_LIMIT_EXCEEDED: 用户已有 3 个候选角色，最多 3 个",
        )

    # Create new candidate
    candidate = PlayerCandidate(
        user_id=user_uuid,
        name=request.name,
        personality=request.personality,
        backstory=request.backstory,
        appearance=request.appearance,
        initial_inventory=[],  # managed by backend, default empty
    )
    db.add(candidate)
    await db.commit()
    await db.refresh(candidate)

    return {
        "code": 0,
        "data": {
            "id": str(candidate.id),
            "name": candidate.name,
            "personality": candidate.personality,
            "backstory": candidate.backstory,
            "appearance": candidate.appearance,
            "initial_inventory": candidate.initial_inventory or [],
        },
    }


@router.post("/game/session/create")
async def create_corvus_session(
    request: CreateCorvusSessionRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR-037 AC-006: Create a new Corvus game session.

    Creates a corvus_game_sessions record with status='waiting_select_player'
    and returns the game_session_id (UUID v4).
    """
    # Use request.user_id if provided (for admin/testing), else use authenticated user
    session_user_id = request.user_id if request.user_id else user_id
    user_uuid = UUID(session_user_id)

    session = CorvusGameSession(
        user_id=user_uuid,
        status="waiting_select_player",
        engine_type="corvus",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "code": 0,
        "data": {
            "game_session_id": str(session.id),
            "status": session.status,
            "engine_type": session.engine_type,
        },
    }


class SelectPlayerRequest(BaseModel):
    """Request body for POST /game/session/select-player."""
    game_session_id: str
    character_id: str


@router.post("/game/session/select-player")
async def select_player(
    request: SelectPlayerRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    CR-037 AC-007: Select a player candidate and create a Corvus game.

    Calls CorvusClient.create_game with ONLY the selected candidate.
    Updates the CorvusGameSession: status=playing, corvus_internal_game_id.
    """
    from app.services.corvus_adapter import CorvusAdapter

    adapter = CorvusAdapter(db)
    result = await adapter.create_session(
        user_id=UUID(user_id),
        game_session_id=UUID(request.game_session_id),
        character_id=UUID(request.character_id),
    )

    return {
        "code": 0,
        "data": result,
    }
