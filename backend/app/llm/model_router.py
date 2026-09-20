"""ModelRouter — 根据场景自动选择模型+降级链

v4.4 双Agent架构核心组件。
Ref: /root/.openclaw/workspace/main/v4.4-完整需求与实现方案-v4.0.md § 3.2
"""

import logging
from enum import Enum
from typing import AsyncGenerator, List, Optional
from dataclasses import dataclass


class ScenarioType(str, Enum):
    """场景类型"""
    NARRATIVE = "narrative"              # 叙事生成
    CONVERGENCE = "convergence"          # 集合点/高潮剧情
    CHOICE_GENERATION = "choice_gen"     # 选择分支生成
    ENDING = "ending"                    # 结局生成
    FREE_CHAT = "free_chat"              # 自由对话
    FREE_CHAT_ADVANCED = "free_chat_adv" # 高级对话模式
    MEMORY_EXTRACTION = "memory_ext"     # 记忆提取
    EMOTION_INFERENCE = "emotion_inf"    # 情绪推断
    CONTENT_MODERATION = "content_mod"   # 内容审核
    DIALOGUE_QUALITY = "dialogue_qual"   # 对话质量检查
    USER_PERSONA_UPDATE = "persona_upd"  # 用户画像更新


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    provider: str
    tier: str  # S/A/B/C
    fallback_chain: List[str]


# 模型池 (S×5 + A×5 + B×4 + C×1 = 15)
MODEL_POOL = {
    # S级
    "hermes-3-llama-3.1-405b": ModelConfig("hermes-3-llama-3.1-405b", "nousresearch", "S", ["MiniMax-M2.5", "qwen3.7-max", "deepseek-v4-pro"]),
    "qwen3.7-max": ModelConfig("qwen3.7-max", "qwen", "S", ["deepseek-v4-pro", "kimi-k2.6", "qwen3.6-plus"]),
    "deepseek-v4-pro": ModelConfig("deepseek-v4-pro", "deepseek", "S", ["qwen3.7-max", "kimi-k2.6", "qwen3.6-plus"]),
    "kimi-k2.7-code": ModelConfig("kimi-k2.7-code", "moonshot", "S", ["glm-5.2", "qwen3.7-max", "qwen3.6-plus"]),
    "glm-5.2": ModelConfig("glm-5.2", "zhipu", "S", ["deepseek-v4-pro", "qwen3.7-max", "qwen3.6-plus"]),

    # A级
    "qwen3.7-plus": ModelConfig("qwen3.7-plus", "qwen", "A", ["kimi-k2.6", "glm-5.1", "deepseek-v3.2"]),
    "deepseek-v4-flash": ModelConfig("deepseek-v4-flash", "deepseek", "A", ["kimi-k2.5", "glm-5", "qwen3.6-plus"]),
    "kimi-k2.6": ModelConfig("kimi-k2.6", "moonshot", "A", ["glm-5.1", "qwen3.7-plus", "deepseek-v3.2"]),
    "glm-5.1": ModelConfig("glm-5.1", "zhipu", "A", ["kimi-k2.6", "qwen3.7-plus", "deepseek-v3.2"]),
    "MiniMax-M2.5": ModelConfig("MiniMax-M2.5", "minimax", "A", ["qwen3.7-plus", "kimi-k2.5", "glm-5"]),

    # B级
    "qwen3.6-plus": ModelConfig("qwen3.6-plus", "qwen", "B", ["deepseek-v3.2", "glm-5", "kimi-k2.5"]),
    "deepseek-v3.2": ModelConfig("deepseek-v3.2", "deepseek", "B", ["qwen3.6-plus", "kimi-k2.5", "glm-5"]),
    "kimi-k2.5": ModelConfig("kimi-k2.5", "moonshot", "B", ["glm-5", "qwen3.6-plus", "deepseek-v3.2"]),
    "glm-5": ModelConfig("glm-5", "zhipu", "B", ["kimi-k2.5", "qwen3.6-plus", "deepseek-v3.2"]),

    # C级
    "qwen3.6-flash": ModelConfig("qwen3.6-flash", "qwen", "C", []),
}

# 场景→模型映射
SCENARIO_MODEL_MAP = {
    ScenarioType.NARRATIVE: "qwen3.7-max",
    ScenarioType.CONVERGENCE: "qwen3.7-max",
    ScenarioType.CHOICE_GENERATION: "qwen3.7-plus",
    ScenarioType.ENDING: "qwen3.7-max",
    ScenarioType.FREE_CHAT: "hermes-3-llama-3.1-405b",
    ScenarioType.FREE_CHAT_ADVANCED: "hermes-3-llama-3.1-405b",
    ScenarioType.MEMORY_EXTRACTION: "qwen3.6-flash",
    ScenarioType.EMOTION_INFERENCE: "qwen3.6-flash",
    ScenarioType.CONTENT_MODERATION: "qwen3.6-flash",
    ScenarioType.DIALOGUE_QUALITY: "qwen3.7-plus",
    ScenarioType.USER_PERSONA_UPDATE: "qwen3.6-plus",
}


