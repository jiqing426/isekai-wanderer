"""LLM Gateway - business orchestration layer for LLM operations.

Uses providers from app/llm/providers/ for actual LLM calls.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.core.redis import check_rate_limit
from app.llm.providers.base import BaseLLMProvider
from app.llm.providers.openai_provider import OpenAIProvider as _OpenAIProvider
from app.llm.providers.mock_provider import MockProvider as _MockProvider
from app.llm.providers.thoushub_provider import ThoushubProvider as _ThoushubProvider
from app.llm.model_router import ModelRouter, MODEL_POOL

# Re-export for backward compat (tests, narrative services)
OpenAIProvider = _OpenAIProvider
MockProvider = _MockProvider
ThoushubProvider = _ThoushubProvider


@dataclass
class LLMMessage:
    """Single message in a conversation."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class LLMProvider:
    """Wrapper that adapts app/llm/providers to messages-based interface.
    
    Delegates generate/stream/embed/close to the underlying BaseLLMProvider.
    Adds complete()/stream_complete() for business-layer callers.
    """
    
    def __init__(self, provider: BaseLLMProvider):
        self._provider = provider
    
    @property
    def base_provider(self) -> BaseLLMProvider:
        """Access the underlying app/llm provider (for isinstance checks)."""
        return self._provider
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """Delegate to underlying provider."""
        return await self._provider.generate(prompt, **kwargs)
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Delegate to underlying provider."""
        async for chunk in self._provider.stream(prompt, **kwargs):
            yield chunk
    
    async def embed(self, text: str) -> list[float]:
        """Delegate to underlying provider."""
        return await self._provider.embed(text)
    
    async def close(self) -> None:
        """Delegate to underlying provider."""
        await self._provider.close()
    
    async def complete(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
    ) -> LLMResponse:
        """Generate completion from message list (business layer interface)."""
        # Build prompt from messages
        system_parts = []
        user_parts = []
        for m in messages:
            if m.role == "system":
                system_parts.append(m.content)
            else:
                user_parts.append(f"{m.role}: {m.content}" if m.role != "user" else m.content)
        
        prompt = "\n\n".join(user_parts) if user_parts else "Continue."
        system_prompt = "\n\n".join(system_parts) if system_parts else "You are a helpful assistant."
        
        # Delegate to provider.generate()
        raw = await self._provider.generate(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return LLMResponse(
            content=raw,
            model=getattr(self._provider, "model", "unknown"),
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            finish_reason="stop",
        )
    
    async def stream_complete(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> AsyncGenerator[str, None]:
        """Stream completion from message list (business layer interface)."""
        system_parts = []
        user_parts = []
        for m in messages:
            if m.role == "system":
                system_parts.append(m.content)
            else:
                user_parts.append(f"{m.role}: {m.content}" if m.role != "user" else m.content)
        
        prompt = "\n\n".join(user_parts) if user_parts else "Continue."
        system_prompt = "\n\n".join(system_parts) if system_parts else "You are a helpful assistant."
        
        async for chunk in self._provider.stream(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        ):
            yield chunk


class LLMGateway:
    """Gateway for LLM operations with rate limiting and provider abstraction."""
    
    def __init__(self):
        self._provider: Optional[LLMProvider] = None
        self._model_router = ModelRouter()
    
    @property
    def provider(self) -> LLMProvider:
        """Get current LLM provider adapter (lazy init).
        
        Returns an LLMProvider that wraps the app/llm base provider.
        Use provider.base_provider for isinstance checks against MockProvider/OpenAIProvider/ThoushubProvider.
        """
        if self._provider is None:
            # Use mock in test/dev, OpenAI in production
            if settings.llm_provider == "mock" or not settings.llm_api_key:
                base = MockProvider()
            elif settings.llm_provider == "thoushub":
                base = ThoushubProvider(
                    api_key=settings.llm_api_key,
                    model=settings.llm_default_model or "qwen3.7-plus",
                    base_url=settings.llm_base_url,
                )
            else:
                base = OpenAIProvider(
                    api_key=settings.llm_api_key,
                    model=settings.llm_model or "gpt-4o-mini",
                    base_url=settings.llm_base_url,
                )
            self._provider = LLMProvider(base)
        return self._provider
    
    async def call(self, model_name: str, messages: List[dict], **kwargs) -> dict:
        """Call specific model with fallback support.
        
        Args:
            model_name: Name of the model to call
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional arguments (temperature, max_tokens, etc.)
        
        Returns:
            dict with 'text' key containing the response
        """
        # Get model config from router
        model_config = MODEL_POOL.get(model_name)
        if not model_config:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Convert messages to prompt
        system_parts = []
        user_parts = []
        for m in messages:
            if m.get("role") == "system":
                system_parts.append(m.get("content", ""))
            else:
                user_parts.append(m.get("content", ""))
        
        prompt = "\n\n".join(user_parts) if user_parts else "Continue."
        system_prompt = "\n\n".join(system_parts) if system_parts else "You are a helpful assistant."
        
        # Try primary model first, then fallback chain
        models_to_try = [model_name] + model_config.fallback_chain
        
        for current_model in models_to_try:
            if current_model not in MODEL_POOL:
                continue
                
            try:
                # Create provider for this model
                if settings.llm_provider == "mock" or not settings.llm_api_key:
                    base = MockProvider()
                else:
                    base = ThoushubProvider(
                        api_key=settings.llm_api_key,
                        model=current_model,
                        base_url=settings.llm_base_url,
                    )
                
                # Generate response
                response = await base.generate(
                    prompt,
                    system_prompt=system_prompt,
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", 1000),
                )
                
                return {"text": response}
            except Exception as e:
                logger.warning(f"Model {current_model} failed: {e}, trying fallback...")
                continue
        
        # All models failed
        raise Exception(f"All models in fallback chain failed for {model_name}")
    
    async def generate_dialogue(
        self,
        character_name: str,
        character_personality: str,
        context: str,
        user_input: str,
        conversation_history: list[Dict[str, str]],
    ) -> str:
        """Generate character dialogue."""
        # Rate limit check (skip if Redis unavailable)
        try:
            allowed, remaining = await check_rate_limit(
                f"llm:dialogue:{character_name}",
                settings.llm_rate_limit,
                window_seconds=60,
            )
            if not allowed:
                raise Exception(f"Rate limit exceeded for {character_name}")
        except Exception as e:
            if "Rate limit exceeded" in str(e):
                raise
            # Redis unavailable, skip rate limiting
            pass
        
        # Build prompt
        system_prompt = f"""You are {character_name}, a character in an interactive story.
        
