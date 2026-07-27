"""AI dialogue quality optimization service.

Handles:
- Prompt template optimization by affection level
- Character consistency enhancement
- Long dialogue context summarization
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal


class PromptOptimizer:
    """Optimizes prompts based on affection level and dialogue quality."""

    # Affection-based prompt adjustments
    AFFECTION_ADJUSTMENTS = {
        "cold": {
            "range": (Decimal("0.0"), Decimal("20.0")),
            "tone_modifier": "冷淡、疏远、简短回复",
            "behavior_hint": "角色对玩家不信任，回复保持距离感，避免主动分享信息。",
        },
        "neutral": {
            "range": (Decimal("20.0"), Decimal("40.0")),
            "tone_modifier": "礼貌、中立、适度友好",
            "behavior_hint": "角色对玩家态度中性，可以正常交流但不会特别热情。",
        },
        "friendly": {
            "range": (Decimal("40.0"), Decimal("60.0")),
            "tone_modifier": "友好、温暖、主动关心",
            "behavior_hint": "角色视玩家为朋友，会主动关心、分享日常、表达真实想法。",
        },
        "close": {
            "range": (Decimal("60.0"), Decimal("80.0")),
            "tone_modifier": "亲密、信任、偶尔撒娇",
            "behavior_hint": "角色与玩家关系亲密，会撒娇、吐槽、展现脆弱的一面。",
        },
        "devoted": {
            "range": (Decimal("80.0"), Decimal("100.0")),
            "tone_modifier": "深情、依赖、高度信任",
            "behavior_hint": "角色深爱玩家，会表达依赖、担忧、期待，偶尔害羞或吃醋。",
        },
    }

    @classmethod
    def get_affection_level(cls, affection_value: Decimal) -> str:
        """Determine affection level from numeric value.

        Args:
            affection_value: Affection score (0-100).

        Returns:
            Level name: "cold", "neutral", "friendly", "close", "devoted".
        """
        for level, config in cls.AFFECTION_ADJUSTMENTS.items():
            low, high = config["range"]
            if low <= affection_value < high:
                return level
        return "devoted"  # Default to highest if >= 100

    @classmethod
    def optimize_prompt(
        cls,
        base_prompt: str,
        affection: Decimal,
        character_name: str,
        context_summary: Optional[str] = None,
    ) -> str:
        """Optimize prompt with affection-based adjustments.

        Args:
            base_prompt: Original system/user prompt.
            affection: Current affection value (0-100).
            character_name: Character name for personalization.
            context_summary: Optional summary of recent dialogue context.

        Returns:
            Enhanced prompt string.
        """
        level = cls.get_affection_level(affection)
        config = cls.AFFECTION_ADJUSTMENTS[level]

        # Build affection-aware instruction block
        affection_block = f"""
【关系状态：{level}（好感度 {affection}/100）】
语气调整：{config['tone_modifier']}
行为提示：{config['behavior_hint']}
"""

        # Add context summary if provided
        context_block = ""
        if context_summary:
            context_block = f"""
