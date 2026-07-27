"""业务层 LLM 服务模块

提供对话生成、记忆提取等业务编排能力，内部调用 app/llm/ 层的 Provider 实现。

架构：
    narrative_engine / memory_service
        ↓ import llm_gateway
    LLMGateway (业务编排)
        ↓ 内部使用
    LLMProviderAdapter (适配器)
        ↓ 包装
    app.llm.providers.MockProvider / OpenAIProvider (底层实现)

导出：
    LLMMessage: 消息格式
    LLMResponse: 响应格式
    LLMProviderAdapter: Provider 适配器（包装 app.llm.providers）
    LLMGateway: 业务层 LLM 网关
    llm_gateway: 全局网关实例
"""

from dataclasses import dataclass
from typing import Any, AsyncGenerator
from app.llm.providers import (
    BaseLLMProvider,
    MockProvider,
    OpenAIProvider,
    get_provider,
)


@dataclass
class LLMMessage:
    """业务层消息格式"""
    role: str
    content: str


@dataclass
class LLMResponse:
    """业务层响应格式"""
    content: str
    model: str
    usage: dict[str, int]
    finish_reason: str


class LLMProviderAdapter:
    """Provider 适配器
    
    包装 app.llm.providers.BaseLLMProvider，暴露业务层需要的 complete/stream_complete 接口。
    内部调用底层 Provider 的 generate/stream 方法。
    """
    
    def __init__(self, provider: BaseLLMProvider):
        self._provider = provider
    
    @property
    def base_provider(self) -> BaseLLMProvider:
        """获取底层 Provider 实例"""
        return self._provider
    
    async def complete(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ) -> LLMResponse:
        """调用 LLM 生成完整响应（业务层接口）
        
        将消息列表转换为 prompt 字符串，调用底层 generate() 方法。
        """
        # 构建 prompt
        system_msgs = [m.content for m in messages if m.role == "system"]
        user_msgs = [m.content for m in messages if m.role == "user"]
        
        prompt_parts = []
        if system_msgs:
            prompt_parts.append("\n".join(system_msgs))
        if user_msgs:
            prompt_parts.append("\n".join(user_msgs))
        
        prompt = "\n\n".join(prompt_parts) if prompt_parts else "Continue the conversation."
        
        # 调用底层 generate
        content = await self._provider.generate(
            prompt,
            system_prompt=system_msgs[0] if system_msgs else None,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        
        # 返回业务层响应格式
        return LLMResponse(
            content=content,
            model=self._provider.model if hasattr(self._provider, "model") else "unknown",
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            finish_reason="stop",
        )
    
    async def stream_complete(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """流式生成响应（业务层接口）
        
        将消息列表转换为 prompt 字符串，调用底层 stream() 方法。
        """
        # 构建 prompt
        system_msgs = [m.content for m in messages if m.role == "system"]
        user_msgs = [m.content for m in messages if m.role == "user"]
        
        prompt_parts = []
        if system_msgs:
            prompt_parts.append("\n".join(system_msgs))
        if user_msgs:
            prompt_parts.append("\n".join(user_msgs))
        
        prompt = "\n\n".join(prompt_parts) if prompt_parts else "Continue the conversation."
        
        # 调用底层 stream
        async for chunk in self._provider.stream(
            prompt,
            system_prompt=system_msgs[0] if system_msgs else None,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        ):
            yield chunk
    
    async def embed(self, text: str) -> list[float]:
        """生成文本嵌入向量"""
        return await self._provider.embed(text)


class LLMGateway:
    """业务层 LLM 网关
    
    提供对话生成、记忆提取等业务编排能力。
    内部使用 LLMProviderAdapter 包装底层 Provider。
    """
    
    def __init__(self):
        self._provider = LLMProviderAdapter(get_provider())
    
    @property
    def provider(self) -> LLMProviderAdapter:
        """获取 Provider 适配器"""
        return self._provider
    
    async def generate_dialogue(
        self,
        character_name: str,
        character_personality: str,
        context: str,
        user_input: str,
        conversation_history: list[dict[str, str]],
    ) -> str:
        """生成对话（业务编排）"""
        # 构建消息列表
        messages = [
            LLMMessage(
                role="system",
                content=f"你是{character_name}，{character_personality}。{context}"
            )
        ]
        
        # 添加历史消息（最近 3 轮）
        for hist in conversation_history[-3:]:
            messages.append(LLMMessage(
                role=hist.get("role", "user"),
                content=hist.get("content", "")
            ))
        
        # 添加当前用户输入
        messages.append(LLMMessage(role="user", content=user_input))
        
        # 调用 Provider
        response = await self._provider.complete(messages)
        return response.content
    
    async def extract_memory(self, dialogue: str, character_name: str) -> list[str]:
        """提取记忆（业务编排）"""
        messages = [
            LLMMessage(
                role="system",
                content="从对话中提取关键事实、情感、事件，返回 JSON 字符串数组。"
            ),
            LLMMessage(
                role="user",
                content=f"角色：{character_name}\n对话：\n{dialogue}"
            ),
        ]
        
        response = await self._provider.complete(messages, temperature=0.3)
        
        # 解析 JSON
        import json
        try:
            return json.loads(response.content)
        except:
            return [response.content] if response.content else []


# 全局网关实例
llm_gateway = LLMGateway()


__all__ = [
    "LLMMessage",
    "LLMResponse",
    "LLMProviderAdapter",
    "LLMGateway",
    "llm_gateway",
]
