"""Mock LLM provider for testing (no real API calls)."""

import asyncio
from typing import AsyncIterator, List, Optional, Dict, Any
from dataclasses import dataclass
from .base import BaseLLMProvider


@dataclass
class MockLLMResponse:
    """Mock response matching LLMResponse interface."""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class MockProvider(BaseLLMProvider):
    """Deterministic mock provider for unit tests.

    Returns canned responses; does NOT call any external API.
    Suitable for development/component tests only.
    """

    def __init__(self):
        self.generate_calls: List[dict] = []
        self.stream_calls: List[dict] = []
        self.embed_calls: List[str] = []
        self.mock_response = "这是 Mock 生成的对话内容。"
        self.mock_embedding = [0.01] * 1536

    async def generate(self, prompt: str, **kwargs) -> str:
        """Return mock response."""
        self.generate_calls.append({"prompt": prompt, "kwargs": kwargs})
        return self.mock_response

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Yield mock tokens."""
        self.stream_calls.append({"prompt": prompt, "kwargs": kwargs})
        for char in self.mock_response:
            await asyncio.sleep(0.01)
            yield char

    async def embed(self, text: str) -> List[float]:
        """Return mock embedding."""
        self.embed_calls.append(text)
        return self.mock_embedding

    async def close(self) -> None:
        """No-op cleanup."""
        pass

    def set_mock_response(self, response: str) -> None:
        """Configure mock response for testing."""
        self.mock_response = response

    async def complete(
        self,
        messages: List[Any],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
    ) -> "LLMResponse":
        """Business-layer interface: message-based completion."""
        from app.services.llm.gateway import LLMResponse
        
        user_msg = messages[-1].content if messages else ""
        mock_response = f"[Mock response to: {user_msg[:50]}...]"
        
        return LLMResponse(
            content=mock_response,
            model="mock-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop",
        )

    async def stream_complete(
        self,
        messages: List[Any],
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> AsyncIterator[str]:
        """Business-layer interface: message-based streaming."""
        user_msg = messages[-1].content if messages else ""
        mock_response = f"[Mock streaming response to: {user_msg[:50]}...]"
        
        for word in mock_response.split():
            yield word + " "
            await asyncio.sleep(0.05)