【近期对话摘要】
{context_summary}
"""

        # Combine all parts
        enhanced = f"""{base_prompt}
{affection_block}
{context_block}
【重要提示】
- 保持角色「{character_name}」的性格一致性
- 根据好感度调整语气和亲密度
- 回复自然、简短（1-3 句话），避免说教或过度解释
- 使用 [emotion:xxx] 标签标注情绪变化
"""
        return enhanced.strip()


class PersonaConsistencyGuard:
    """Ensures character consistency across dialogue turns."""

    # Common consistency violations
    VIOLATION_PATTERNS = {
        "breaking_character": [
            "作为 AI", "我是 AI", "我是一个语言模型",
            "我没有感情", "我没有身体", "我无法",
        ],
        "fourth_wall": [
            "游戏", "剧情", "设定", "开发者", "玩家",
        ],
        "out_of_character": [
            "我建议", "你可以", "也许应该",  # Too advisory
        ],
    }

    @classmethod
    def check_consistency(
        cls,
        response: str,
        character_name: str,
        personality_traits: List[str],
    ) -> Dict[str, Any]:
        """Check response for character consistency issues.

        Args:
            response: LLM-generated response text.
            character_name: Character name.
            personality_traits: List of character personality traits.

        Returns:
            Dict with:
            - is_consistent: bool
            - violations: List[str]
            - suggestions: List[str]
        """
        violations = []
        suggestions = []

        # Check for breaking character
        for phrase in cls.VIOLATION_PATTERNS["breaking_character"]:
            if phrase in response:
                violations.append(f"打破角色：包含 '{phrase}'")
                suggestions.append(f"删除 '{phrase}'，用角色视角重新表述")

        # Check for fourth wall breaks (context-dependent)
        # Only flag if character shouldn't know about games/meta
        for phrase in cls.VIOLATION_PATTERNS["fourth_wall"]:
            if phrase in response and "游戏" not in personality_traits:
                violations.append(f"打破第四面墙：提及 '{phrase}'")
                suggestions.append(f"避免提及 '{phrase}'，除非角色设定允许")

        # Check if response is too advisory (should be in-character)
        advisory_count = sum(1 for p in cls.VIOLATION_PATTERNS["out_of_character"] if p in response)
        if advisory_count >= 2:
            violations.append("过于建议性：像助手而非角色")
            suggestions.append("用角色口吻表达，例如「我觉得...」而非「我建议...」")

        # Check for emotion tag consistency
        emotion_tags = cls._extract_emotion_tags(response)
        if emotion_tags:
            # Validate emotion tags are reasonable
            valid_emotions = {"happy", "sad", "angry", "shy", "surprised", "neutral", "worried", "excited"}
            for tag in emotion_tags:
                if tag not in valid_emotions:
                    violations.append(f"无效情绪标签：[emotion:{tag}]")
                    suggestions.append(f"使用标准情绪：{', '.join(valid_emotions)}")

        is_consistent = len(violations) == 0
        return {
            "is_consistent": is_consistent,
            "violations": violations,
            "suggestions": suggestions,
        }

    @staticmethod
    def _extract_emotion_tags(text: str) -> List[str]:
        """Extract [emotion:xxx] tags from text."""
        import re
        pattern = r"\[emotion:([a-zA-Z_]+)\]"
        return re.findall(pattern, text)

    @classmethod
    def enhance_response(
        cls,
        response: str,
        character_name: str,
        personality_traits: List[str],
    ) -> str:
        """Enhance response with consistency fixes (basic).

        Note: This is a simple fix. For complex issues, regenerate with better prompt.

        Args:
            response: Original response.
            character_name: Character name.
            personality_traits: Character traits.

        Returns:
            Enhanced response (minor fixes only).
        """
        enhanced = response

        # Remove obvious AI self-references
        for phrase in cls.VIOLATION_PATTERNS["breaking_character"]:
            enhanced = enhanced.replace(phrase, "")

        # Clean up extra spaces
        enhanced = " ".join(enhanced.split())

        return enhanced


class ContextSummarizer:
    """Summarizes long dialogue contexts to fit token limits."""

    @classmethod
    def summarize_dialogue(
        cls,
        dialogue_history: List[Dict[str, str]],
        max_turns: int = 10,
        preserve_recent: int = 4,
    ) -> str:
        """Summarize dialogue history into compact summary.

        Args:
            dialogue_history: List of {"role": "user/assistant", "content": "..."} dicts.
            max_turns: Maximum turns to include in summary.
            preserve_recent: Number of recent turns to preserve verbatim.

        Returns:
            Formatted summary string.
        """
        if not dialogue_history:
            return ""

        # Split into old (to summarize) and recent (to preserve)
        if len(dialogue_history) <= preserve_recent:
            # All recent, no need to summarize
            return cls._format_recent(dialogue_history)

        old_turns = dialogue_history[:-preserve_recent]
        recent_turns = dialogue_history[-preserve_recent:]

        # Summarize old turns (simple extraction)
        old_summary = cls._summarize_old_turns(old_turns, max_turns)

        # Format recent turns
        recent_formatted = cls._format_recent(recent_turns)

        # Combine
        summary = f"""【早期对话摘要】
{old_summary}

【近期对话】
{recent_formatted}
"""
        return summary.strip()

    @staticmethod
    def _summarize_old_turns(turns: List[Dict[str, str]], max_turns: int) -> str:
        """Summarize older dialogue turns.

        Simple strategy: Extract key user statements and character responses.
        For better results, use LLM-based summarization.
        """
        if not turns:
            return "（无早期对话）"

        # Take first few and last few of old turns
        if len(turns) <= max_turns:
            selected = turns
        else:
            half = max_turns // 2
            selected = turns[:half] + turns[-half:]

        # Format as bullet points
        summaries = []
        for turn in selected:
            role = "玩家" if turn.get("role") == "user" else "角色"
            content = turn.get("content", "")[:80]  # Truncate long content
            summaries.append(f"- {role}：{content}")

        return "\n".join(summaries)

    @staticmethod
    def _format_recent(turns: List[Dict[str, str]]) -> str:
        """Format recent turns for direct inclusion."""
        formatted = []
        for turn in turns:
            role = "玩家" if turn.get("role") == "user" else "角色"
            content = turn.get("content", "")
            formatted.append(f"{role}：{content}")
        return "\n".join(formatted)


# Convenience exports
__all__ = [
    "PromptOptimizer",
    "PersonaConsistencyGuard",
    "ContextSummarizer",
]
