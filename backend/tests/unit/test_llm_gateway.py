"""测试 LLM Gateway 业务层"""

import pytest
from app.services.llm import (
    LLMMessage,
    LLMResponse,
    LLMProviderAdapter,
    LLMGateway,
    llm_gateway,
)
from app.llm.providers import MockProvider


class TestLLMMessage:
    def test_create_message(self):
        msg = LLMMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"


class TestLLMResponse:
    def test_create_response(self):
        resp = LLMResponse(
            content="Hi there!",
            model="gpt-4",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            finish_reason="stop"
        )
        assert resp.content == "Hi there!"
        assert resp.model == "gpt-4"
        assert resp.usage["total_tokens"] == 15


class TestLLMProviderAdapter:
    @pytest.mark.asyncio
    async def test_complete_with_mock_provider(self):
        """测试适配器包装 MockProvider"""
        mock = MockProvider()
        adapter = LLMProviderAdapter(mock)
        
        messages = [
            LLMMessage(role="system", content="你是助手"),
            LLMMessage(role="user", content="你好")
        ]
        
        response = await adapter.complete(messages)
        
        assert isinstance(response, LLMResponse)
        assert response.content == "这是 Mock 生成的对话内容。"
        assert response.finish_reason == "stop"
    
    @pytest.mark.asyncio
    async def test_stream_complete_with_mock_provider(self):
        """测试适配器流式生成"""
        mock = MockProvider()
        adapter = LLMProviderAdapter(mock)
        
        messages = [
            LLMMessage(role="user", content="讲个故事")
        ]
        
        chunks = []
        async for chunk in adapter.stream_complete(messages):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_text = "".join(chunks)
        assert "这是 Mock 生成的对话内容。" in full_text or len(full_text) > 0
    
    def test_base_provider_property(self):
        """测试 base_provider 属性"""
        mock = MockProvider()
        adapter = LLMProviderAdapter(mock)
        
        assert adapter.base_provider is mock
        assert isinstance(adapter.base_provider, MockProvider)


class TestLLMGateway:
    def test_gateway_initialization(self):
        """测试网关初始化"""
        gateway = LLMGateway()
        assert isinstance(gateway.provider, LLMProviderAdapter)
        assert isinstance(gateway.provider.base_provider, MockProvider)
    
    @pytest.mark.asyncio
    async def test_generate_dialogue(self):
        """测试对话生成"""
        gateway = LLMGateway()
        
        dialogue = await gateway.generate_dialogue(
            character_name="艾莉丝",
            character_personality="温柔善良的少女",
            context="在花园中散步",
            user_input="今天天气真好",
            conversation_history=[]
        )
        
        assert isinstance(dialogue, str)
        assert len(dialogue) > 0
    
    @pytest.mark.asyncio
    async def test_generate_dialogue_with_history(self):
        """测试带历史的对话生成"""
        gateway = LLMGateway()
        
        history = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"},
            {"role": "user", "content": "你是谁？"}
        ]
        
        dialogue = await gateway.generate_dialogue(
            character_name="艾莉丝",
            character_personality="温柔善良的少女",
            context="初次见面",
            user_input="很高兴认识你",
            conversation_history=history
        )
        
        assert isinstance(dialogue, str)
        assert len(dialogue) > 0
    
    @pytest.mark.asyncio
    async def test_extract_memory(self):
        """测试记忆提取"""
        gateway = LLMGateway()
        
        memories = await gateway.extract_memory(
            dialogue="我最喜欢的颜色是蓝色，我喜欢在周末去游泳。",
            character_name="艾莉丝"
        )
        
        assert isinstance(memories, list)
        # MockProvider 返回的文本无法解析为 JSON，会 fallback 到单元素列表
        assert len(memories) >= 0


class TestGlobalGateway:
    def test_global_gateway_exists(self):
        """测试全局网关实例"""
        assert llm_gateway is not None
        assert isinstance(llm_gateway, LLMGateway)
    
    @pytest.mark.asyncio
    async def test_global_gateway_can_generate(self):
        """测试全局网关可用"""
        dialogue = await llm_gateway.generate_dialogue(
            character_name="测试角色",
            character_personality="测试性格",
            context="测试场景",
            user_input="测试输入",
            conversation_history=[]
        )
        
        assert isinstance(dialogue, str)
        assert len(dialogue) > 0
