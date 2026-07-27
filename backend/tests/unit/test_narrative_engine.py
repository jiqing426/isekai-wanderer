"""NarrativeEngine unit tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from app.services.narrative.narrative_engine import (
    NarrativeEngine,
    MAX_RETRIES,
    FALLBACK_DIALOGUES,
)
from app.models.script import Node, Character, NodeChoice


class TestNarrativeEngineConstants:
    def test_max_retries(self):
        assert MAX_RETRIES == 2

    def test_fallback_has_default(self):
        assert "_default" in FALLBACK_DIALOGUES


class TestInferEmotion:
    def _make_engine(self):
        db = MagicMock()
        return NarrativeEngine(db)

    def test_happy_emotion(self):
        engine = self._make_engine()
        node = MagicMock()
        node.content = {}
        result = engine._infer_emotion("I'm so happy to see you!", node)
        assert result == "happy"

    def test_sad_emotion(self):
        engine = self._make_engine()
        node = MagicMock()
        node.content = {}
        result = engine._infer_emotion("I'm sorry, this makes me sad.", node)
        assert result == "sad"

    def test_angry_emotion(self):
        engine = self._make_engine()
        node = MagicMock()
        node.content = {}
        result = engine._infer_emotion("I'm angry about this!", node)
        assert result == "angry"

    def test_neutral_emotion(self):
        engine = self._make_engine()
        node = MagicMock()
        node.content = {}
        result = engine._infer_emotion("The sky is blue today.", node)
        assert result == "neutral"

    def test_emotion_from_node_content(self):
        engine = self._make_engine()
        node = MagicMock()
        node.content = {"emotion": "surprised"}
        result = engine._infer_emotion("anything", node)
        assert result == "surprised"


class TestGetFallback:
    def _make_engine(self):
        db = MagicMock()
        return NarrativeEngine(db)

    def test_default_fallback(self):
        engine = self._make_engine()
        node = MagicMock()
        node.id = uuid4()
        node.content = {}
        result = engine._get_fallback(node)
        assert result == FALLBACK_DIALOGUES["_default"]

    def test_node_content_fallback(self):
        engine = self._make_engine()
        node = MagicMock()
        node.id = uuid4()
        node.content = {"fallback": "The character looks away silently."}
        result = engine._get_fallback(node)
        assert result == "The character looks away silently."


class TestSSEEvent:
    def test_sse_event_format(self):
        result = NarrativeEngine._sse_event("text", {"content": "hello"})
        assert result.startswith("event: text\n")
        assert '"content": "hello"' in result
        assert result.endswith("\n\n")
