"""NarrativeEngine - orchestrates script state machine, LLM generation, rule validation,
memory recall, and affection updates into a unified dialogue/choice flow."""

import json
from typing import AsyncGenerator, Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.script import Node, Character, NodeChoice
from app.models.game import GameSession, GameProgress
from app.services.narrative.script_service import ScriptService
from app.services.narrative.rule_engine import RuleEngine, ValidationResult
from app.services.narrative.memory_service import MemoryService
from app.services.narrative.affection_service import AffectionService
from app.services.llm.gateway import llm_gateway
from app.core.exceptions import AppException


# Max retries for LLM generation when rule engine rejects output
MAX_RETRIES = 2

# Fallback dialogue per node (keyed by node_id string)
FALLBACK_DIALOGUES: Dict[str, str] = {
    # Default fallback when no node-specific fallback exists
    "_default": "The character pauses for a moment, gathering their thoughts...",
}


class NarrativeEngine:
    """
    Core narrative engine that orchestrates the game loop:

    1. Load current node from ScriptService
    2. If preset node → return preset content
    3. If transition node → generate via LLM with:
       - Character personality constraints
       - Memory recall injection
       - Emotion tagging
    4. Validate output via RuleEngine
    5. If validation fails → retry (max 2x) → fallback dialogue
    6. Apply affection changes from choice
    7. Extract and store memories asynchronously
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.script_service = ScriptService(db)
        self.rule_engine = RuleEngine(db)
        self.memory_service = MemoryService(db)
        self.affection_service = AffectionService(db)

    # ---- Main Dialogue Generation ----

    async def generate_dialogue(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        Generate dialogue for the current game state.

        Returns a structured response with text, emotion, choices, and metadata.
        """
        # 1. Get current session state
        state = await self.script_service.get_game_session_state(session_id)
        session = state["session"]
        current_node = state["current_node"]

        if state["is_ended"]:
            return {
                "type": "ending",
                "ending_type": session.ending_type or "normal",
                "session_id": str(session_id),
            }

        if not current_node:
            raise AppException(
                error_code="NARRATIVE_NO_NODE",
                status_code=400,
                message="Session has no current node to generate dialogue for",
            )

        # 2. Check node type
        node_type = current_node.node_type

        if node_type == "preset":
            # Preset node: return content directly
            return await self._handle_preset_node(current_node, session)

        elif node_type == "transition":
            # Transition node: LLM generation with validation
            return await self._handle_transition_node(current_node, session, user_id)

        elif node_type == "choice":
            # Choice node: return choices for player
            return await self._handle_choice_node(current_node, session, user_id)

        elif node_type == "ending":
            return await self._handle_ending_node(current_node, session)

        # New node types (CR-018 fix)
        elif node_type == "fixed_scene":
            return await self._handle_fixed_scene(current_node, session)

        elif node_type == "ai_dialog":
            return await self._handle_ai_dialog(current_node, session, user_id)

        elif node_type == "choice_point":
            return await self._handle_choice_point(current_node, session)

        elif node_type == "cg_trigger":
            return await self._handle_cg_trigger(current_node, session)

        elif node_type == "converge_node":
            return await self._handle_converge_node(current_node, session)

        else:
            # Unknown type, treat as preset
            return await self._handle_preset_node(current_node, session)

    async def generate_dialogue_stream(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> AsyncGenerator[str, None]:
        """
        SSE-compatible streaming dialogue generation.

        Yields JSON-encoded SSE events.
        """
        state = await self.script_service.get_game_session_state(session_id)
        session = state["session"]
        current_node = state["current_node"]

        if state["is_ended"]:
            yield self._sse_event("ending", {
                "ending_type": session.ending_type or "normal",
                "session_id": str(session_id),
            })
            return

        if not current_node:
            yield self._sse_event("error", {"message": "No current node"})
            return

        character_id = self.script_service.get_node_character_id(current_node)
        character = None
        if character_id:
            character = await self.script_service.get_character(character_id)

        if current_node.node_type == "preset":
            # Stream preset content
            content = current_node.content or {}
            text = content.get("text", "")
            emotion = content.get("emotion", "neutral")

            if character:
                yield self._sse_event("emotion", {
                    "emotion": emotion,
                    "character_id": str(character.id),
                })

            # Stream text word by word
            for word in text.split():
                yield self._sse_event("text", {
                    "content": word + " ",
                    "character_id": str(character.id) if character else None,
                })

        elif current_node.node_type == "transition" and character:
            # Stream LLM-generated content with validation
            dialogue = await self._generate_validated_dialogue(
                current_node, character, session, user_id
            )

            yield self._sse_event("emotion", {
                "emotion": dialogue.get("emotion", "neutral"),
                "character_id": str(character.id),
            })

            # Stream text
            text = dialogue.get("text", "")
            for word in text.split():
                yield self._sse_event("text", {
                    "content": word + " ",
                    "character_id": str(character.id),
                })

        # Emit choices if available
        if current_node.choices:
            filtered = await self._filter_choices(current_node.choices, session.user_id)
            options = self._choices_to_dicts(filtered, session.user_id)
            yield self._sse_event("choice", {"options": options})

        # Emit affection update if character exists
        if character_id:
            affection = await self.affection_service.get_affection(user_id, character_id)
            yield self._sse_event("affection_update", {
                "character_id": str(character_id),
                "value": affection.value,
                "level": affection.level,
            })

        # Done signal
        yield self._sse_event("done", {
            "session_id": str(session_id),
            "node_id": str(current_node.id),
        })

    # ---- Custom Input Processing ----

    async def process_custom_input(
        self,
        session_id: UUID,
        user_id: UUID,
        user_text: str,
    ) -> Dict[str, Any]:
        """
        玩家自由输入推进剧情。

        流程：
        1. 获取当前节点和角色信息
        2. 通过 LLM 生成角色回应
        3. 记录到对话历史
        4. 提取记忆
        5. 返回角色回应 + 下一步选项
        """
        # 1. 获取当前状态
        state = await self.script_service.get_game_session_state(session_id)
        session = state["session"]
        current_node = state["current_node"]

        if state["is_ended"]:
            return {
                "type": "ending",
                "ending_type": session.ending_type or "normal",
                "session_id": str(session_id),
            }

        if not current_node:
            raise AppException(
                error_code="NARRATIVE_NO_NODE",
                status_code=400,
                message="Session has no current node",
            )

        # 2. 获取角色信息
        character_id = self.script_service.get_node_character_id(current_node)
        character = None
        if character_id:
            character = await self.script_service.get_character(character_id)

        # 3. 生成角色回应
        if character:
            # 有角色 → 用 LLM 生成角色回应
            dialogue = await self._generate_custom_response(
                node=current_node,
                character=character,
                session=session,
                user_id=user_id,
                user_text=user_text,
            )
            response_text = dialogue.get("text", "")
            emotion = dialogue.get("emotion", "neutral")
        else:
            # 无角色 → 用 LLM 生成旁白回应
            response_text = await self._generate_narrator_response(
                node=current_node,
                session=session,
                user_text=user_text,
            )
            emotion = "neutral"

        # 4. 记录到 choice_history（复用字段存储自定义输入）
        if session.choice_history is None:
            session.choice_history = []
        session.choice_history.append({
            "type": "custom_input",
            "user_text": user_text,
            "node_id": str(current_node.id),
        })
        await self.db.commit()

        # 5. 提取记忆
        if character_id and response_text:
            await self.memory_service.extract_and_store(
                user_id=user_id,
                character_id=character_id,
                dialogue_text=f"用户: {user_text}\n{character.name}: {response_text}",
                session_id=session_id,
            )

        # 6. 返回结果
        result = {
            "type": "dialogue",
            "text": response_text,
            "emotion": emotion,
            "node_id": str(current_node.id),
            "session_id": str(session_id),
            "is_custom": True,
        }

        if character:
            result["character_id"] = str(character.id)

        # 如果有选项，也返回（让玩家可以继续选择）
        if current_node.choices:
            filtered = await self._filter_choices(current_node.choices, session.user_id)
            result["choices"] = self._choices_to_dicts(filtered, session.user_id)

        return result

    async def _generate_custom_response(
        self,
        node: Node,
        character: Character,
        session: GameSession,
        user_id: UUID,
        user_text: str,
    ) -> Dict[str, str]:
        """用 LLM 生成角色对玩家自由输入的回应。"""
        # 获取好感度
        affection_value = await self.rule_engine.get_affection_for_character(
            user_id, character.id
        )

        # 回忆相关记忆
        memory_context = ""
        memories = await self.memory_service.recall(
            user_id=user_id,
            character_id=character.id,
            query_text=user_text,
        )
        if memories:
            memory_lines = [f"- {m['memory_text']}" for m in memories]
            memory_context = "相关回忆:\n" + "\n".join(memory_lines)

        # 构建对话历史
        conversation_history = []
        if session.choice_history:
            for entry in session.choice_history[-5:]:
                if entry.get("type") == "custom_input":
                    conversation_history.append({
                        "role": "user",
                        "content": entry.get("user_text", ""),
                    })
                else:
                    conversation_history.append({
                        "role": "assistant",
                        "content": f"[之前的互动]",
                    })

        scene_context = (node.content or {}).get("scene", "")
        node_context = (node.content or {}).get("context", "")

        # 注入角色人设
        from app.llm.prompts.character_personas import get_character_persona
        persona = await get_character_persona(str(character.id), self.db)
        persona_context = (
            f"\n\n## 角色设定\n"
            f"- 姓名：{persona['name']}\n"
            f"- 性格：{persona['traits']}\n"
            f"- 说话风格：{persona['speak_style']}"
        )

        for attempt in range(MAX_RETRIES + 1):
            try:
                text = await llm_gateway.generate_dialogue(
                    character_name=character.name,
                    character_personality=(character.description or character.dialogue_style or "neutral") + persona_context,
                    context=f"{memory_context}\n场景: {scene_context}\n{node_context}\n好感度: {affection_value}",
                    user_input=user_text,
                    conversation_history=conversation_history,
                )

                validation = await self.rule_engine.validate_dialogue(
                    text=text,
                    character=character,
                    affection_value=affection_value,
                    current_node=node,
                )

                if validation.passed:
                    return {
                        "text": text,
                        "emotion": self._infer_emotion(text, node),
                    }
            except Exception:
                pass

        # fallback
        return {
            "text": f"{character.name}沉思了一会儿，似乎对你的话有所感悟...",
            "emotion": "neutral",
        }

    async def _generate_narrator_response(
        self,
        node: Node,
        session: GameSession,
        user_text: str,
    ) -> str:
        """用 LLM 生成旁白对玩家自由输入的回应。"""
        scene_context = (node.content or {}).get("scene", "")

        for attempt in range(MAX_RETRIES + 1):
            try:
                text = await llm_gateway.generate_story_narrative(
                    context=f"场景: {scene_context}\n当前剧情节点的内容",
                    player_choice=user_text,
                    narrative_style="immersive",
                )
                if text:
                    return text
            except Exception:
                pass

        return f"你的行动在这片空间中引起了微妙的变化..."

    # ---- Choice Processing ----

    async def process_choice(
        self,
        session_id: UUID,
        user_id: UUID,
        choice_id: UUID,
    ) -> Dict[str, Any]:
        """
        Process a player's choice:
        1. Apply affection delta
        2. Track choice streak (CR3-049)
        3. Advance session to next node
        4. Extract memories from the interaction
        5. Check for ending if session completed (CR3-050)
        """
        # Get current state before advancing
        state = await self.script_service.get_game_session_state(session_id)
        current_node = state["current_node"]
        character_id = self.script_service.get_node_character_id(current_node) if current_node else None

        # Get the choice object
        choice_obj = None
        if current_node:
            for c in (current_node.choices or []):
                if c.id == choice_id:
                    choice_obj = c
                    break

        # Apply affection change
        affection_change = None
        if character_id:
            affection_change = await self.affection_service.apply_choice_delta(user_id, choice_id)

        # Track choice streak (CR3-049)
        streak_event = None
        if choice_obj:
            from app.services.choice_streak import ChoiceStreakService
            streak_service = ChoiceStreakService(self.db)
            streak_event = await streak_service.record_and_check(user_id, session_id, choice_obj)

        # Advance the session
        new_state = await self.script_service.advance_session(session_id, choice_id)

        # Extract memories asynchronously
        if character_id and current_node:
            choice_text = ""
            for c in (current_node.choices or []):
                if c.id == choice_id:
                    choice_text = c.text
                    break
            if choice_text:
                await self.memory_service.extract_and_store(
                    user_id=user_id,
                    character_id=character_id,
                    dialogue_text=choice_text,
                    session_id=session_id,
                )

        result = {
            "session_id": str(session_id),
            "is_ended": new_state["is_ended"],
            "next_node_id": str(new_state["current_node"].id) if new_state["current_node"] else None,
        }

        if affection_change:
            # Fetch character name
            character_name = None
            if character_id:
                character = await self.script_service.get_character(character_id)
                if character:
                    character_name = character.name
            
            result["affection_change"] = {
                "character_id": str(character_id),
                "character_name": character_name,
                "delta": affection_change.delta,
                "old_value": affection_change.old_value,
                "new_value": affection_change.new_value,
                "old_level": affection_change.old_level,
                "new_level": affection_change.new_level,
                "level_changed": affection_change.level_changed,
            }

        # Add streak event if triggered
        if streak_event:
            result["streak_event"] = streak_event

        # Check for ending if session completed (CR3-050)
        if new_state["is_ended"]:
            # DEV-BE-010: Affection-based ending calculation
            if character_id:
                affection = await self.affection_service.get_affection(user_id, character_id)
                ending_type = self.affection_service.calculate_ending(affection.value, str(character_id))
                result["ending_type"] = ending_type
                result["ending_triggered"] = True
            
            # Legacy: Complex ending calculation (CR3-050)
            from app.services.ending_calculator import EndingCalculator
            ending_calc = EndingCalculator(self.db)
            ending_info = await ending_calc.calculate(session_id, user_id, character_id)
            result["ending"] = ending_info

        return result

    # ---- Node Handlers ----

    async def _handle_preset_node(
        self, node: Node, session: GameSession
    ) -> Dict[str, Any]:
        """Handle a preset (scripted) node."""
        content = node.content or {}
        result = {
            "type": "dialogue",
            "node_type": "preset",
            "node_id": str(node.id),
            "text": content.get("text", ""),
            "emotion": content.get("emotion", "neutral"),
            "scene": content.get("scene"),
            "character_id": content.get("character_id"),
            "background": node.background,
        }

        if node.choices:
            filtered = await self._filter_choices(node.choices, session.user_id)
            result["choices"] = self._choices_to_dicts(filtered, session.user_id)

        return result

    async def _handle_transition_node(
        self, node: Node, session: GameSession, user_id: UUID
    ) -> Dict[str, Any]:
        """Handle a transition (LLM-generated) node."""
        character_id = self.script_service.get_node_character_id(node)
        character = None
        if character_id:
            character = await self.script_service.get_character(character_id)

        if not character:
            # No character, return preset content
            return await self._handle_preset_node(node, session)

        dialogue = await self._generate_validated_dialogue(node, character, session, user_id)

        result = {
            "type": "dialogue",
            "node_type": "transition",
            "node_id": str(node.id),
            "text": dialogue.get("text", ""),
            "emotion": dialogue.get("emotion", "neutral"),
            "character_id": str(character.id),
            "background": node.background,
        }

        if node.choices:
            filtered = await self._filter_choices(node.choices, session.user_id)
            result["choices"] = self._choices_to_dicts(filtered, session.user_id)

        return result

    async def _handle_choice_node(
        self, node: Node, session: GameSession, user_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Handle a choice node — returns available choices (filtered by affection)."""
        content = node.content or {}
        choices = await self._filter_choices(node.choices or [], session.user_id)
        return {
            "type": "choice",
            "node_id": str(node.id),
            "text": content.get("text", ""),
            "choices": [
                {
                    "id": str(c.id),
                    "text": c.text,
                    "affection_delta": c.affection_delta,
                    "hint": c.hint,
                    "is_hidden": c.is_hidden and not self._meets_affection(c, session.user_id),
                }
                for c in choices
            ],
        }

    async def _handle_ending_node(
        self, node: Node, session: GameSession
    ) -> Dict[str, Any]:
        """Handle an ending node."""
        content = node.content or {}
        return {
            "type": "ending",
            "node_id": str(node.id),
            "ending_type": content.get("ending_type", "normal"),
            "text": content.get("text", "The story has come to an end."),
            "session_id": str(session.id),
        }

    async def _handle_fixed_scene(
        self, node: Node, session: GameSession
    ) -> Dict[str, Any]:
        """Handle a fixed_scene node — returns preset scene content."""
        content = node.content or {}
        result = {
            "type": "dialogue",
            "node_type": "fixed_scene",
            "node_id": str(node.id),
            "text": content.get("content") or content.get("text") or content.get("title", ""),
            "emotion": content.get("emotion", "neutral"),
            "scene": content.get("title"),
        }
        # Check for choices on this node
        if node.choices:
            filtered = await self._filter_choices(node.choices, session.user_id)
            result["choices"] = self._choices_to_dicts(filtered, session.user_id)
        return result

    async def _handle_ai_dialog(
        self, node: Node, session: GameSession, user_id: UUID
    ) -> Dict[str, Any]:
        """Handle an ai_dialog node — generates LLM dialogue based on node content."""
        content = node.content or {}
        character_name = content.get("character", "角色")
        dialogue_hint = content.get("dialogue", "")
        
        # Try to get character info for better generation
        character_id = self.script_service.get_node_character_id(node)
        character = None
        if character_id:
            character = await self.script_service.get_character(character_id)
        
        if character:
            # Use LLM to generate dialogue
            dialogue = await self._generate_validated_dialogue(node, character, session, user_id)
            result = {
                "type": "dialogue",
                "node_type": "ai_dialog",
                "node_id": str(node.id),
                "text": dialogue.get("text", dialogue_hint or f"{character.name}看着你，似乎想说什么..."),
                "emotion": dialogue.get("emotion", "neutral"),
                "character_id": str(character.id),
            }
        else:
            # No character, use hint or fallback
            result = {
                "type": "dialogue",
                "node_type": "ai_dialog",
                "node_id": str(node.id),
                "text": dialogue_hint or f"{character_name}似乎想对你说些什么...",
                "emotion": content.get("emotion", "neutral"),
            }
        
        # Check for choices
        if node.choices:
            filtered = await self._filter_choices(node.choices, session.user_id)
            result["choices"] = self._choices_to_dicts(filtered, session.user_id)
        
        return result

    async def _handle_choice_point(
        self, node: Node, session: GameSession
    ) -> Dict[str, Any]:
        """Handle a choice_point node — returns choices for player."""
        content = node.content or {}
        choices = await self._filter_choices(node.choices or [], session.user_id)
        return {
            "type": "choice",
            "node_type": "choice_point",
            "node_id": str(node.id),
            "text": content.get("text") or content.get("title", "请做出你的选择"),
            "choices": [
                {
                    "id": str(c.id),
                    "text": c.text,
                    "affection_delta": c.affection_delta,
                    "hint": c.hint,
                    "is_hidden": c.is_hidden and not self._meets_affection(c, session.user_id),
                }
                for c in choices
            ],
        }

    async def _handle_cg_trigger(
        self, node: Node, session: GameSession
    ) -> Dict[str, Any]:
        """Handle a cg_trigger node — triggers CG unlock and returns dialogue."""
        content = node.content or {}
        cg_title = content.get("title", "特殊CG")
        cg_description = content.get("description", "你解锁了一张特殊CG！")
        cg_image = content.get("image")
        
        # Record unlock event for frontend to display
        try:
            from app.services.unlock_service import UnlockService
            unlock_svc = UnlockService(self.db)
            await unlock_svc.record_unlock(
                user_id=session.user_id,
                unlock_type="cg",
                content_id=str(node.id),
                title=cg_title,
                description=cg_description,
                image_url=cg_image,
                rarity=content.get("rarity", "SR"),
            )
        except Exception as e:
            # Log but don't fail if unlock service fails
            import logging
            logging.getLogger(__name__).warning(f"Failed to record CG unlock: {e}")
        
        result = {
            "type": "dialogue",
            "node_type": "cg_trigger",
            "node_id": str(node.id),
            "text": content.get("text") or cg_description,
            "emotion": content.get("emotion", "happy"),
            "cg_unlock": {
                "title": cg_title,
                "description": cg_description,
                "image": cg_image,
                "rarity": content.get("rarity", "SR"),
            },
        }
        
        # Check for choices
        if node.choices:
            filtered = await self._filter_choices(node.choices, session.user_id)
            result["choices"] = self._choices_to_dicts(filtered, session.user_id)
        
        return result

    async def _handle_converge_node(
        self, node: Node, session: GameSession
    ) -> Dict[str, Any]:
        """Handle a converge_node — triggers convergence scene and returns dialogue."""
        content = node.content or {}
        converge_title = content.get("title", "故事汇聚")
        converge_description = content.get("description", "命运的线索在此交汇...")
        
        # Record unlock event for frontend
        try:
            from app.services.unlock_service import UnlockService
            unlock_svc = UnlockService(self.db)
            await unlock_svc.record_unlock(
                user_id=session.user_id,
                unlock_type="hidden_story",
                content_id=str(node.id),
                title=converge_title,
                description=converge_description,
                rarity=content.get("rarity", "SR"),
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to record converge unlock: {e}")
        
        result = {
            "type": "dialogue",
            "node_type": "converge_node",
            "node_id": str(node.id),
            "text": content.get("text") or converge_description,
            "emotion": content.get("emotion", "surprised"),
            "convergence_reached": True,
            "convergence_point": {
                "id": str(node.id),
                "title": converge_title,
                "description": converge_description,
            },
        }
        
        # Check for choices
        if node.choices:
            filtered = await self._filter_choices(node.choices, session.user_id)
            result["choices"] = self._choices_to_dicts(filtered, session.user_id)
        
        return result

    # ---- LLM Generation + Validation Loop ----

    async def _generate_validated_dialogue(
        self,
        node: Node,
        character: Character,
        session: GameSession,
        user_id: UUID,
    ) -> Dict[str, str]:
        """
        Generate dialogue with LLM, validate via RuleEngine, retry or fallback.

        Flow:
        1. Recall relevant memories
        2. Build context + prompt
        3. Generate via LLM
        4. Validate via RuleEngine
        5. If fail → retry (max 2x)
        6. If still fail → use fallback dialogue
        """
        # Get affection for rule checking
        affection_value = await self.rule_engine.get_affection_for_character(
            user_id, character.id
        )

        # Recall relevant memories
        memory_context = ""
        node_text = (node.content or {}).get("text", "")
        memories = await self.memory_service.recall(
            user_id=user_id,
            character_id=character.id,
            query_text=node_text or character.description or "",
        )
        if memories:
            memory_lines = [f"- {m['memory_text']}" for m in memories]
            memory_context = "Relevant memories:\n" + "\n".join(memory_lines)

        # Build conversation history from session
        conversation_history = []
        if session.choice_history:
            for entry in session.choice_history[-5:]:
                conversation_history.append({
                    "role": "assistant",
                    "content": f"[Previous interaction at node {entry.get('node_id', 'unknown')}]",
                })

        # Generate + validate loop
        for attempt in range(MAX_RETRIES + 1):
            try:
                text = await llm_gateway.generate_dialogue(
                    character_name=character.name,
                    character_personality=character.description or character.dialogue_style or "neutral",
                    context=memory_context + "\n" + (node.content or {}).get("context", ""),
                    user_input=node_text or "Continue the conversation.",
                    conversation_history=conversation_history,
                )

                # Validate
                validation = await self.rule_engine.validate_dialogue(
                    text=text,
                    character=character,
                    affection_value=affection_value,
                    current_node=node,
                )

                if validation.passed:
                    return {
                        "text": text,
                        "emotion": self._infer_emotion(text, node),
                    }

            except Exception:
                # LLM failure, fall through to fallback
                pass

        # All retries exhausted — use fallback
        fallback = self._get_fallback(node)
        return {
            "text": fallback,
            "emotion": "neutral",
        }

    # ---- Helpers ----

    def _get_fallback(self, node: Node) -> str:
        """Get fallback dialogue for a node."""
        node_id_str = str(node.id)
        if node_id_str in FALLBACK_DIALOGUES:
            return FALLBACK_DIALOGUES[node_id_str]

        # Check node content for fallback
        if node.content and "fallback" in node.content:
            return node.content["fallback"]

        return FALLBACK_DIALOGUES["_default"]

    def _infer_emotion(self, text: str, node: Node) -> str:
        """Infer emotion from text content or node metadata."""
        # Check node content first
        if node.content and "emotion" in node.content:
            return node.content["emotion"]

        # Simple heuristic
        text_lower = text.lower()
        if any(w in text_lower for w in ["happy", "glad", "joy", "smile", "开心", "高兴"]):
            return "happy"
        if any(w in text_lower for w in ["sad", "sorry", "cry", "难过", "抱歉"]):
            return "sad"
        if any(w in text_lower for w in ["angry", "furious", "生气"]):
            return "angry"
        if any(w in text_lower for w in ["surprise", "wow", "惊讶"]):
            return "surprised"

        return "neutral"

    @staticmethod
    def _sse_event(event_type: str, data: dict) -> str:
        """Format an SSE event string."""
        return f"event: {event_type}\ndata: {json.dumps(data, default=str)}\n\n"

    # ---- Choice Filtering (CR3-047: Hidden Choices) ----

    async def _filter_choices(
        self, choices: list, user_id: UUID, character_id: UUID = None
    ) -> list:
        """
        Filter choices: hide choices that are marked is_hidden and where
        the user's affection does not meet required_affection.

        Non-hidden choices are always visible. Hidden choices become visible
        when affection >= required_affection.
        """
        visible = []
        affection_value = 0
        # Pre-fetch affection if we have a character
        if character_id:
            try:
                aff = await self.affection_service.get_affection(user_id, character_id)
                affection_value = aff.value
            except Exception:
                affection_value = 0

        for choice in choices:
            if not choice.is_hidden:
                # Non-hidden choices are always visible
                visible.append(choice)
            elif choice.required_affection <= 0:
                # Hidden but no affection requirement → always visible
                visible.append(choice)
            elif affection_value >= choice.required_affection:
                # Hidden but affection meets threshold → visible
                visible.append(choice)
            # else: hidden and affection too low → skip
        return visible

    def _choices_to_dicts(self, choices: list, user_id: UUID) -> list:
        """Convert choice objects to response dicts with hints (CR3-048)."""
        return [
            {
                "id": str(c.id),
                "text": c.text,
                "affection_delta": c.affection_delta,
                "hint": c.hint,
                "is_hidden": c.is_hidden,
                "required_affection": c.required_affection,
            }
            for c in choices
        ]

    def _meets_affection(self, choice, user_id: UUID) -> bool:
        """Synchronous affection check stub — always True (async check done in _filter_choices)."""
        return True
