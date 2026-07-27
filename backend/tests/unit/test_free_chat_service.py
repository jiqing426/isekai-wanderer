"""
DEV-CR2-009: FreeChatService Red tests (AC-058).

Tests:
- 5 topic templates available
- Topic validation (valid/invalid topic_id)
- Session creation for free chat
- MockLLMProvider returns response
- Emotion tag system
"""

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone

import pytest

from app.services.free_chat_service import FreeChatService, TOPIC_TEMPLATES


class TestTopicTemplates:
    """Test the 5 built-in topic templates."""

    def test_five_topics_exist(self):
        assert len(TOPIC_TEMPLATES) == 5

    def test_each_topic_has_required_fields(self):
        for topic in TOPIC_TEMPLATES:
            assert "id" in topic
            assert "title" in topic
            assert "description" in topic
            assert "prompt_prefix" in topic

    def test_topic_ids_are_unique(self):
        ids = [t["id"] for t in TOPIC_TEMPLATES]
        assert len(ids) == len(set(ids))


class TestFreeChatServiceTopicValidation:
    """Test topic validation logic."""

    @pytest.mark.asyncio
    async def test_valid_topic_accepted(self):
        svc = FreeChatService()
        result = await svc.validate_topic(TOPIC_TEMPLATES[0]["id"])
        assert result is True

    @pytest.mark.asyncio
    async def test_invalid_topic_rejected(self):
        svc = FreeChatService()
        result = await svc.validate_topic("nonexistent-topic-xyz")
        assert result is False


class TestFreeChatServiceSession:
    """Test free chat session creation and message handling."""

    @pytest.mark.asyncio
    async def test_create_session(self):
        svc = FreeChatService()
        session = await svc.create_session(
            user_id=str(uuid.uuid4()),
            topic_id=TOPIC_TEMPLATES[0]["id"],
        )
        assert session is not None
        assert "session_id" in session
        assert "topic_id" in session
        assert session["topic_id"] == TOPIC_TEMPLATES[0]["id"]

    @pytest.mark.asyncio
    async def test_send_message_returns_response(self):
        svc = FreeChatService()
        session = await svc.create_session(
            user_id=str(uuid.uuid4()),
            topic_id=TOPIC_TEMPLATES[0]["id"],
        )
        response = await svc.send_message(
            session_id=session["session_id"],
            message="你好，我想聊聊我的冒险经历",
        )
        assert response is not None
        assert "text" in response
        assert "emotion" in response
        assert len(response["text"]) > 0

    @pytest.mark.asyncio
    async def test_emotion_tag_in_response(self):
        svc = FreeChatService()
        session = await svc.create_session(
            user_id=str(uuid.uuid4()),
            topic_id=TOPIC_TEMPLATES[0]["id"],
        )
        response = await svc.send_message(
            session_id=session["session_id"],
            message="今天遇到了一只可爱的猫咪",
        )
        assert response["emotion"] in [
            "happy", "sad", "neutral", "excited", "thoughtful", "surprised",
        ]