Personality: {character_personality}

Context: {context}

Respond in character, keeping responses natural and engaging. Stay consistent with your personality and the story context."""
        
        messages = [LLMMessage(role="system", content=system_prompt)]
        
        # Add conversation history
        for msg in conversation_history[-5:]:  # Last 5 exchanges
            messages.append(LLMMessage(role=msg["role"], content=msg["content"]))
        
        # Add current user input
        messages.append(LLMMessage(role="user", content=user_input))
        
        # Generate response with fallback to mock
        try:
            response = await self.provider.complete(messages, temperature=0.8, max_tokens=500)
            return response.content
        except Exception as e:
            logger.warning(f"LLM generation failed, falling back to mock: {e}")
            # Fallback to mock provider
            mock_provider = MockProvider()
            mock_response = await mock_provider.complete(messages, temperature=0.8, max_tokens=500)
            return mock_response.content
    
    async def stream_dialogue(
        self,
        character_name: str,
        character_personality: str,
        context: str,
        user_input: str,
        conversation_history: list[Dict[str, str]],
    ) -> AsyncGenerator[str, None]:
        """Stream character dialogue."""
        # Rate limit check (skip if Redis unavailable)
        try:
            allowed, remaining = await check_rate_limit(
                f"llm:dialogue:{character_name}",
                settings.llm_rate_limit,
                window_seconds=60,
            )
            if not allowed:
                raise Exception(f"Rate limit exceeded for {character_name}")
        except Exception as e:
            if "Rate limit exceeded" in str(e):
                raise
            pass
        
        # Build prompt
        system_prompt = f"""You are {character_name}, a character in an interactive story.
        
Personality: {character_personality}

Context: {context}

Respond in character, keeping responses natural and engaging. Stay consistent with your personality and the story context."""
        
        messages = [LLMMessage(role="system", content=system_prompt)]
        
        # Add conversation history
        for msg in conversation_history[-5:]:
            messages.append(LLMMessage(role=msg["role"], content=msg["content"]))
        
        messages.append(LLMMessage(role="user", content=user_input))
        
        # Stream response
        async for chunk in self.provider.stream_complete(messages, temperature=0.8, max_tokens=500):
            yield chunk
    
    async def generate_story_narrative(
        self,
        context: str,
        player_choice: str,
        narrative_style: str = "descriptive",
    ) -> str:
        """Generate narrative text for story progression."""
        system_prompt = f"""You are a narrative writer for an interactive story game.
        
Style: {narrative_style}

Write engaging, immersive narrative text that advances the story based on player choices."""
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=f"Context: {context}\n\nPlayer choice: {player_choice}\n\nWrite the narrative continuation:"),
        ]
        
        response = await self.provider.complete(messages, temperature=0.7, max_tokens=800)
        return response.content
    
    async def extract_memory(
        self,
        dialogue: str,
        character_name: str,
    ) -> list[str]:
        """Extract memorable facts from dialogue for long-term memory."""
        system_prompt = """You are a memory extraction system. Identify key facts, emotions, and events from dialogue that should be remembered long-term.

Return as JSON array of strings, each representing a memorable fact."""
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=f"Character: {character_name}\n\nDialogue:\n{dialogue}\n\nExtract memorable facts:"),
        ]
        
        response = await self.provider.complete(messages, temperature=0.3, max_tokens=500)
        
        # Parse JSON response
        try:
            memories = json.loads(response.content)
            return memories if isinstance(memories, list) else []
        except json.JSONDecodeError:
            return []


# Global gateway instance
llm_gateway = LLMGateway()
