"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Optional
from pydantic import BaseModel


class DialogueContext(BaseModel):
    """Context passed to LLM for dialogue generation."""
    user_message: str
    character_name: str
    character_persona: str
    conversation_history: List[str] = []
    memory_context: List[str] = []
    emotion_state: str = "neutral"
    scene_description: str = ""
    style_hint: str = ""


class Memory(BaseModel):
    """Extracted memory from conversation."""
    content: str
    importance: float = 0.5
    category: str = "general"


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a single completion.

        Args:
            prompt: Full prompt string.
            **kwargs: Optional parameters (temperature, max_tokens, etc.).

        Returns:
            Generated text.
        """
        ...

    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream tokens as they are generated.

        Args:
            prompt: Full prompt string.
            **kwargs: Optional parameters.

        Yields:
            Token chunks.
        """
        ...

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embedding vector for text.

        Args:
            text: Text to embed.

        Returns:
            1536-dimensional embedding vector.
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Clean up resources."""
        ...
