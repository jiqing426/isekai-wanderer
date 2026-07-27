"""Tests for dialogue quality optimization service (Task 3)."""

import pytest
from decimal import Decimal
from app.services.dialogue_quality import (
    PromptOptimizer,
    PersonaConsistencyGuard,
    ContextSummarizer,
)


class TestPromptOptimizer:
    """Test PromptOptimizer affection-based prompt optimization."""

    def test_get_affection_level_cold(self):
        """Test cold affection level detection."""
        assert PromptOptimizer.get_affection_level(Decimal("0.0")) == "cold"
        assert PromptOptimizer.get_affection_level(Decimal("10.0")) == "cold"
        assert PromptOptimizer.get_affection_level(Decimal("19.9")) == "cold"

    def test_get_affection_level_neutral(self):
        """Test neutral affection level detection."""
        assert PromptOptimizer.get_affection_level(Decimal("20.0")) == "neutral"
        assert PromptOptimizer.get_affection_level(Decimal("30.0")) == "neutral"
        assert PromptOptimizer.get_affection_level(Decimal("39.9")) == "neutral"

    def test_get_affection_level_friendly(self):
        """Test friendly affection level detection."""
        assert PromptOptimizer.get_affection_level(Decimal("40.0")) == "friendly"
        assert PromptOptimizer.get_affection_level(Decimal("50.0")) == "friendly"
        assert PromptOptimizer.get_affection_level(Decimal("59.9")) == "friendly"

    def test_get_affection_level_close(self):
        """Test close affection level detection."""
        assert PromptOptimizer.get_affection_level(Decimal("60.0")) == "close"
        assert PromptOptimizer.get_affection_level(Decimal("70.0")) == "close"
        assert PromptOptimizer.get_affection_level(Decimal("79.9")) == "close"

    def test_get_affection_level_devoted(self):
        """Test devoted affection level detection."""
        assert PromptOptimizer.get_affection_level(Decimal("80.0")) == "devoted"
        assert PromptOptimizer.get_affection_level(Decimal("90.0")) == "devoted"
        assert PromptOptimizer.get_affection_level(Decimal("100.0")) == "devoted"

    def test_optimize_prompt_basic(self):
        """Test basic prompt optimization."""
        base = "你是一个角色。"
        result = PromptOptimizer.optimize_prompt(base, Decimal("50.0"), "Alice")

        assert "Alice" in result
        assert "friendly" in result
        assert "好感度" in result
        assert "50" in result

    def test_optimize_prompt_cold_level(self):
        """Test prompt optimization for cold level."""
        base = "你是一个角色。"
        result = PromptOptimizer.optimize_prompt(base, Decimal("10.0"), "Bob")

        assert "cold" in result
        assert "冷淡" in result or "疏远" in result
        assert "Bob" in result

    def test_optimize_prompt_devoted_level(self):
        """Test prompt optimization for devoted level."""
        base = "你是一个角色。"
        result = PromptOptimizer.optimize_prompt(base, Decimal("95.0"), "Charlie")

        assert "devoted" in result
        assert "深情" in result or "依赖" in result
        assert "Charlie" in result

    def test_optimize_prompt_with_context_summary(self):
        """Test prompt optimization with context summary."""
        base = "你是一个角色。"
        context = "玩家最近提到工作压力大，喜欢喝咖啡。"
        result = PromptOptimizer.optimize_prompt(base, Decimal("60.0"), "Alice", context)

        assert "近期对话摘要" in result
        assert "工作压力" in result
        assert "咖啡" in result

    def test_optimize_prompt_without_context(self):
        """Test prompt optimization without context summary."""
        base = "你是一个角色。"
        result = PromptOptimizer.optimize_prompt(base, Decimal("50.0"), "Alice", None)

        assert "近期对话摘要" not in result
        assert "Alice" in result

    def test_optimize_prompt_includes_emotion_instruction(self):
        """Test that optimized prompt includes emotion tag instruction."""
        base = "你是一个角色。"
        result = PromptOptimizer.optimize_prompt(base, Decimal("50.0"), "Alice")

        assert "[emotion:xxx]" in result
        assert "情绪" in result


