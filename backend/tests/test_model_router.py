"""Unit tests for ModelRouter

验证:
1. ScenarioType 枚举覆盖 11 种场景
2. MODEL_POOL 包含 14 个模型（S级4个、A级4个、B级4个、C级1个）
3. 降级链正确：S→A→B→C→预设回复
4. call_with_fallback 正常工作
"""

import pytest
from app.llm.model_router import (
    ScenarioType,
    ModelConfig,
    MODEL_POOL,
    SCENARIO_MODEL_MAP,
    FALLBACK_RESPONSES,
    DEFAULT_FALLBACK,
    ModelRouter,
    model_router,
)


class TestScenarioType:
    """测试 ScenarioType 枚举"""

    def test_scenario_count(self):
        """验证 11 种场景"""
        scenarios = list(ScenarioType)
        assert len(scenarios) == 11

    def test_scenario_values(self):
        """验证场景值"""
        assert ScenarioType.NARRATIVE.value == "narrative"
        assert ScenarioType.CONVERGENCE.value == "convergence"
        assert ScenarioType.CHOICE_GENERATION.value == "choice_gen"
        assert ScenarioType.ENDING.value == "ending"
        assert ScenarioType.FREE_CHAT.value == "free_chat"
        assert ScenarioType.FREE_CHAT_ADVANCED.value == "free_chat_adv"
        assert ScenarioType.MEMORY_EXTRACTION.value == "memory_ext"
        assert ScenarioType.EMOTION_INFERENCE.value == "emotion_inf"
        assert ScenarioType.CONTENT_MODERATION.value == "content_mod"
        assert ScenarioType.DIALOGUE_QUALITY.value == "dialogue_qual"
        assert ScenarioType.USER_PERSONA_UPDATE.value == "persona_upd"


class TestModelPool:
    """测试 MODEL_POOL"""

    def test_model_count(self):
        """验证 14 个模型"""
        assert len(MODEL_POOL) == 14

    def test_tier_distribution(self):
        """验证 S/A/B/C 四级分布"""
        tiers = {}
        for name, cfg in MODEL_POOL.items():
            tiers.setdefault(cfg.tier, []).append(name)

        assert len(tiers["S"]) == 4  # S级4个
        assert len(tiers["A"]) == 4  # A级4个
        assert len(tiers["B"]) == 4  # B级4个
        assert len(tiers["C"]) == 1  # C级1个

    def test_s_tier_models(self):
        """验证 S 级模型"""
        s_models = ["qwen3.7-max", "deepseek-v4-pro", "kimi-k2.7-code", "glm-5.2"]
        for name in s_models:
            assert name in MODEL_POOL
            assert MODEL_POOL[name].tier == "S"

    def test_a_tier_models(self):
        """验证 A 级模型"""
        a_models = ["qwen3.7-plus", "deepseek-v4-flash", "kimi-k2.6", "glm-5.1"]
        for name in a_models:
            assert name in MODEL_POOL
            assert MODEL_POOL[name].tier == "A"

    def test_b_tier_models(self):
        """验证 B 级模型"""
        b_models = ["qwen3.6-plus", "deepseek-v3.2", "kimi-k2.5", "glm-5"]
        for name in b_models:
            assert name in MODEL_POOL
            assert MODEL_POOL[name].tier == "B"

    def test_c_tier_models(self):
        """验证 C 级模型"""
        assert "qwen3.6-flash" in MODEL_POOL
        assert MODEL_POOL["qwen3.6-flash"].tier == "C"
        assert MODEL_POOL["qwen3.6-flash"].fallback_chain == []  # C级无后续降级

    def test_all_models_have_fallback_chain(self):
        """验证所有模型都有 fallback_chain 字段"""
        for name, cfg in MODEL_POOL.items():
            assert hasattr(cfg, "fallback_chain")
            assert isinstance(cfg.fallback_chain, list)

    def test_fallback_chain_references_valid_models(self):
        """验证 fallback_chain 引用的模型都存在于 MODEL_POOL"""
        for name, cfg in MODEL_POOL.items():
            for fallback_name in cfg.fallback_chain:
                assert fallback_name in MODEL_POOL, (
                    f"Model {name} references non-existent fallback: {fallback_name}"
                )


class TestScenarioModelMap:
    """测试场景→模型映射"""

    def test_all_scenarios_mapped(self):
        """验证所有场景都有映射"""
        for scenario in ScenarioType:
            assert scenario in SCENARIO_MODEL_MAP

    def test_mapped_models_exist(self):
        """验证映射的模型都存在于 MODEL_POOL"""
        for scenario, model_name in SCENARIO_MODEL_MAP.items():
            assert model_name in MODEL_POOL, (
                f"Scenario {scenario} maps to non-existent model: {model_name}"
            )


