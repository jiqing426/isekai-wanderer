"""RuleEngine unit tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.narrative.rule_engine import (
    RuleEngine,
    ValidationResult,
    get_affection_level,
    get_level_threshold,
    AFFECTION_LEVELS,
    INTIMATE_TERMS,
)
from app.models.script import Character


def _make_character(style: str = "gentle") -> Character:
    char = MagicMock(spec=Character)
    char.id = uuid4()
    char.name = "TestChar"
    char.dialogue_style = style
    char.description = "A test character"
    return char


# ---- Affection level mapping ----

class TestAffectionLevels:
    def test_acquaintance(self):
        assert get_affection_level(0) == "acquaintance"
        assert get_affection_level(19) == "acquaintance"

    def test_ambiguous(self):
        assert get_affection_level(20) == "ambiguous"
        assert get_affection_level(39) == "ambiguous"

    def test_trust(self):
        assert get_affection_level(40) == "trust"
        assert get_affection_level(59) == "trust"

    def test_bond(self):
        assert get_affection_level(60) == "bond"
        assert get_affection_level(79) == "bond"

    def test_love(self):
        assert get_affection_level(80) == "love"
        assert get_affection_level(100) == "love"

    def test_thresholds(self):
        assert get_level_threshold("acquaintance") == 0
        assert get_level_threshold("love") == 80


# ---- Intimate term validation ----

class TestAffectionTermCheck:
    @pytest.mark.asyncio
    async def test_intimate_term_blocked_at_low_affection(self):
        db = MagicMock()
        engine = RuleEngine(db)
        char = _make_character()
        result = await engine.validate_dialogue(
            text="你好啊亲爱的，今天过得怎么样？",
            character=char,
            affection_value=25,
        )
        assert result.passed is False
        assert any(v.rule == "affection_intimate_term" for v in result.violations)

    @pytest.mark.asyncio
    async def test_intimate_term_allowed_at_high_affection(self):
        db = MagicMock()
        engine = RuleEngine(db)
        char = _make_character()
        result = await engine.validate_dialogue(
            text="你好啊亲爱的，今天过得怎么样？",
            character=char,
            affection_value=70,
        )
        assert result.passed is True

    @pytest.mark.asyncio
    async def test_normal_text_passes(self):
        db = MagicMock()
        engine = RuleEngine(db)
        char = _make_character()
        result = await engine.validate_dialogue(
            text="今天天气不错，我们去散步吧。",
            character=char,
            affection_value=10,
        )
        assert result.passed is True


# ---- Personality consistency ----

class TestPersonalityCheck:
    @pytest.mark.asyncio
    async def test_gentle_char_aggressive_blocked(self):
        db = MagicMock()
        engine = RuleEngine(db)
        char = _make_character("gentle")
        result = await engine.validate_dialogue(
            text="你给我滚，我不想看到你！",
            character=char,
            affection_value=50,
        )
        assert result.passed is False
        assert any(v.rule == "personality_mismatch" for v in result.violations)

    @pytest.mark.asyncio
    async def test_cold_char_emotional_warning(self):
        db = MagicMock()
        engine = RuleEngine(db)
        char = _make_character("cold")
        result = await engine.validate_dialogue(
            text="呜呜呜，太开心了！",
            character=char,
            affection_value=50,
        )
        # Warning severity, not error — may still pass
        personality_violations = [v for v in result.violations if v.rule == "personality_mismatch"]
        assert len(personality_violations) > 0
