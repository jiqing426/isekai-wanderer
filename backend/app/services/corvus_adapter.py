"""CorvusAdapter — bridges Isekai Wanderer backend and Corvus-Story-Core.

Responsibilities:
- create_session (DEV-003): select player candidate → call Corvus create_game → store game_id
- stream_turn (DEV-004): SSE streaming + event translation
- SSETranslator: translate Corvus SSE events to frontend format
- sync_world_state (DEV-005): async DB sync of affinity/items/flags from gm_update

Future scope (DEV-006):
- write_memory / recall_and_inject: vector memory with pgvector
- restore_npc_knowninfo: restore NPC knownInfo after recall
"""

import asyncio
import json
import logging
import re
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.corvus import PlayerCandidate, CorvusGameSession, SessionNpc, InventoryItem, StoryFlag
from app.models.memory import CharacterMemory
from app.services.corvus_client import get_corvus_client
from app.core.database import async_session_factory
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)


class CorvusAdapter:
    """Adapter between Isekai Wanderer and Corvus-Story-Core."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = get_corvus_client()

    async def create_session(
        self,
        user_id: uuid.UUID,
        game_session_id: uuid.UUID,
        character_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Select a character and create a Corvus game.

        CR-038 改造 (2026-09-07): 接受 character_id 而非 player_candidate_id。
        从 Character 表直接获取角色数据。

        Steps:
        1. Query the CorvusGameSession by id, verify ownership + status.
        2. Query the selected Character (from characters table, playable=True).
        3. Call CorvusClient.create_game with the character data.
        4. Update the GameSession: selected_character_id, status=playing,
           corvus_internal_game_id.
        5. Return initial session data for the frontend.

        Args:
            user_id: The authenticated user's UUID.
            game_session_id: The CorvusGameSession UUID (from POST /session/create).
            character_id: The selected Character UUID (from characters table).

        Returns:
            dict with game_session_id, status, corvus_game_id, player info.

        Raises:
            AppException on session not found, ownership mismatch, wrong status,
            character not found, or Corvus API failure.
        """
        from app.core.exceptions import AppException

        # 1. Query game session
        stmt = select(CorvusGameSession).where(
            CorvusGameSession.id == game_session_id,
        )
        result = await self.db.execute(stmt)
        session = result.scalar_one_or_none()

        if not session:
            raise AppException(
                "SESSION_NOT_FOUND",
                404,
                f"Corvus game session {game_session_id} not found",
            )

        # Verify ownership
        if session.user_id != user_id:
            raise AppException(
                "SESSION_FORBIDDEN",
                403,
                "Access denied: you do not own this session",
            )

        # Verify status
        if session.status != "waiting_select_player":
            raise AppException(
                "SESSION_INVALID_STATUS",
                400,
                f"Session status is '{session.status}', expected 'waiting_select_player'",
            )

        # 2. Query selected character (CR-038: from characters table, not player_candidates)
        from app.models.script import Character
        stmt = select(Character).where(
            Character.id == character_id,
            Character.playable == True,
        )
        result = await self.db.execute(stmt)
        character = result.scalar_one_or_none()

        if not character:
            raise AppException(
                "CHARACTER_NOT_FOUND",
                404,
                f"Character {character_id} not found or not playable",
            )

        # 3. Call Corvus create_game with character data
        try:
            # Convert personality dict to string if needed
            personality_str = ""
            if character.personality:
                if isinstance(character.personality, dict):
                    personality_str = ", ".join(f"{k}: {v}" for k, v in character.personality.items())
                else:
                    personality_str = str(character.personality)

            corvus_game_id = await self.client.create_game(
                player_name=character.name,
                backstory=personality_str or character.description or "",
                appearance=character.description or "",
                player_inventory=[],
            )
        except Exception as e:
            logger.error(f"[CorvusAdapter] create_game failed: {e}")
            raise AppException(
                "CORVUS_CREATE_FAILED",
                503,
                f"Failed to create Corvus game: {e}",
            )

        # 4. Update game session
        # CR-038: 不再写 selected_player_candidate_id（有FK约束到 player_candidates 表）
        # CR-039 D6: Store character_id for /game/status retrieval
        session.character_id = character_id
        session.status = "playing"
        session.corvus_internal_game_id = corvus_game_id
        session.updated_at = datetime.utcnow()

        await self.db.flush()
        # Commit handled by get_db dependency

        logger.info(
            f"[CorvusAdapter] create_session: session={game_session_id}, "
            f"character={character.name}, corvus_game={corvus_game_id}"
        )

        # 5. Fetch initial scene from Corvus API
        try:
            game_state = await self.client.get_game(corvus_game_id)
            # Extract location/scenes from game state
            world_state = game_state.get("worldState", {})
            events = world_state.get("events", [])
            # Build initial_scene from whatever is available in the Corvus game state
            initial_scene = {
                "location": "default",
                "context": "",
                "history": events[-5:] if events else [],  # last 5 events
                "opening_text": events[0].get("message", "") if events and isinstance(events[0], dict) else "",
            }
        except Exception as e:
            logger.warning(f"[CorvusAdapter] get_game failed for initial_scene fallback: {e}")
            initial_scene = {
                "location": "default",
                "context": "",
                "history": [],
                "opening_text": "",
            }

        # 6. Return frontend-compatible response
        return {
            "game_session_id": str(session.id),
            "status": session.status,
            "engine_type": session.engine_type,
            "corvus_game_id": corvus_game_id,
            "initial_scene": initial_scene,
            "player": {
                "id": str(character.id),
                "name": character.name,
                "personality": personality_str or None,
                "backstory": character.description,
                "appearance": character.description,
                "initial_inventory": [],
            },
        }

    async def _resolve_character_id(self, session) -> uuid.UUID:
        """Resolve the character_id for the Corvus game session.

        CR-038 改造: 不再依赖 selected_player_candidate_id。
        直接从 Character 表取第一个 playable 角色。
        """
        try:
            from app.models.script import Character
            async with async_session_factory() as db:
                # CR-038: 直接取第一个 playable character
                char_stmt = select(Character).where(Character.playable == True).limit(1)
                char_result = await db.execute(char_stmt)
                character = char_result.scalar_one_or_none()
                if character:
                            logger.info(f"[CorvusAdapter] First playable character_id: {character.id}")
                            return character.id
                # Fallback: return first character
                all_chars = await db.execute(select(Character).limit(1))
                first_char = all_chars.scalar_one_or_none()
                if first_char:
                    logger.info(f"[CorvusAdapter] No playable character found, using fallback")
                    return first_char.id
        except Exception as e:
            logger.error(f"[CorvusAdapter] _resolve_character_id failed: {e}")
        # Last resort: return the candidate_id (may fail FK)
        return user_id  # fallback

    async def stream_turn(
        self,
        game_session_id: uuid.UUID,
        user_id: uuid.UUID,
        user_input: str,
    ) -> AsyncGenerator[str, None]:
        """Stream a game turn via SSE, translating Corvus events to frontend format.

        Steps:
        1. Query the CorvusGameSession, verify ownership + status=playing.
        2. Call CorvusClient.stream_message with the user input.
        3. Translate Corvus SSE events to frontend format via SSETranslator.
        4. Yield each translated event as an SSE data line.

        Args:
            game_session_id: The CorvusGameSession UUID.
            user_id: The authenticated user's UUID.
            user_input: The player's text input.

        Yields:
            SSE data lines (strings like 'data: {...}\n\n').
        """
        from app.core.exceptions import AppException

        # Use independent session for all DB ops to avoid greenlet conflicts
        translator = SSETranslator()
        restore_list = []
        lock = self._get_lock(game_session_id)

        try:
            async with async_session_factory() as db:
                stmt = select(CorvusGameSession).where(
                    CorvusGameSession.id == game_session_id,
                )
                result = await db.execute(stmt)
                session = result.scalar_one_or_none()

                if not session:
                    raise AppException("SESSION_NOT_FOUND", 404, f"Session {game_session_id} not found")
                if session.user_id != user_id:
                    raise AppException("SESSION_FORBIDDEN", 403, "Access denied")
                if session.status != "playing":
                    raise AppException("SESSION_INVALID_STATUS", 400, f"Status is '{session.status}', expected 'playing'")
                corvus_game_id = session.corvus_internal_game_id
                if not corvus_game_id:
                    raise AppException("CORVUS_GAME_ID_MISSING", 500, "No corvus_internal_game_id")

                async with lock:
                    char_id = await self._resolve_character_id(session)
                    restore_list = await self.recall_and_inject(
                        game_session_id=game_session_id,
                        user_id=user_id,
                        character_id=char_id,
                        user_input=user_input,
                        corvus_game_id=corvus_game_id,
                    )

                self._collected_gm_updates = []
                self._collected_done_texts = []
                self._char_id = char_id
                self._user_id = user_id
                self._game_session_id = game_session_id
                self._corvus_game_id = corvus_game_id
                self._restore_list = restore_list

            # Stream outside of DB session context
            async for corvus_event in self.client.stream_message(
                corvus_game_id, user_input
            ):
                if corvus_event.get("type") == "gm_update":
                    self._collected_gm_updates.append(corvus_event)
                if corvus_event.get("type") == "done":
                    done_text = corvus_event.get("content", corvus_event.get("message", {}).get("content", ""))
                    if done_text:
                        self._collected_done_texts.append(done_text)
                for frontend_event in translator.translate(corvus_event):
                    yield f"data: {json.dumps(frontend_event, ensure_ascii=False)}\n\n"

                # On stream_end, process deferred DB ops in same async context
                if corvus_event.get("type") == "stream_end":
                    logger.warning(f"[CorvusAdapter] stream_end received, processing deferred: {len(self._collected_gm_updates)} gm_updates, {len(self._collected_done_texts)} done_texts")
                    # Restore NPC knownInfo
                    if restore_list:
                        try:
                            await self.restore_npc_knowninfo(corvus_game_id, restore_list)
                            logger.warning("[CorvusAdapter] NPC knownInfo restored")
                        except Exception as e:
                            logger.error(f"[CorvusAdapter] restore_npc_knowninfo: {e}", exc_info=True)
                    # Sync world state
                    for gm_event in self._collected_gm_updates:
                        try:
                            await self.sync_world_state(game_session_id, gm_event)
                        except Exception as e:
                            logger.error(f"[CorvusAdapter] sync_world_state deferred: {e}", exc_info=True)
                    # Write memories
                    for d_text in self._collected_done_texts:
                        try:
                            await self.write_memory(
                                user_id=user_id,
                                character_id=char_id,
                                dialogue_text=d_text,
                                game_session_id=game_session_id,
                            )
                            logger.warning("[CorvusAdapter] write_memory done")
                        except Exception as e:
                            logger.error(f"[CorvusAdapter] write_memory deferred: {e}", exc_info=True)

        except httpx.ConnectError as e:
            logger.error(f"[CorvusAdapter] SSE connect failed: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'Corvus 服务连接失败，请重试'}, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"[CorvusAdapter] SSE stream error: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': '服务器内部错误，请重试'}, ensure_ascii=False)}\n\n"

    async def deferred_finalize(self) -> None:
        """Execute deferred DB operations after SSE stream completes.

        Called by the endpoint's event_generator finally block.
        Uses independent DB sessions to avoid greenlet conflicts.
        """
        # Restore NPC knownInfo
        if hasattr(self, '_restore_list') and hasattr(self, '_corvus_game_id'):
            try:
                async with async_session_factory() as db:
                    await self.restore_npc_knowninfo(self._corvus_game_id, self._restore_list)
            except Exception as e:
                logger.error(f"[CorvusAdapter] deferred restore_npc_knowninfo failed: {e}", exc_info=True)

        # Sync world state from collected gm_update events
        if hasattr(self, '_collected_gm_updates') and self._collected_gm_updates:
            for gm_event in self._collected_gm_updates:
                try:
                    await self.sync_world_state(self._game_session_id, gm_event)
                except Exception as e:
                    logger.error(f"[CorvusAdapter] deferred sync_world_state failed: {e}", exc_info=True)

        # Write memories from collected done texts
        if hasattr(self, '_collected_done_texts') and self._collected_done_texts:
            for done_text in self._collected_done_texts:
                try:
                    await self.write_memory(
                        user_id=self._user_id,
                        character_id=self._char_id,
                        dialogue_text=done_text,
                        game_session_id=self._game_session_id,
                    )
                except Exception as e:
                    logger.error(f"[CorvusAdapter] deferred write_memory failed: {e}", exc_info=True)

    async def sync_world_state(
        self,
        game_session_id: uuid.UUID,
        gm_event: dict,
    ) -> None:
        """DEV-005: Async sync world_state from Corvus gm_update event to DB.

        Uses an independent DB session to avoid conflicts with the
        request-scoped session used by stream_turn.
        """
        try:
            async with async_session_factory() as db:
                await self._sync_world_state_impl(db, game_session_id, gm_event)
        except Exception as e:
            logger.error(f"[CorvusAdapter] sync_world_state error: {e}", exc_info=True)

    async def _sync_world_state_impl(
        self,
        db: AsyncSession,
        game_session_id: uuid.UUID,
        gm_event: dict,
    ) -> None:
        """Internal implementation of sync_world_state using a provided db session."""
        try:
            summary = gm_event.get("summary", {})
            player = gm_event.get("player", {})
            characters = gm_event.get("characters", [])
            world_state = gm_event.get("worldState", {})

            # Log what we received for debugging
            logger.info(
                f"[CorvusAdapter] sync_world_state called: "
                f"statChanges={len(summary.get('statChanges', []))}, "
                f"inventoryChanges={len(summary.get('inventoryChanges', []))}, "
                f"worldEvents={len(summary.get('worldEvents', []))}, "
                f"relationships={len(player.get('relationships', []))}, "
                f"player_inventory={len(player.get('inventory', []))}, "
                f"characters={len(characters)}, "
                f"ws_events={len(world_state.get('events', []))}"
            )

            # AC-012: Sync affinity
            stat_changes = summary.get("statChanges", [])
            relationship_changes = summary.get("relationshipChanges", [])
            if stat_changes:
                await self._sync_affinity(db, game_session_id, stat_changes)
            else:
                relationships = player.get("relationships", [])
                if relationships:
                    await self._sync_affinity_from_relationships(db, game_session_id, relationships, characters)
                elif characters:
                    await self._sync_affinity_from_characters(db, game_session_id, characters, relationship_changes)

            # AC-013: Sync inventory
            inventory_changes = summary.get("inventoryChanges", [])
            if inventory_changes:
                await self._sync_inventory(db, game_session_id, inventory_changes)
            else:
                player_inventory = player.get("inventory", [])
                if player_inventory:
                    await self._sync_inventory_from_snapshot(db, game_session_id, player_inventory)

            # AC-014: Sync story flags
            world_events = summary.get("worldEvents", [])
            if world_events:
                await self._sync_story_flags(db, game_session_id, world_events)
            else:
                ws_events = world_state.get("events", [])
                if ws_events:
                    await self._sync_story_flags(db, game_session_id, ws_events)

            # Also sync NPCs from characters[] if session_npcs is empty
            if characters:
                await self._sync_npcs_from_characters(db, game_session_id, characters)

            await db.commit()
            logger.info(f"[CorvusAdapter] sync_world_state completed for session {game_session_id}")
        except Exception as e:
            logger.error(f"[CorvusAdapter] sync_world_state error: {e}", exc_info=True)
            # Don't re-raise: this is a background task, errors should not
            # crash the SSE stream
            await db.rollback()

    async def _sync_affinity_from_relationships(
        self,
        db: AsyncSession,

        game_session_id: uuid.UUID,
        relationships: list,
        characters: list,
    ) -> None:
        """AC-012 fallback: Sync affinity from player.relationships."""
        for rel in relationships:
            if not isinstance(rel, dict):
                continue
            npc_name = rel.get("character", rel.get("name", ""))
            affinity = rel.get("affinity", rel.get("value", 0))
            corvus_char_id = rel.get("characterId", rel.get("id", ""))
            if not npc_name and not corvus_char_id:
                continue

            if corvus_char_id:
                stmt = select(SessionNpc).where(
                    SessionNpc.game_session_id == game_session_id,
                    SessionNpc.corvus_character_id == str(corvus_char_id),
                )
            else:
                stmt = select(SessionNpc).where(
                    SessionNpc.game_session_id == game_session_id,
                    SessionNpc.name == npc_name,
                )
            result = await db.execute(stmt)
            npc = result.scalar_one_or_none()
            if npc:
                npc.affinity = affinity
            else:
                new_npc = SessionNpc(
                    game_session_id=game_session_id,
                    name=npc_name,
                    affinity=affinity,
                    corvus_character_id=str(corvus_char_id) if corvus_char_id else None,
                )
                db.add(new_npc)
            logger.info(f"[CorvusAdapter] affinity from relationship: {npc_name} = {affinity}")

    async def _sync_affinity_from_characters(
        self,
        db: AsyncSession,

        game_session_id: uuid.UUID,
        characters: list,
        relationship_changes: list | None = None,
    ) -> None:
        """AC-012 fallback: Sync affinity from characters[].dispositionTowardPlayer.

        If no numeric relationship/affinity field exists, fall back to
        dispositionTowardPlayer string heuristics:
        - friendly/友好/信任/喜爱 → positive value
        - hostile/敌/厌恶 → negative value
        - unknown/未知 → 0
        - complex/复杂/旧识 → small positive (10)

        Also process summary.relationshipChanges (string → delta):
        - 信任/trust → +10
        - 友好/friendly → +5
        - 敌意/hostile → -10
        - 犹豫/hesitant → +2
        """
        # AC-014: Process relationshipChanges for delta updates
        rel_deltas: dict[str, int] = {}
        if relationship_changes:
            for rc in relationship_changes:
                if not isinstance(rc, str):
                    continue
                # Format: "character_name: keyword" or "char_id: keyword"
                parts = rc.split(':', 1)
                if len(parts) != 2:
                    continue
                rc_name = parts[0].strip()
                rc_keyword = parts[1].strip()
                delta = 0
                if any(k in rc_keyword for k in ["信任", "trust"]):
                    delta = 10
                elif any(k in rc_keyword for k in ["友好", "friendly", "喜爱"]):
                    delta = 5
                elif any(k in rc_keyword for k in ["敌", "hostile", "厌恶"]):
                    delta = -10
                elif any(k in rc_keyword for k in ["犹豫", "hesitant"]):
                    delta = 2
                elif any(k in rc_keyword for k in ["复杂", "complex"]):
                    delta = 3
                rel_deltas[rc_name] = delta

        for char in characters:
            if not isinstance(char, dict):
                continue
            npc_name = char.get("revealedName") or char.get("name", "")
            corvus_char_id = char.get("id", "")
            # Use relationship or affinity as numeric value if present
            relationship = char.get("relationship", char.get("affinity", 0))
            # If no numeric relationship, try dispositionTowardPlayer
            if not relationship:
                disposition = char.get("dispositionTowardPlayer", "")
                if isinstance(disposition, str):
                    if any(k in disposition for k in ["信任", "友好", "友善", "friend", "trust", "喜爱", "感兴趣"]):
                        relationship = 30
                    elif any(k in disposition for k in ["复杂", "complex"]):
                        relationship = 10
                    elif any(k in disposition for k in ["谨慎", "cautious", "curious", "好奇", "interested"]):
                        relationship = 5
                    elif any(k in disposition for k in ["未知", "unknown"]):
                        relationship = 0
                    elif any(k in disposition for k in ["敌", "hostile", "hate", "厌恶"]):
                        relationship = -30
                    else:
                        relationship = 0
            if not npc_name and not corvus_char_id:
                continue

            if corvus_char_id:
                stmt = select(SessionNpc).where(
                    SessionNpc.game_session_id == game_session_id,
                    SessionNpc.corvus_character_id == str(corvus_char_id),
                )
            else:
                stmt = select(SessionNpc).where(
                    SessionNpc.game_session_id == game_session_id,
                    SessionNpc.name == npc_name,
                )
            result = await db.execute(stmt)
            npc = result.scalar_one_or_none()

            base_affinity = int(relationship) if isinstance(relationship, (int, float)) else 0

            # AC-014: Apply relationshipChanges delta on top of existing DB value
            delta = 0
            if rel_deltas:
                # Match by name or corvus_char_id
                delta = rel_deltas.get(npc_name, rel_deltas.get(corvus_char_id, 0))

            if npc:
                # If we have a delta, apply it to existing value
                if delta:
                    npc.affinity = (npc.affinity or 0) + delta
                else:
                    # Set absolute value from disposition
                    if base_affinity:
                        npc.affinity = base_affinity
                logger.info(f"[CorvusAdapter] NPC affinity: {npc_name} = {npc.affinity} (base={base_affinity}, delta={delta})")
            else:
                new_affinity = base_affinity + delta
                new_npc = SessionNpc(
                    game_session_id=game_session_id,
                    name=npc_name,
                    affinity=new_affinity,
                    corvus_character_id=str(corvus_char_id) if corvus_char_id else None,
                )
                db.add(new_npc)
                logger.info(f"[CorvusAdapter] new NPC: {npc_name} affinity={new_affinity} (base={base_affinity}, delta={delta})")

    async def _sync_inventory_from_snapshot(
        self,
        db: AsyncSession,

        game_session_id: uuid.UUID,
        player_inventory: list,
    ) -> None:
        """AC-013 fallback: Sync inventory from player.inventory snapshot."""
        for item in player_inventory:
            if isinstance(item, dict):
                item_name = item.get("name", item.get("item", ""))
                quantity = item.get("quantity", 1)
                description = item.get("description", "")
            elif isinstance(item, str):
                item_name = item
                quantity = 1
                description = ""
            else:
                continue
            if not item_name:
                continue

            stmt = select(InventoryItem).where(
                InventoryItem.game_session_id == game_session_id,
                InventoryItem.name == item_name,
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if existing:
                existing.quantity = quantity
                if description:
                    existing.description = description
            else:
                new_item = InventoryItem(
                    game_session_id=game_session_id,
                    name=item_name,
                    description=description or None,
                    quantity=quantity,
                )
                db.add(new_item)
            logger.info(f"[CorvusAdapter] inventory snapshot: {item_name} x{quantity}")

    async def _sync_npcs_from_characters(
        self,
        db: AsyncSession,

        game_session_id: uuid.UUID,
        characters: list,
    ) -> None:
        """Sync NPCs from Corvus characters[] if not already in session_npcs."""
        for char in characters:
            if not isinstance(char, dict):
                continue
            npc_name = char.get("revealedName") or char.get("name", "")
            corvus_char_id = char.get("id", "")
            if not corvus_char_id:
                continue

            # Check if NPC already exists
            stmt = select(SessionNpc).where(
                SessionNpc.game_session_id == game_session_id,
                SessionNpc.corvus_character_id == str(corvus_char_id),
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            if not existing:
                new_npc = SessionNpc(
                    game_session_id=game_session_id,
                    name=npc_name,
                    affinity=0,
                    corvus_character_id=str(corvus_char_id),
                )
                db.add(new_npc)
                logger.info(f"[CorvusAdapter] new NPC from characters: {npc_name} ({corvus_char_id})")

    async def _sync_affinity(
        self,
        db: AsyncSession,

        game_session_id: uuid.UUID,
        stat_changes: list,
    ) -> None:
        """AC-012: Update session_npcs.affinity from statChanges."""
        for change in stat_changes:
            if not isinstance(change, dict):
                continue
            stat = change.get("stat", "")
            if stat != "affinity":
                continue

            delta = change.get("delta", 0)
            npc_name = change.get("character", change.get("name", ""))
            corvus_char_id = change.get("characterId", change.get("id", ""))

            # Find the NPC in session_npcs
            if corvus_char_id:
                stmt = select(SessionNpc).where(
                    SessionNpc.game_session_id == game_session_id,
                    SessionNpc.corvus_character_id == str(corvus_char_id),
                )
            elif npc_name:
                stmt = select(SessionNpc).where(
                    SessionNpc.game_session_id == game_session_id,
                    SessionNpc.name == npc_name,
                )
            else:
                continue

            result = await db.execute(stmt)
            npc = result.scalar_one_or_none()

            if npc:
                npc.affinity = (npc.affinity or 0) + delta
                logger.info(
                    f"[CorvusAdapter] affinity update: {npc_name} +{delta} → {npc.affinity}"
                )
            else:
                # Create new NPC entry if not found
                new_npc = SessionNpc(
                    game_session_id=game_session_id,
                    name=npc_name,
                    affinity=delta,
                    corvus_character_id=str(corvus_char_id) if corvus_char_id else None,
                )
                db.add(new_npc)
                logger.info(f"[CorvusAdapter] new NPC: {npc_name} affinity={delta}")

    async def _sync_inventory(
        self,
        db: AsyncSession,

        game_session_id: uuid.UUID,
        inventory_changes: list,
    ) -> None:
        """AC-013: Sync inventory_items from inventoryChanges."""
        for change in inventory_changes:
            if not isinstance(change, dict):
                continue

            action = change.get("action", "add")
            item_name = change.get("item", change.get("name", ""))
            if not item_name:
                continue

            if action in ("add", "update"):
                # Find existing item
                stmt = select(InventoryItem).where(
                    InventoryItem.game_session_id == game_session_id,
                    InventoryItem.name == item_name,
                )
                result = await db.execute(stmt)
                item = result.scalar_one_or_none()

                if item:
                    # Update quantity
                    if action == "update":
                        item.quantity = change.get("quantity", item.quantity)
                    else:  # add
                        item.quantity = (item.quantity or 1) + change.get("quantity", 1)
                    if change.get("description"):
                        item.description = change["description"]
                else:
                    # Create new item
                    new_item = InventoryItem(
                        game_session_id=game_session_id,
                        name=item_name,
                        description=change.get("description"),
                        quantity=change.get("quantity", 1),
                    )
                    db.add(new_item)
                    logger.info(f"[CorvusAdapter] inventory add: {item_name}")

            elif action == "remove":
                stmt = select(InventoryItem).where(
                    InventoryItem.game_session_id == game_session_id,
                    InventoryItem.name == item_name,
                )
                result = await db.execute(stmt)
                item = result.scalar_one_or_none()
                if item:
                    await db.delete(item)
                    logger.info(f"[CorvusAdapter] inventory remove: {item_name}")

    async def _sync_story_flags(
        self,
        db: AsyncSession,

        game_session_id: uuid.UUID,
        world_events: list,
    ) -> None:
        """AC-014: Upsert story_flags from worldEvents.

        Uses ON CONFLICT (game_session_id, flag_key) DO UPDATE to handle
        duplicate flag_key without error.
        """
        for event in world_events:
            if not isinstance(event, dict):
                continue

            flag_key = event.get("key", event.get("flag", event.get("name", "")))
            if not flag_key:
                continue

            flag_value = event.get("value", event)

            # Check if flag already exists
            stmt = select(StoryFlag).where(
                StoryFlag.game_session_id == game_session_id,
                StoryFlag.flag_key == flag_key,
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing flag value
                existing.flag_value = flag_value
                logger.info(f"[CorvusAdapter] story_flag update: {flag_key}")
            else:
                # Create new flag
                new_flag = StoryFlag(
                    game_session_id=game_session_id,
                    flag_key=flag_key,
                    flag_value=flag_value,
                )
                db.add(new_flag)
                logger.info(f"[CorvusAdapter] story_flag create: {flag_key}")

    # ── DEV-006: Vector memory methods ────────────────────────────────

    # Per-session locks for knownInfo restore
    _knowninfo_locks: dict[uuid.UUID, asyncio.Lock] = {}

    def _get_lock(self, session_id: uuid.UUID) -> asyncio.Lock:
        """Get or create an asyncio.Lock for a game session."""
        if session_id not in self._knowninfo_locks:
            self._knowninfo_locks[session_id] = asyncio.Lock()
        return self._knowninfo_locks[session_id]

    async def write_memory(
        self,
        user_id: uuid.UUID,
        character_id: uuid.UUID,
        dialogue_text: str,
        game_session_id: uuid.UUID,
    ) -> None:
        """AC-015: Write vector memory after assistant-complete event.

        Uses an independent DB session to avoid conflicts with the
        request-scoped session used by stream_turn.
        """
        async with async_session_factory() as db:
            embedding_svc = get_embedding_service()
            await embedding_svc.write_memory(
                db=db,
                user_id=user_id,
                character_id=character_id,
                memory_text=dialogue_text,
                source_session_id=None,  # FK points to game_sessions, not corvus_game_sessions
            )
            await db.commit()
            logger.warning(f"[CorvusAdapter] write_memory committed: user={user_id}, char={character_id}")

    async def recall_and_inject(
        self,
        game_session_id: uuid.UUID,
        user_id: uuid.UUID,
        character_id: uuid.UUID,
        user_input: str,
        corvus_game_id: str,
    ) -> list[dict]:
        """AC-016/017: Recall memories and inject into NPC knownInfo.

        Uses an independent DB session to avoid conflicts with the
        request-scoped session used by stream_turn.

        Steps:
        1. Generate embedding for user input.
        2. pgvector KNN search character_memories (WHERE user_id+character_id).
        3. Get NPCs from Corvus game.
        4. Append recalled memories to NPC knownInfo.
        5. Store original knownInfo for later restore.

        Returns list of {npc_id, original_knowninfo} for restore.
        """
        async with async_session_factory() as db:
            embedding_svc = get_embedding_service()
            recalled = await embedding_svc.recall(
                db=db,
                user_id=user_id,
                character_id=character_id,
                query_text=user_input,
            )

            if not recalled:
                return []

            # Get NPCs from Corvus
            try:
                npcs = await self.client.get_characters(corvus_game_id)
            except Exception as e:
                logger.warning(f"[CorvusAdapter] get_characters failed for recall: {e}")
                return []

            restore_list = []
            memory_text = "\n".join(f"[相关记忆] {m}" for m in recalled)

            for npc in npcs:
                npc_id = npc.get("id", "")
                if not npc_id:
                    continue
                original_knowninfo = npc.get("knownInfo", "")

                # Append recalled memories to knownInfo
                new_knowninfo = original_knowninfo
                if new_knowninfo:
                    new_knowninfo = new_knowninfo + "\n" + memory_text
                else:
                    new_knowninfo = memory_text

                try:
                    await self.client.update_npc_knowninfo(
                        corvus_game_id, npc_id, new_knowninfo
                    )
                    restore_list.append({
                        "npc_id": npc_id,
                        "original_knowninfo": original_knowninfo,
                    })
                    logger.info(
                        f"[CorvusAdapter] Injected memories into NPC {npc_id}"
                    )
                except Exception as e:
                    logger.warning(
                        f"[CorvusAdapter] update_npc_knowninfo failed for {npc_id}: {e}"
                    )

            return restore_list

    async def restore_npc_knowninfo(
        self,
        corvus_game_id: str,
        restore_list: list[dict],
    ) -> None:
        """AC-017: Restore NPC knownInfo to original values after a turn.

        Must be called with the session lock to ensure restore happens
        before next injection.
        """
        for item in restore_list:
            npc_id = item.get("npc_id", "")
            original = item.get("original_knowninfo", "")
            if not npc_id:
                continue
            try:
                await self.client.update_npc_knowninfo(
                    corvus_game_id, npc_id, original
                )
                logger.info(f"[CorvusAdapter] Restored knownInfo for NPC {npc_id}")
            except Exception as e:
                logger.warning(
                    f"[CorvusAdapter] restore knownInfo failed for {npc_id}: {e}"
                )


class SSETranslator:
    """Translate Corvus SSE events to frontend format.

    Corvus Event → Frontend Event mapping:
    - token → {"type":"text","content":"..."}  (逐字渲染)
    - narrator → filtered (internal, not sent to frontend)
    - done → {"type":"done","text":"...","character_id":"...","character_name":"..."}
    - gm_update → {"type":"gm_update",...world state...}  (好感度/道具/标记更新)
    - gm-start → filtered (internal marker)
    - user → filtered (echo of user message, not needed)
    - context-assembled → filtered (internal)
    - stream_end → {"type":"stream_end"}  (关闭连接)
    - error → {"type":"error","message":"..."}
    """

    # Corvus event types that are internal and filtered out
    _FILTERED_TYPES = {"user", "context-assembled", "narrator", "gm-start"}

    # CR-039 D1/BUG-039-001: Regex to strip [Narrator]/[Character] and [Character: name] markers from full text
    _ROLE_MARKER_RE = re.compile(r'\[(Narrator|Character|narrator|character)(\s*:\s*[^\]]*)?\]\s*\n?', re.UNICODE)

    # CR-039 D1/BUG-039-001: Detect start of a role marker in a token chunk (supports optional : name)
    _ROLE_MARKER_START_RE = re.compile(r'\[(Narrator|Character|narrator|character)(\s*:\s*[^\]]*)?\]', re.UNICODE)

    def __init__(self):
        # Buffer for accumulating token chunks that may contain partial role markers
        self._token_buffer = ""
        self._in_marker = False
        # CR-039 D1: Track whether we are inside a [Narrator] or [Character] block
        # When inside, tokens are suppressed until the marker is closed by \n
        # CR-039 D1: Partial marker detection — buffer up to max marker length + margin
        # BUG-039-001: Increase to accommodate [Character: name] format
        self._MAX_MARKER_LEN = len("[Character: 槐枝]") + 2  # +2 for \s*\n?

    def _strip_role_markers(self, text: str) -> str:
        """Remove [Narrator] and [Character] markers from full text (done event)."""
        if not text:
            return text
        return self._ROLE_MARKER_RE.sub('', text)

    def _process_token_chunk(self, content: str) -> str:
        """Process a single token chunk, filtering role markers that may span chunks.

n        Strategy: maintain a buffer. When we see a partial '[' that could be
        the start of a role marker, hold it back until we can determine if it
        is a [Narrator]/[Character] marker or regular text.
        """
        if not content:
            return content

        result = ""
        buf = self._token_buffer + content
        self._token_buffer = ""

        i = 0
        while i < len(buf):
            # Check if remaining text could be start of a role marker
            remaining = buf[i:]

            # Check for '[' that might begin a role marker
            if remaining[0] == '[':
                # Try to match a complete role marker
                marker_match = self._ROLE_MARKER_START_RE.match(remaining)
                if marker_match:
                    # Found a complete marker — skip it and trailing whitespace/newline
                    # NOTE: match end is relative to `remaining`, add i for absolute buf position
                    end = i + marker_match.end()
                    # Also consume any trailing \n or whitespace right after
                    while end < len(buf) and buf[end] in ('\n', '\r', ' '):
                        end += 1
                    i = end
                    continue

                # Check if remaining could be a prefix of a role marker
                # BUG-039-001: Also handle ':' after [Character for [Character: name] format
                prefixes = (
                    '[N', '[n', '[C', '[c',
                    '[Na', '[na', '[Ca', '[ca',
                    '[Nar', '[nar', '[Cha', '[cha',
                    '[Narr', '[narr', '[Char', '[char',
                    '[Narra', '[narra', '[Chara', '[chara',
                    '[Narrat', '[narrat', '[Charac', '[charac',
                    '[Narrato', '[narrato', '[Charact', '[charact',
                    '[Narrator', '[narrator', '[Character', '[character',
                    # [Character: name] prefixes — up to and including the colon
                    '[Character:', '[character:',
                    '[Narrator:', '[narrator:',
                )
                if remaining.startswith(prefixes):
                    # Hold this in buffer — might be a partial marker
                    self._token_buffer = buf[i:]
                    break
                else:
                    # Regular '[' — output it
                    result += buf[i]
                    i += 1
                    continue
            else:
                result += buf[i]
                i += 1

        # If buffer is too long (not a marker), flush it
        if len(self._token_buffer) > self._MAX_MARKER_LEN:
            result += self._token_buffer
            self._token_buffer = ""

        return result

    def _flush_token_buffer(self) -> str:
        """Flush any remaining buffered token content."""
        result = self._token_buffer
        self._token_buffer = ""
        return result

    def translate(self, corvus_event: dict) -> list[dict]:
        """Translate a Corvus SSE event to zero or more frontend events.

        Returns a list because some Corvus events may map to multiple
        frontend events (or none for filtered types).
        """
        event_type = corvus_event.get("type", "")

        if event_type in self._FILTERED_TYPES:
            return []

        if event_type == "token":
            content = corvus_event.get("content", "")
            # CR-039 D1: Filter [Narrator]/[Character] markers from token events
            filtered = self._process_token_chunk(content)
            if filtered:
                return [{"type": "text", "content": filtered}]
            return []

        if event_type == "done":
            # Flush any remaining buffered token content first
            buffered = self._flush_token_buffer()

            # Extract full text and character info from done event
            full_text = ""
            character_id = None
            character_name = None

            # Corvus done event may contain 'message' or 'content' field
            msg = corvus_event.get("message", corvus_event)
            if isinstance(msg, dict):
                full_text = msg.get("content", msg.get("text", ""))
                character_id = msg.get("characterId", msg.get("character_id"))
                character_name = msg.get("characterName", msg.get("character_name"))
            elif isinstance(msg, str):
                full_text = msg

            # CR-039 D1: Filter [Narrator]/[Character] markers from done text
            full_text = self._strip_role_markers(full_text)

            events = []
            if buffered:
                events.append({"type": "text", "content": buffered})
            events.append({
                "type": "done",
                "text": full_text,
                "character_id": str(character_id) if character_id else None,
                "character_name": character_name,
            })
            return events

        if event_type == "gm_update":
            # Extract world state changes
            summary = corvus_event.get("summary", {})
            stat_changes = summary.get("statChanges", [])
            inventory_changes = summary.get("inventoryChanges", [])
            relationship_changes = summary.get("relationshipChanges", [])
            new_characters = summary.get("newCharacters", [])
            world_events = summary.get("worldEvents", [])
            # CR-039: Extract playerOptions and map to frontend choices format
            player_options = corvus_event.get("playerOptions", [])
            choices = []
            if player_options and isinstance(player_options, list):
                choices = [
                    {
                        "id": str(i),
                        "text": opt.get("text", ""),
                        "hint": opt.get("hint", ""),
                    }
                    for i, opt in enumerate(player_options)
                    if isinstance(opt, dict)
                ]

            # CR-039 D2: Extract character_name from Corvus characters array
            # The first character in the array is the speaker
            characters = corvus_event.get("characters", [])
            gm_character_name = None
            if characters and isinstance(characters, list):
                for char in characters:
                    if isinstance(char, dict):
                        gm_character_name = char.get("revealedName") or char.get("name") or None
                        if gm_character_name:
                            break

            # CR-039 D3/AC-014: Extract affinity from player.relationships
            player = corvus_event.get("player", {})
            relationships = player.get("relationships", [])
            affinity_current = None
            if relationships and isinstance(relationships, list):
                for rel in relationships:
                    if not isinstance(rel, dict):
                        continue
                    rel_name = rel.get("character", rel.get("name", ""))
                    rel_affinity = rel.get("affinity", rel.get("value"))
                    if rel_affinity is not None:
                        affinity_current = rel_affinity
                        break

            # CR-039 D3: Fallback — extract disposition from characters array
            affinity_disposition = None
            if characters and isinstance(characters, list):
                for char in characters:
                    if isinstance(char, dict):
                        disposition = char.get("dispositionTowardPlayer")
                        if disposition:
                            affinity_disposition = disposition
                            break

            # AC-014: If no numeric affinity from relationships, compute from disposition string
            if affinity_current is None and affinity_disposition:
                disp = affinity_disposition
                if any(k in disp for k in ["信任", "友好", "友善", "friend", "trust", "喜爱", "感兴趣"]):
                    affinity_current = 30
                elif any(k in disp for k in ["复杂", "complex"]):
                    affinity_current = 10
                elif any(k in disp for k in ["谨慎", "cautious", "curious", "好奇", "interested"]):
                    affinity_current = 5
                elif any(k in disp for k in ["未知", "unknown"]):
                    affinity_current = 0
                elif any(k in disp for k in ["敌", "hostile", "hate", "厌恶"]):
                    affinity_current = -30
                else:
                    affinity_current = 0

            # AC-014: Also compute delta from relationshipChanges
            affinity_delta = 0
            if relationship_changes and isinstance(relationship_changes, list):
                for rc in relationship_changes:
                    if not isinstance(rc, str):
                        continue
                    parts = rc.split(':', 1)
                    if len(parts) != 2:
                        continue
                    rc_keyword = parts[1].strip()
                    if any(k in rc_keyword for k in ["信任", "trust"]):
                        affinity_delta += 10
                    elif any(k in rc_keyword for k in ["友好", "friendly", "喜爱"]):
                        affinity_delta += 5
                    elif any(k in rc_keyword for k in ["敌", "hostile", "厌恶"]):
                        affinity_delta -= 10
                    elif any(k in rc_keyword for k in ["犹豫", "hesitant"]):
                        affinity_delta += 2
                    elif any(k in rc_keyword for k in ["复杂", "complex"]):
                        affinity_delta += 3

            frontend_event = {
                "type": "gm_update",
            }

            # CR-039 D2: Add character_name from gm_update characters array
            if gm_character_name:
                frontend_event["character_name"] = gm_character_name

            # Add affinity deltas if present
            if stat_changes:
                frontend_event["affinity_deltas"] = stat_changes

            # CR-039 D3/AC-014: Add affinity_current (numeric)
            if affinity_current is not None:
                frontend_event["affinity_current"] = affinity_current

            # AC-014: Add affinity_delta (numeric, from relationshipChanges)
            if affinity_delta:
                frontend_event["affinity_delta"] = affinity_delta

            # CR-039 D3: Add affinity_disposition from characters array
            if affinity_disposition:
                frontend_event["affinity_disposition"] = affinity_disposition

            if inventory_changes:
                frontend_event["inventory_changes"] = inventory_changes

            if relationship_changes:
                frontend_event["relationship_changes"] = relationship_changes

            if new_characters:
                # newCharacters entries may be strings or dicts
                frontend_event["new_characters"] = [
                    c.get("name", c.get("id", "")) if isinstance(c, dict) else str(c)
                    for c in new_characters
                ]

            if world_events:
                frontend_event["world_events"] = world_events

            # CR-039: Always include choices (empty array = free-form input)
            frontend_event["choices"] = choices

            # Always yield gm_update even if empty (frontend can handle)
            return [frontend_event]

        if event_type == "stream_end":
            return [{"type": "stream_end"}]

        if event_type == "error":
            message = corvus_event.get("message", corvus_event.get("error", "Unknown error"))
            return [{"type": "error", "message": message}]

        # Unknown event type — pass through with warning
        logger.warning(f"[SSETranslator] Unknown Corvus event type: {event_type}")
        return [{"type": "unknown", "raw": corvus_event}]


# Need httpx import for exception handling in stream_turn
import httpx
