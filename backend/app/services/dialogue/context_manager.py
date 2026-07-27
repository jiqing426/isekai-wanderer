"""Multi-turn dialogue context manager.

Manages conversation history with token-aware trimming, memory injection,
and emotion-based style adjustments for character consistency.
"""

import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available, using character-based token estimation")

logger = logging.getLogger(__name__)


@dataclass
class DialogueMessage:
    """Single message in dialogue history."""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Optional: emotion state when this message was generated
    emotion: Optional[str] = None
    # Optional: memory references used for this message
    memory_refs: List[str] = field(default_factory=list)


class DialogueContextManager:
    """Manages multi-turn dialogue context with intelligent trimming and memory injection.

    Features:
    - Token-aware context window management (max_tokens limit)
    - Priority-based message trimming (recent > old, user > system)
    - Character memory injection for context continuity
    - Emotion state tracking and style adjustment
    """

    def __init__(
        self,
        max_tokens: int = 2048,
        model: str = "gpt-4",
        reserve_tokens: int = 300,  # Reserve for response
    ):
        """Initialize context manager.

        Args:
            max_tokens: Maximum token budget for context window.
            model: Model name for tokenizer selection.
            reserve_tokens: Tokens reserved for model response.
        """
        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens
        self.effective_tokens = max_tokens - reserve_tokens
        self.model = model

        # Initialize tokenizer
        if TIKTOKEN_AVAILABLE:
            try:
                self.encoding = tiktoken.encoding_for_model(model)
            except Exception:
                self.encoding = tiktoken.get_encoding("cl100k_base")
        else:
            self.encoding = None

        # Message history
        self.messages: List[DialogueMessage] = []

        # Current emotion state (for style adjustment)
        self.current_emotion: Optional[str] = None

        # Injected memories (for tracking what's been added)
        self.injected_memories: List[str] = []

    def add_message(
        self,
        role: str,
        content: str,
        emotion: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a message to dialogue history.

        Args:
            role: Message role ("system", "user", "assistant").
            content: Message content.
            emotion: Optional emotion state for this message.
            metadata: Optional metadata dict.
        """
        message = DialogueMessage(
            role=role,
            content=content,
            emotion=emotion or self.current_emotion,
            metadata=metadata or {},
        )
        self.messages.append(message)

        # Update current emotion if provided
        if emotion:
            self.current_emotion = emotion

    def get_context(
        self,
        memories: Optional[List[str]] = None,
        inject_memories: bool = True,
    ) -> List[Dict[str, str]]:
        """Get trimmed context window for LLM generation.

        Args:
            memories: Optional list of memory strings to inject.
            inject_memories: Whether to inject memories (default True).

        Returns:
            List of message dicts in OpenAI format: [{"role": "...", "content": "..."}]
        """
        # Build context with optional memory injection
        context_messages = []

        # 1. Inject memories as system message (if enabled)
        if inject_memories and memories:
            memory_text = self._format_memories(memories)
            context_messages.append({
                "role": "system",
                "content": f"[Character Memories]\n{memory_text}",
            })
            self.injected_memories = memories

        # 2. Add dialogue history (with trimming)
        trimmed_history = self._trim_messages(self.effective_tokens)
        for msg in trimmed_history:
            context_messages.append({
                "role": msg.role,
                "content": msg.content,
            })

        return context_messages

    def get_context_with_style(
        self,
        memories: Optional[List[str]] = None,
        base_style: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Get context with emotion-based style adjustment.

        Args:
            memories: Optional memories to inject.
            base_style: Base character style description.

        Returns:
            List of message dicts with style-adjusted system prompt.
        """
        context = []

        # 1. Build system prompt with emotion-aware style
        style_prompt = self._build_style_prompt(base_style)
        if style_prompt:
            context.append({
                "role": "system",
                "content": style_prompt,
            })

        # 2. Inject memories
        if memories:
            memory_text = self._format_memories(memories)
            context.append({
                "role": "system",
                "content": f"[Character Memories]\n{memory_text}",
            })

        # 3. Add trimmed history
        trimmed_history = self._trim_messages(
            self.effective_tokens - self._count_tokens(style_prompt or "")
        )
        for msg in trimmed_history:
            context.append({
                "role": msg.role,
                "content": msg.content,
            })

        return context

    def clear(self) -> None:
        """Clear all dialogue history."""
        self.messages.clear()
        self.current_emotion = None
        self.injected_memories.clear()

    def set_emotion(self, emotion: str) -> None:
        """Set current emotion state.

        Args:
            emotion: Emotion label (e.g., "happy", "sad", "angry", "neutral").
        """
        self.current_emotion = emotion

    def get_stats(self) -> Dict[str, Any]:
        """Get context statistics.

        Returns:
            Dict with message count, token count, emotion, etc.
        """
        total_tokens = sum(self._count_tokens(msg.content) for msg in self.messages)
        return {
            "message_count": len(self.messages),
            "total_tokens": total_tokens,
            "max_tokens": self.max_tokens,
            "effective_tokens": self.effective_tokens,
            "current_emotion": self.current_emotion,
            "injected_memories": len(self.injected_memories),
        }

    def _trim_messages(self, target_tokens: int) -> List[DialogueMessage]:
        """Trim messages to fit within token budget.

        Strategy:
        - Keep system messages (high priority)
        - Keep recent messages (reverse chronological)
        - Drop old user/assistant messages first

        Args:
            target_tokens: Target token budget.

        Returns:
            Trimmed list of messages.
        """
        if not self.messages:
            return []

        # Calculate tokens for each message
        message_tokens = [
            (msg, self._count_tokens(msg.content))
            for msg in self.messages
        ]

        total_tokens = sum(tokens for _, tokens in message_tokens)

        # If under budget, return all
        if total_tokens <= target_tokens:
            return self.messages

        # Separate system messages (always keep)
        system_msgs = [(msg, tokens) for msg, tokens in message_tokens if msg.role == "system"]
        other_msgs = [(msg, tokens) for msg, tokens in message_tokens if msg.role != "system"]

        # Keep system messages
        kept_tokens = sum(tokens for _, tokens in system_msgs)
        kept_messages = [msg for msg, _ in system_msgs]

        # Add recent messages (reverse order) until budget exhausted
        remaining_budget = target_tokens - kept_tokens
        for msg, tokens in reversed(other_msgs):
            if remaining_budget >= tokens:
                kept_messages.insert(len(system_msgs), msg)  # Insert after system
                remaining_budget -= tokens
            else:
                logger.info(
                    f"Trimming old message (tokens={tokens}, budget={remaining_budget})"
                )
                break

        return kept_messages

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: Input text.

        Returns:
            Token count.
        """
        if not text:
            return 0

        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Fallback: estimate ~4 characters per token
            return len(text) // 4

    def _format_memories(self, memories: List[str]) -> str:
        """Format memories for injection.

        Args:
            memories: List of memory strings.

        Returns:
            Formatted memory text.
        """
        if not memories:
            return ""

        formatted = []
        for i, memory in enumerate(memories, 1):
            formatted.append(f"{i}. {memory}")

        return "\n".join(formatted)

    def _build_style_prompt(self, base_style: Optional[str] = None) -> Optional[str]:
        """Build style prompt with emotion adjustment.

        Args:
            base_style: Base character style description.

        Returns:
            Style prompt string or None if no emotion/style.
        """
        if not self.current_emotion and not base_style:
            return None

        parts = []

        if base_style:
            parts.append(f"Base character style: {base_style}")

        if self.current_emotion:
            emotion_styles = {
                "happy": "Respond with warmth and enthusiasm. Use upbeat language.",
                "sad": "Respond with melancholy and introspection. Use softer, slower language.",
                "angry": "Respond with intensity and sharpness. Use direct, forceful language.",
                "fearful": "Respond with caution and anxiety. Use hesitant, uncertain language.",
                "surprised": "Respond with wonder and curiosity. Use exclamatory language.",
                "neutral": "Respond with calm neutrality. Use balanced, measured language.",
            }
            emotion_style = emotion_styles.get(self.current_emotion, "")
            if emotion_style:
                parts.append(f"Current emotion ({self.current_emotion}): {emotion_style}")

        return "\n".join(parts) if parts else None

    def __len__(self) -> int:
        """Return number of messages in history."""
        return len(self.messages)

    def __repr__(self) -> str:
        """String representation."""
        stats = self.get_stats()
        return (
            f"DialogueContextManager(messages={stats['message_count']}, "
            f"tokens={stats['total_tokens']}/{stats['max_tokens']}, "
            f"emotion={stats['current_emotion']})"
        )
