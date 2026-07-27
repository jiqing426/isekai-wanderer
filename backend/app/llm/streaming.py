"""SSE streaming helpers for LLM dialogue output."""

import asyncio
import json
import re
from typing import AsyncIterator, Optional
from .providers.base import BaseLLMProvider, DialogueContext


class SSEFormatter:
    """Format LLM output into SSE event stream."""

    EMOTION_PATTERN = re.compile(r"\[emotion:(\w+)\]", re.IGNORECASE)
    ACTION_PATTERN = re.compile(r"\[action:(\w+)\]", re.IGNORECASE)

    @staticmethod
    def format_text(content: str, character_id: str = "") -> str:
        """Format a text chunk as SSE event."""
        data = {"type": "text", "content": content, "character_id": character_id}
        return f"event: message\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    @staticmethod
    def format_emotion(emotion: str, character_id: str = "") -> str:
        """Format an emotion change as SSE event."""
        data = {"type": "emotion", "emotion": emotion, "character_id": character_id}
        return f"event: message\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    @staticmethod
    def format_done(session_id: str = "", node_id: str = "") -> str:
        """Format session-complete SSE event."""
        data = {"type": "done", "session_id": session_id, "node_id": node_id}
        return f"event: done\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    @staticmethod
    def format_error(error_code: str, message: str) -> str:
        """Format an error as SSE event."""
        data = {"type": "error", "error_code": error_code, "message": message}
        return f"event: error\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"

    @staticmethod
    def format_memory_recall(text: str) -> str:
        """Format a memory recall event."""
        data = {"type": "memory_recall", "text": text}
        return f"event: message\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def stream_with_parsing(
    provider: BaseLLMProvider,
    prompt: str,
    system_prompt: str,
    character_id: str = "",
    session_id: str = "",
    node_id: str = "",
    **kwargs,
) -> AsyncIterator[str]:
    """Stream LLM output, parsing inline emotion/action tags into SSE events.

    The LLM is instructed to embed tags like [emotion:happy] in its output.
    This function parses those tags out and emits them as separate SSE events,
    passing through clean text chunks.

    Args:
        provider: The LLM provider to use.
        prompt: User-facing prompt.
        system_prompt: System instruction.
        character_id: Character identifier for SSE events.
        session_id: Game session ID.
        node_id: Current node ID.

    Yields:
        SSE-formatted event strings.
    """
    buffer = ""
    pending_emotion = None

    try:
        async for token in provider.stream(prompt, system_prompt=system_prompt, **kwargs):
            buffer += token

            # Check for emotion tags
            emotion_match = SSEFormatter.EMOTION_PATTERN.search(buffer)
            if emotion_match:
                # Flush text before the tag
                before_tag = buffer[: emotion_match.start()]
                if before_tag.strip():
                    yield SSEFormatter.format_text(before_tag, character_id)

                # Emit emotion event
                emotion = emotion_match.group(1).lower()
                if emotion != pending_emotion:
                    pending_emotion = emotion
                    yield SSEFormatter.format_emotion(emotion, character_id)

                # Remove tag from buffer
                buffer = buffer[emotion_match.end() :]
                continue

            # Flush complete sentences (on sentence-ending punctuation)
            if any(buffer.endswith(p) for p in ["。", "！", "？", ".", "!", "?", "…", "\n"]):
                if buffer.strip():
                    yield SSEFormatter.format_text(buffer, character_id)
                buffer = ""

        # Flush remaining buffer
        if buffer.strip():
            # Strip any trailing emotion tags
            clean = SSEFormatter.EMOTION_PATTERN.sub("", buffer).strip()
            if clean:
                yield SSEFormatter.format_text(clean, character_id)

    except Exception as e:
        yield SSEFormatter.format_error("LLM_GENERATION_FAILED", str(e))

    # Emit done event
    yield SSEFormatter.format_done(session_id, node_id)


async def fallback_dialogue(character_id: str = "") -> str:
    """Generate a safe fallback response when LLM fails.

    Returns SSE-formatted fallback text.
    """
    fallback_text = "……我好像有些走神了，能再说一遍吗？"
    return SSEFormatter.format_text(fallback_text, character_id)