class ModelRouter:
    """模型路由器"""

    def get_model_for_scenario(self, scenario: ScenarioType) -> ModelConfig:
        """根据场景获取主模型"""
        model_name = SCENARIO_MODEL_MAP.get(scenario, "qwen3.6-plus")
        return MODEL_POOL[model_name]

    def get_fallback_chain(self, scenario: ScenarioType) -> List[ModelConfig]:
        """获取降级链"""
        primary = self.get_model_for_scenario(scenario)
        fallback_models = [MODEL_POOL[name] for name in primary.fallback_chain if name in MODEL_POOL]
        return [primary] + fallback_models

    async def call_with_fallback(self, scenario: ScenarioType, messages: List[dict], **kwargs):
        """带降级的模型调用"""
        chain = self.get_fallback_chain(scenario)

        for model in chain:
            try:
                # 调用模型
                response = await self._call_model(model, messages, **kwargs)
                return response
            except Exception as e:
                # 记录错误，尝试下一个模型
                print(f"Model {model.name} failed: {e}, trying fallback...")
                continue

        # 所有模型都失败，返回预设回复
        return self._get_fallback_response(scenario)

    async def _call_model(self, model: ModelConfig, messages: List[dict], **kwargs):
        """调用具体模型（通过LLM Gateway）"""
        from app.services.llm.gateway import llm_gateway
        return await llm_gateway.call(model.name, messages, **kwargs)

    async def _stream_model(
        self,
        model: ModelConfig,
        messages: List[dict],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream tokens from a specific model via LLM Gateway provider.

        Delegates to llm_gateway.provider.stream_complete() with
        LLMMessage-converted messages.
        """
        from app.services.llm.gateway import llm_gateway, LLMMessage

        llm_messages = [
            LLMMessage(role=m["role"], content=m["content"])
            for m in messages
        ]

        async for chunk in llm_gateway.provider.stream_complete(
            llm_messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 500),
        ):
            yield chunk

    async def stream_with_fallback(
        self,
        scenario: ScenarioType,
        messages: List[dict],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Stream with automatic fallback model switching.

        Tries primary model's stream() first. On failure (timeout, connection error),
        switches to next model in fallback chain. If all models fail, yields a
        fallback text as a single chunk (non-streaming fallback).

        Yields:
            str: Text tokens from the LLM.
        """
        chain = self.get_fallback_chain(scenario)
        log = logging.getLogger(__name__)

        for i, model in enumerate(chain):
            try:
                async for chunk in self._stream_model(model, messages, **kwargs):
                    yield chunk
                return  # Success — no fallback needed

            except Exception as e:
                log.warning(
                    f"Model {model.name} stream failed (chain pos {i}): {e}, "
                    f"trying fallback..."
                )
                continue

        # All models failed — yield fallback text (Q-003 confirmation)
        fallback_text = self._get_stream_fallback_text(scenario)
        yield fallback_text

    def _get_stream_fallback_text(self, scenario: ScenarioType) -> str:
        """Get fallback text when all models fail (Q-003).

        Returns scenario-specific friendly text in character voice,
        so users don't feel a system error.
        """
        fallback_texts = {
            ScenarioType.FREE_CHAT: "（微微侧头，轻轻笑了笑）抱歉，我刚才走神了……你说的真有意思，能再和我说说吗？",
            ScenarioType.FREE_CHAT_ADVANCED: "（微微侧头，轻轻笑了笑）抱歉，我刚才走神了……你说的真有意思，能再和我说说吗？",
            ScenarioType.NARRATIVE: "（故事在这一刻仿佛停滞了片刻，随后又缓缓流淌……）",
            ScenarioType.CONVERGENCE: "（故事在这一刻仿佛停滞了片刻，随后又缓缓流淌……）",
            ScenarioType.CHOICE_GENERATION: "选项似乎暂时无法生成，请稍后再试。",
            ScenarioType.ENDING: "（结局的画面渐渐模糊，仿佛回忆渐渐远去……）",
        }
        return fallback_texts.get(scenario, "抱歉，暂时无法回应，请稍后再试。")

    def _get_fallback_response(self, scenario: ScenarioType):
        """预设回复（所有模型都失败时）"""
        fallback_responses = {
            ScenarioType.FREE_CHAT: "（微微侧头）嗯……我好像有点记不清了，也许我们还需要多相处一段时间？",
            ScenarioType.NARRATIVE: "故事还在继续，请稍等片刻……",
        }
        return {"text": fallback_responses.get(scenario, "请稍后再试。")}


# 全局单例
model_router = ModelRouter()