class TestPersonaConsistencyGuard:
    """Test PersonaConsistencyGuard character consistency checking."""

    def test_check_consistency_clean(self):
        """Test consistency check with clean response."""
        response = "我今天心情很好呢！[emotion:happy]"
        result = PersonaConsistencyGuard.check_consistency(
            response, "Alice", ["开朗", "友好"]
        )

        assert result["is_consistent"] is True
        assert len(result["violations"]) == 0

    def test_check_consistency_breaking_character(self):
        """Test detection of AI self-reference."""
        response = "作为 AI，我无法表达真实情感。"
        result = PersonaConsistencyGuard.check_consistency(
            response, "Alice", ["开朗"]
        )

        assert result["is_consistent"] is False
        assert any("打破角色" in v for v in result["violations"])
        assert len(result["suggestions"]) > 0

    def test_check_consistency_fourth_wall(self):
        """Test detection of fourth wall breaks."""
        response = "这个游戏的剧情真有趣。"
        result = PersonaConsistencyGuard.check_consistency(
            response, "Alice", ["开朗"]
        )

        assert result["is_consistent"] is False
        assert any("第四面墙" in v for v in result["violations"])

    def test_check_consistency_fourth_wall_allowed(self):
        """Test that game reference is allowed if character knows about games."""
        response = "这个游戏的剧情真有趣。"
        result = PersonaConsistencyGuard.check_consistency(
            response, "Alice", ["开朗", "游戏"]
        )

        assert result["is_consistent"] is True

    def test_check_consistency_advisory_tone(self):
        """Test detection of overly advisory tone."""
        response = "我建议你这样做，也许应该尝试一下，你可以考虑。"
        result = PersonaConsistencyGuard.check_consistency(
            response, "Alice", ["开朗"]
        )

        assert result["is_consistent"] is False
        assert any("建议性" in v for v in result["violations"])

    def test_check_consistency_invalid_emotion_tag(self):
        """Test detection of invalid emotion tags."""
        response = "我今天很[emotion:super_happy]！"
        result = PersonaConsistencyGuard.check_consistency(
            response, "Alice", ["开朗"]
        )

        assert result["is_consistent"] is False
        assert any("无效情绪标签" in v for v in result["violations"])

    def test_check_consistency_valid_emotion_tags(self):
        """Test that valid emotion tags pass."""
        response = "我今天很[emotion:happy]，但有点[emotion:worried]。"
        result = PersonaConsistencyGuard.check_consistency(
            response, "Alice", ["开朗"]
        )

        assert result["is_consistent"] is True

    def test_extract_emotion_tags(self):
        """Test emotion tag extraction."""
        text = "Hello [emotion:happy] world [emotion:sad] test"
        tags = PersonaConsistencyGuard._extract_emotion_tags(text)
        assert tags == ["happy", "sad"]

    def test_extract_emotion_tags_empty(self):
        """Test emotion tag extraction with no tags."""
        text = "Hello world"
        tags = PersonaConsistencyGuard._extract_emotion_tags(text)
        assert tags == []

    def test_enhance_response_removes_ai_reference(self):
        """Test that enhance_response removes AI self-references."""
        response = "作为 AI，我觉得今天天气很好。"
        enhanced = PersonaConsistencyGuard.enhance_response(
            response, "Alice", ["开朗"]
        )

        assert "作为 AI" not in enhanced
        assert "今天天气很好" in enhanced

    def test_enhance_response_cleans_spaces(self):
        """Test that enhance_response cleans up extra spaces."""
        response = "Hello    world   test"
        enhanced = PersonaConsistencyGuard.enhance_response(
            response, "Alice", ["开朗"]
        )

        assert "  " not in enhanced  # No double spaces


class TestContextSummarizer:
    """Test ContextSummarizer dialogue summarization."""

    def test_summarize_empty_dialogue(self):
        """Test summarization of empty dialogue."""
        result = ContextSummarizer.summarize_dialogue([])
        assert result == ""

    def test_summarize_short_dialogue(self):
        """Test summarization of short dialogue (all recent)."""
        dialogue = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"},
        ]
        result = ContextSummarizer.summarize_dialogue(dialogue, preserve_recent=4)

        assert "玩家：你好" in result
        assert "角色：你好！" in result

    def test_summarize_long_dialogue(self):
        """Test summarization of long dialogue (old + recent)."""
        dialogue = [
            {"role": "user", "content": "我叫小明"},
            {"role": "assistant", "content": "小明你好"},
            {"role": "user", "content": "我喜欢咖啡"},
            {"role": "assistant", "content": "咖啡不错"},
            {"role": "user", "content": "今天天气好"},
            {"role": "assistant", "content": "是的呢"},
            {"role": "user", "content": "再见"},
            {"role": "assistant", "content": "再见！"},
        ]
        result = ContextSummarizer.summarize_dialogue(dialogue, preserve_recent=4)

        # Should have both sections
        assert "早期对话摘要" in result
        assert "近期对话" in result
        # Recent should be verbatim
        assert "玩家：今天天气好" in result
        assert "角色：是的呢" in result

    def test_summarize_preserves_recent_count(self):
        """Test that correct number of recent turns is preserved."""
        dialogue = [
            {"role": "user", "content": f"消息{i}"} for i in range(10)
        ]
        result = ContextSummarizer.summarize_dialogue(dialogue, preserve_recent=3)

        # Last 3 should be in recent section
        assert "消息7" in result
        assert "消息8" in result
        assert "消息9" in result

    def test_summarize_truncates_long_content(self):
        """Test that long content is truncated in summary."""
        long_content = "A" * 200
        dialogue = [
            {"role": "user", "content": long_content},
            {"role": "assistant", "content": "回复"},
        ]
        result = ContextSummarizer._summarize_old_turns(dialogue, max_turns=10)

        # Should not contain full 200 chars
        assert len(result) < 200

    def test_format_recent(self):
        """Test formatting of recent turns."""
        turns = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！"},
        ]
        result = ContextSummarizer._format_recent(turns)

        assert "玩家：你好" in result
        assert "角色：你好！" in result

    def test_summarize_old_turns_empty(self):
        """Test summarization of empty old turns."""
        result = ContextSummarizer._summarize_old_turns([], max_turns=10)
        assert "无早期对话" in result

    def test_summarize_old_turns_selection(self):
        """Test that old turns are selected (first half + last half)."""
        turns = [{"role": "user", "content": f"消息{i}"} for i in range(20)]
        result = ContextSummarizer._summarize_old_turns(turns, max_turns=10)

        # Should contain some from beginning and some from end
        assert "消息0" in result
        assert "消息19" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
