"""LLM provider registry."""

import os
from .base import BaseLLMProvider, DialogueContext, Memory
from .openai_provider import OpenAIProvider
from .mock_provider import MockProvider


def get_provider() -> BaseLLMProvider:
    """获取当前配置的 LLM provider
    
    根据环境变量 LLM_PROVIDER 或 OPENAI_API_KEY 决定使用哪个 provider：
    - 如果 LLM_PROVIDER=mock 或没有 OPENAI_API_KEY，返回 MockProvider
    - 否则返回 OpenAIProvider
    
    Returns:
        BaseLLMProvider 实例
    """
    provider_type = os.getenv("LLM_PROVIDER", "").lower()
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    if provider_type == "mock" or not api_key:
        return MockProvider()
    else:
        return OpenAIProvider()


__all__ = [
    "BaseLLMProvider",
    "DialogueContext",
    "Memory",
    "OpenAIProvider",
    "MockProvider",
    "get_provider",
]
