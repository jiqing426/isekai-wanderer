"""LLM Gateway — unified entry point for all LLM operations.

Combines DEV-008 spec (prompt templates, emotion parsing, retry, SSE streaming)
with auto-degrade logic from services/llm/gateway.py.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from typing import AsyncIterator, List, Optional, Dict, Any

from app.core.config import settings
from app.core.exceptions import AppException, ErrorCode
from .providers.base import BaseLLMProvider, DialogueContext, Memory
from .providers.openai_provider import OpenAIProvider
from .providers.mock_provider import MockProvider
from .prompts.narrative import build_narrative_prompt, SYSTEM_PROMPT as NARRATIVE_SYSTEM_PROMPT
from .prompts.character import build_character_constraint
from .prompts.memory_extract import (
    build_memory_extract_prompt,
    build_memory_summary_prompt,
    MEMORY_EXTRACTION_SYSTEM,
)
from .prompts.style import build_style_prompt
from .streaming import stream_with_parsing, fallback_dialogue, SSEFormatter

logger = logging.getLogger(__name__)


@dataclass
class LLMMessage:
    """Single message in a conversation (compatibility shim for narrative services)."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from LLM provider (compatibility shim for narrative services)."""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class LLMGateway:
    """Unified gateway for LLM operations with retry, fallback, and rate limiting.

    Provides high-level methods for dialogue generation, streaming,
    and memory extraction. Handles retries and graceful degradation.

    Two calling conventions are supported:
      1. DEV-008 style: generate_dialogue(DialogueContext(...))
      2. Keyword style: generate_dialogue(character_name=..., user_input=...)
    """

    def __init__(self, provider: Optional[BaseLLMProvider] = None):
        if provider is not None:
            self.provider = provider
        else:
            if settings.llm_provider == "mock" or not settings.openai_api_key:
                self.provider = MockProvider()
            else:
                self.provider = OpenAIProvider(
                    api_key=settings.openai_api_key,
                    model=settings.openai_model or "gpt-4o-mini",
                )
        self.max_retries = 2

    # ---- Context normalizer ----

    def _normalize_context(
        self,
        args: tuple,
        character_name: str = "",
        character_personality: str = "",
        context: str = "",
        user_input: str = "",
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> DialogueContext:
        """Convert positional/keyword args into a DialogueContext."""
        # Positional DialogueContext
        if args and isinstance(args[0], DialogueContext):
            return args[0]

        history = conversation_history or []
        history_strings = [
            f"{m.get('role', 'user')}: {m['content']}" for m in history
        ]
        return DialogueContext(
            user_message=user_input,
            character_name=character_name,
            character_persona=character_personality,
            conversation_history=history_strings,
            scene_description=context,
        )

    # ---- Dialogue generation ----

    async def generate_dialogue(
        self,
        *args,
        character_name: str = "",
        character_personality: str = "",
        context: str = "",
        user_input: str = "",
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """Generate a single dialogue response with retry logic."""
        ctx = self._normalize_context(
            args, character_name, character_personality,
            context, user_input, conversation_history,
        )

        prompt = self._build_dialogue_prompt(ctx)
        system_prompt = self._build_system_prompt(ctx)

        for attempt in range(self.max_retries + 1):
            try:
                return await self.provider.generate(
                    prompt,
                    system_prompt=system_prompt,
                    temperature=0.8,
                    max_tokens=512,
                )
            except Exception as e:
                logger.warning(f"Dialogue generation attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    raise AppException(
                        ErrorCode.LLM_GENERATION_FAILED,
                        503,
                        "AI generation failed after retries",
                    )
                await asyncio.sleep(0.5 * (attempt + 1))

        # unreachable
        raise AppException(ErrorCode.LLM_GENERATION_FAILED, 503, "AI generation failed")

    # ---- Streaming ----

    async def stream_dialogue(
        self,
        *args,
        character_name: str = "",
        character_personality: str = "",
        context: str = "",
        user_input: str = "",
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> AsyncIterator[str]:
        """Stream dialogue response as SSE events with retry + fallback."""
        ctx = self._normalize_context(
            args, character_name, character_personality,
            context, user_input, conversation_history,
        )

        prompt = self._build_dialogue_prompt(ctx)
        system_prompt = self._build_system_prompt(ctx)

        for attempt in range(self.max_retries + 1):
            try:
                async for event in stream_with_parsing(
                    self.provider, prompt, system_prompt,
                    character_id="", session_id="", node_id="",
                    temperature=0.8, max_tokens=512,
                ):
                    yield event
                return
            except Exception as e:
                logger.warning(f"Streaming attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    logger.error("Streaming failed, using fallback")
                    yield await fallback_dialogue("")
                    return
                await asyncio.sleep(0.5 * (attempt + 1))

    # ---- Memory extraction (list[str] compat for narrative services) ----

    async def extract_memory(
        self, dialogue: str, character_name: str = ""
    ) -> List[str]:
        """Extract memorable facts from dialogue (returns plain strings).

        This is the compatibility interface used by memory_service.
        """
        memories = await self.extract_memories(dialogue, character_name=character_name)
        return [m.content for m in memories if m.content]

    async def extract_memories(self, conversation: str, character_name: str = "") -> List[Memory]:
        """Extract memories from conversation text (returns Memory objects)."""
        prompt = build_memory_extract_prompt(conversation, character_name=character_name)

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.provider.generate(
                    prompt,
                    system_prompt=MEMORY_EXTRACTION_SYSTEM,
                    temperature=0.3,
                    max_tokens=1024,
                )
                return self._parse_memory_response(response)
            except Exception as e:
                logger.warning(f"Memory extraction attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    return []
                await asyncio.sleep(0.5 * (attempt + 1))
        return []

    async def summarize_memories(self, memories: List[str]) -> List[Memory]:
        """Compress and summarize old memories."""
        from .prompts.memory_extract import MEMORY_SUMMARY_SYSTEM

        prompt = build_memory_summary_prompt(memories)

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.provider.generate(
                    prompt,
                    system_prompt=MEMORY_SUMMARY_SYSTEM,
                    temperature=0.3,
                    max_tokens=512,
                )
                return self._parse_memory_response(response)
            except Exception as e:
                logger.warning(f"Memory summarization attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries:
                    return []
                await asyncio.sleep(0.5 * (attempt + 1))
        return []

    # ---- Embedding ----

    async def embed(self, text: str) -> List[float]:
        return await self.provider.embed(text)

    # ---- Provider.complete compat (for memory_service compress) ----

    async def complete(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Compatibility shim: messages-based complete() for narrative services.

        Converts LLMMessage list into a single prompt string and delegates
        to the underlying provider.generate().
        """
        system_parts = []
        user_parts = []
        for m in messages:
            if m.role == "system":
                system_parts.append(m.content)
            else:
                user_parts.append(f"{m.role}: {m.content}" if m.role != "user" else m.content)

        prompt = "\n\n".join(user_parts) if user_parts else "Continue."
        system_prompt = "\n\n".join(system_parts) if system_parts else "You are a helpful assistant."

        raw = await self.provider.generate(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return LLMResponse(
            content=raw,
            model=getattr(self.provider, "model", "unknown"),
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            finish_reason="stop",
        )

    async def stream_complete(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> AsyncIterator[str]:
        """Compatibility shim: messages-based stream for narrative services."""
        system_parts = []
        user_parts = []
        for m in messages:
            if m.role == "system":
                system_parts.append(m.content)
            else:
                user_parts.append(f"{m.role}: {m.content}" if m.role != "user" else m.content)

        prompt = "\n\n".join(user_parts) if user_parts else "Continue."
        system_prompt = "\n\n".join(system_parts) if system_parts else "You are a helpful assistant."

        async for chunk in self.provider.stream(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk

    # ---- Cleanup ----

    async def close(self) -> None:
        await self.provider.close()

    # ---- Prompt builders ----

    def _build_dialogue_prompt(self, context: DialogueContext) -> str:
        return build_narrative_prompt(
            character_name=context.character_name,
            character_persona=context.character_persona,
            user_message=context.user_message,
            conversation_history=context.conversation_history,
            memory_context=context.memory_context,
            emotion_state=context.emotion_state,
            scene_description=context.scene_description,
        )

    def _build_system_prompt(self, context: DialogueContext) -> str:
        parts = [NARRATIVE_SYSTEM_PROMPT]
        parts.append(
            build_character_constraint(
                character_name=context.character_name,
                personality=context.character_persona,
            )
        )
        if context.style_hint:
            parts.append(build_style_prompt(context.style_hint))
        return "\n\n".join(parts)

    def _parse_memory_response(self, response: str) -> List[Memory]:
        """Parse LLM JSON response into Memory objects."""
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            data = json.loads(cleaned)
            if not isinstance(data, list):
                logger.warning(f"Memory response is not a list: {data}")
                return []

            return [
                Memory(
                    content=item.get("content", ""),
                    importance=float(item.get("importance", 0.5)),
                    category=item.get("category", "general"),
                )
                for item in data
                if item.get("content")
            ]
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse memory response: {e}\nResponse: {response}")
            return []


# Global gateway instance (singleton for narrative services)
llm_gateway = LLMGateway()
