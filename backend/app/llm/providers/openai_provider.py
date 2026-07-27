"""OpenAI LLM provider (GPT-4o-mini + text-embedding-3-small)."""

import logging
from typing import AsyncIterator, List, Optional
from openai import AsyncOpenAI
from app.core.config import settings
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """Provider for OpenAI API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self.client = AsyncOpenAI(
            api_key=api_key or settings.llm_api_key,
            base_url=base_url or settings.llm_base_url,
        )
        self.model = model or settings.llm_model
        self.embedding_model = "text-embedding-3-small"

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a single completion via OpenAI Chat Completions."""
        temperature = kwargs.get("temperature", 0.8)
        max_tokens = kwargs.get("max_tokens", 1024)
        system_prompt = kwargs.get("system_prompt", "You are a helpful assistant.")

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    async def stream(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream tokens via OpenAI streaming API."""
        temperature = kwargs.get("temperature", 0.8)
        max_tokens = kwargs.get("max_tokens", 1024)
        system_prompt = kwargs.get("system_prompt", "You are a helpful assistant.")

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise

    async def embed(self, text: str) -> List[float]:
        """Generate embedding via text-embedding-3-small."""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise

    async def close(self) -> None:
        """Close the OpenAI client."""
        await self.client.close()