class TestModelRouter:
    """测试 ModelRouter 类"""

    def test_singleton_exists(self):
        """验证全局单例存在"""
        assert model_router is not None
        assert isinstance(model_router, ModelRouter)

    def test_get_model_for_scenario(self):
        """测试根据场景获取主模型"""
        # NARRATIVE → qwen3.7-max (S级)
        model = model_router.get_model_for_scenario(ScenarioType.NARRATIVE)
        assert model.name == "qwen3.7-max"
        assert model.tier == "S"

        # FREE_CHAT → deepseek-v4-flash (A级)
        model = model_router.get_model_for_scenario(ScenarioType.FREE_CHAT)
        assert model.name == "deepseek-v4-flash"
        assert model.tier == "A"

        # MEMORY_EXTRACTION → qwen3.6-flash (C级)
        model = model_router.get_model_for_scenario(ScenarioType.MEMORY_EXTRACTION)
        assert model.name == "qwen3.6-flash"
        assert model.tier == "C"

    def test_get_fallback_chain(self):
        """测试降级链"""
        # NARRATIVE: S级 → 降级链
        chain = model_router.get_fallback_chain(ScenarioType.NARRATIVE)
        assert len(chain) >= 1
        assert chain[0].name == "qwen3.7-max"  # 主模型
        assert chain[0].tier == "S"

        # 验证降级链中的模型都存在
        for model in chain:
            assert model.name in MODEL_POOL

    def test_fallback_chain_order(self):
        """测试降级链顺序正确"""
        chain = model_router.get_fallback_chain(ScenarioType.NARRATIVE)
        # 主模型 qwen3.7-max 的 fallback_chain: ["deepseek-v4-pro", "kimi-k2.6", "qwen3.6-plus"]
        assert len(chain) == 4
        assert chain[0].name == "qwen3.7-max"
        assert chain[1].name == "deepseek-v4-pro"
        assert chain[2].name == "kimi-k2.6"
        assert chain[3].name == "qwen3.6-plus"

    def test_get_fallback_response(self):
        """测试预设回复"""
        # NARRATIVE 有预设回复
        response = model_router._get_fallback_response(ScenarioType.NARRATIVE)
        assert "text" in response
        assert "model" in response
        assert response["model"] == "fallback"
        assert response["tier"] == "preset"
        assert response["text"] == "故事还在继续，请稍等片刻……"

        # FREE_CHAT 有预设回复
        response = model_router._get_fallback_response(ScenarioType.FREE_CHAT)
        assert "微微侧头" in response["text"]

        # 未定义的场景返回默认回复
        # (这里用 ScenarioType.USER_PERSONA_UPDATE，它的 fallback 是空字符串)
        response = model_router._get_fallback_response(ScenarioType.USER_PERSONA_UPDATE)
        assert response["text"] == ""

    @pytest.mark.asyncio
    async def test_call_with_fallback_success(self, monkeypatch):
        """测试 call_with_fallback 成功场景"""
        # Mock _call_model 直接返回成功
        async def mock_call_model(model, messages, **kwargs):
            return {
                "text": "Mock response",
                "model": model.name,
                "tier": model.tier,
            }

        monkeypatch.setattr(model_router, "_call_model", mock_call_model)

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
        ]

        response = await model_router.call_with_fallback(
            ScenarioType.NARRATIVE, messages
        )

        assert "text" in response
        assert response["text"] == "Mock response"
        assert response["model"] == "qwen3.7-max"
        assert response["tier"] == "S"

    @pytest.mark.asyncio
    async def test_call_with_fallback_fallback_on_error(self, monkeypatch):
        """测试 call_with_fallback 降级场景"""
        call_count = {"value": 0}

        # Mock _call_model 前两次失败，第三次成功
        async def mock_call_model(model, messages, **kwargs):
            call_count["value"] += 1
            if call_count["value"] <= 2:
                raise Exception(f"Model {model.name} failed")
            return {
                "text": "Fallback success",
                "model": model.name,
                "tier": model.tier,
            }

        monkeypatch.setattr(model_router, "_call_model", mock_call_model)

        messages = [{"role": "user", "content": "Hello"}]

        response = await model_router.call_with_fallback(
            ScenarioType.NARRATIVE, messages
        )

        # 应该调用3次（主模型 + 2个fallback）
        assert call_count["value"] == 3
        assert response["text"] == "Fallback success"

    @pytest.mark.asyncio
    async def test_call_with_fallback_all_fail(self, monkeypatch):
        """测试 call_with_fallback 所有模型都失败"""
        # Mock _call_model 全部失败
        async def mock_call_model(model, messages, **kwargs):
            raise Exception(f"Model {model.name} failed")

        monkeypatch.setattr(model_router, "_call_model", mock_call_model)

        messages = [{"role": "user", "content": "Hello"}]

        response = await model_router.call_with_fallback(
            ScenarioType.NARRATIVE, messages
        )

        # 应该返回预设回复
        assert response["model"] == "fallback"
        assert response["tier"] == "preset"
        assert "text" in response


class TestFallbackResponses:
    """测试预设回复配置"""

    def test_all_scenarios_have_fallback(self):
        """验证所有场景都有预设回复"""
        for scenario in ScenarioType:
            assert scenario in FALLBACK_RESPONSES

    def test_default_fallback_exists(self):
        """验证默认预设回复存在"""
        assert DEFAULT_FALLBACK == "服务暂时不可用，请稍后重试。"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
