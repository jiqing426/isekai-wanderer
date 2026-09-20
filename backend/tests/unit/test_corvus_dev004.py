"""Unit tests for CR-037 DEV-004: SSE streaming + event translation.

Test Case Artifacts:
- TC-SSE-001: SSE 事件翻译映射验证
- TC-API-005: custom-input SSE 端点 (mocked)

Covers AC-009, AC-010, AC-011, AC-026.

Uses SQLite in-memory DB with conftest.py fixtures.
CorvusClient is mocked to simulate SSE events.
"""
import pytest
import json
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID
from typing import AsyncGenerator

from app.models.corvus import CorvusGameSession, PlayerCandidate
from app.api.v1.auth import get_current_user_id
from app.main import app
from app.services.corvus_adapter import SSETranslator, CorvusAdapter


# ── TC-SSE-001: SSE 事件翻译映射验证 ────────────────────────────────────


class TestTCSSE001EventTranslation:
    """TC-SSE-001: Verify SSE event translation from Corvus format to frontend format."""

    def test_token_translates_to_text(self):
        """AC-010: token event → {type:text, content}."""
        translator = SSETranslator()
        result = translator.translate({"type": "token", "content": "你"})
        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert result[0]["content"] == "你"

    def test_token_with_empty_content(self):
        """AC-010: token event with empty content yields empty text."""
        translator = SSETranslator()
        result = translator.translate({"type": "token", "content": ""})
        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert result[0]["content"] == ""

    def test_user_event_filtered(self):
        """AC-010: user event (echo) is filtered out."""
        translator = SSETranslator()
        result = translator.translate({"type": "user", "content": "hello"})
        assert len(result) == 0

    def test_context_assembled_filtered(self):
        """AC-010: context-assembled event is filtered out."""
        translator = SSETranslator()
        result = translator.translate({"type": "context-assembled", "estimatedTokens": 987})
        assert len(result) == 0

    def test_narrator_filtered(self):
        """AC-010: narrator marker event is filtered out."""
        translator = SSETranslator()
        result = translator.translate({"type": "narrator"})
        assert len(result) == 0

    def test_gm_start_filtered(self):
        """AC-010: gm-start event is filtered out."""
        translator = SSETranslator()
        result = translator.translate({"type": "gm-start"})
        assert len(result) == 0

    def test_stream_end_translates(self):
        """AC-010: stream_end event → {type:stream_end}."""
        translator = SSETranslator()
        result = translator.translate({"type": "stream_end"})
        assert len(result) == 1
        assert result[0]["type"] == "stream_end"

    def test_error_translates(self):
        """AC-011: error event → {type:error, message}."""
        translator = SSETranslator()
        result = translator.translate({"type": "error", "message": "LLM timeout"})
        assert len(result) == 1
        assert result[0]["type"] == "error"
        assert result[0]["message"] == "LLM timeout"

    def test_error_without_message(self):
        """AC-011: error event without message field."""
        translator = SSETranslator()
        result = translator.translate({"type": "error", "error": "Connection refused"})
        assert len(result) == 1
        assert result[0]["type"] == "error"
        assert "Connection refused" in result[0]["message"]

    def test_done_translates_to_done(self):
        """AC-010: done event → {type:done, text, character_id, character_name}."""
        translator = SSETranslator()
        done_event = {
            "type": "done",
            "content": "你好，我是白夜。",
            "characterId": "char-uuid-123",
            "characterName": "白夜",
        }
        result = translator.translate(done_event)
        assert len(result) == 1
        assert result[0]["type"] == "done"
        assert "你好" in result[0]["text"]
        assert result[0]["character_id"] == "char-uuid-123"
        assert result[0]["character_name"] == "白夜"

    def test_done_with_message_field(self):
        """AC-010: done event with 'message' nested object."""
        translator = SSETranslator()
        done_event = {
            "type": "done",
            "message": {
                "content": "完整回复文本",
                "characterId": "npc-456",
                "characterName": "NPC",
            },
        }
        result = translator.translate(done_event)
        assert len(result) == 1
        assert result[0]["type"] == "done"
        assert result[0]["text"] == "完整回复文本"
        assert result[0]["character_id"] == "npc-456"

    def test_gm_update_translates(self):
        """AC-010: gm_update event → {type:gm_update, affinity_deltas, inventory_changes, ...}."""
        translator = SSETranslator()
        gm_event = {
            "type": "gm_update",
            "summary": {
                "statChanges": [{"character": "npc1", "stat": "affinity", "delta": 5}],
                "inventoryChanges": [{"action": "add", "item": "sword"}],
                "relationshipChanges": [],
                "newCharacters": ["蒙面女子"],
                "worldEvents": ["下雨了"],
            },
        }
        result = translator.translate(gm_event)
        assert len(result) == 1
        assert result[0]["type"] == "gm_update"
        assert "affinity_deltas" in result[0]
        assert "inventory_changes" in result[0]
        assert "new_characters" in result[0]

    def test_gm_update_empty_summary(self):
        """AC-010: gm_update with empty summary still yields a gm_update event."""
        translator = SSETranslator()
        gm_event = {
            "type": "gm_update",
            "summary": {},
        }
        result = translator.translate(gm_event)
        assert len(result) == 1
        assert result[0]["type"] == "gm_update"

    def test_unknown_event_passes_through(self):
        """AC-010: unknown event type is passed through with warning."""
        translator = SSETranslator()
        result = translator.translate({"type": "new-future-event", "data": "test"})
        assert len(result) == 1
        assert result[0]["type"] == "unknown"

    def test_full_stream_sequence(self):
        """AC-010: Full SSE stream sequence: tokens → done → gm_update → stream_end."""
        translator = SSETranslator()
        corvus_events = [
            {"type": "user", "content": "你好"},  # filtered
            {"type": "context-assembled", "estimatedTokens": 500},  # filtered
            {"type": "token", "content": "你"},  # text
            {"type": "token", "content": "好"},  # text
            {"type": "narrator"},  # filtered
            {"type": "token", "content": "，我是白夜"},  # text
            {"type": "done", "content": "你好，我是白夜", "characterId": "c1", "characterName": "白夜"},
            {"type": "gm-start"},  # filtered
            {"type": "gm_update", "summary": {"statChanges": [{"delta": 3}]}},
            {"type": "stream_end"},
        ]

        frontend_events = []
        for event in corvus_events:
            frontend_events.extend(translator.translate(event))

        # Verify sequence
        types = [e["type"] for e in frontend_events]
        assert "text" in types  # tokens translated
        assert "done" in types  # done translated
        assert "gm_update" in types  # gm_update translated
        assert "stream_end" in types  # stream_end translated
        # Filtered types should NOT appear
        assert "user" not in types
        assert "context-assembled" not in types
        assert "narrator" not in types
        assert "gm-start" not in types

    def test_token_sequence_concatenation(self):
        """AC-009: Multiple token events produce concatenated text for StoryPanel."""
        translator = SSETranslator()
        tokens = ["你", "好", "，", "我是", "白夜"]
        full_text = ""
        for token in tokens:
            result = translator.translate({"type": "token", "content": token})
            assert len(result) == 1
            assert result[0]["type"] == "text"
            full_text += result[0]["content"]
        assert full_text == "你好，我是白夜"


# ── TC-API-005: custom-input SSE 端点 (mocked) ──────────────────────────


class TestTCAPI005CustomInputSSE:
    """TC-API-005: Test custom-input endpoint with Corvus SSE streaming."""

    @pytest.mark.asyncio
    async def test_custom_input_corvus_returns_sse(self, client, db_session):
        """AC-009: POST /game/{id}/custom-input with Corvus session returns SSE stream."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        # Create a Corvus session in playing state
        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="test-corvus-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        # Mock CorvusClient.stream_message to yield fake events
        async def mock_stream(game_id, content):
            yield {"type": "token", "content": "你好"}
            yield {"type": "token", "content": "，我是白夜"}
            yield {"type": "done", "content": "你好，我是白夜", "characterId": "c1", "characterName": "白夜"}
            yield {"type": "stream_end"}

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.stream_message = mock_stream
            mock_get.return_value = mock_client

            response = await client.post(
                f"/api/v1/game/{session.id}/custom-input",
                json={"text": "你好"},
            )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        # Parse SSE events from response body
        body = response.text
        events = []
        for line in body.split("\n"):
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))

        # Verify translated events
        types = [e["type"] for e in events]
        assert "text" in types
        assert "done" in types
        assert "stream_end" in types
        # Filtered types should not appear
        assert "token" not in types
        assert "user" not in types

    @pytest.mark.asyncio
    async def test_custom_input_corvus_token_content(self, client, db_session):
        """AC-009: SSE token events contain incremental text content for逐字渲染."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="test-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        async def mock_stream(game_id, content):
            yield {"type": "token", "content": "你"}
            yield {"type": "token", "content": "好"}
            yield {"type": "stream_end"}

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.stream_message = mock_stream
            mock_get.return_value = mock_client

            response = await client.post(
                f"/api/v1/game/{session.id}/custom-input",
                json={"text": "hi"},
            )

        body = response.text
        text_events = []
        for line in body.split("\n"):
            if line.startswith("data: "):
                event = json.loads(line[6:])
                if event["type"] == "text":
                    text_events.append(event["content"])

        # Verify incremental text
        assert text_events == ["你", "好"]

    @pytest.mark.asyncio
    async def test_custom_input_corvus_error_handling(self, client, db_session):
        """AC-011: SSE error event is translated and sent to frontend."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="test-slug-err",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        async def mock_stream(game_id, content):
            yield {"type": "token", "content": "部分文本"}
            yield {"type": "error", "message": "Corvus LLM 超时"}
            yield {"type": "stream_end"}

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.stream_message = mock_stream
            mock_get.return_value = mock_client

            response = await client.post(
                f"/api/v1/game/{session.id}/custom-input",
                json={"text": "hi"},
            )

        body = response.text
        events = []
        for line in body.split("\n"):
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))

        error_events = [e for e in events if e["type"] == "error"]
        assert len(error_events) == 1
        assert "Corvus LLM 超时" in error_events[0]["message"]

    @pytest.mark.asyncio
    async def test_custom_input_corvus_connect_error(self, client, db_session):
        """AC-011: Connection error to Corvus yields error SSE event."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="test-slug-conn",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        import httpx

        async def mock_stream(game_id, content):
            raise httpx.ConnectError("Connection refused")
            yield  # never reached

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.stream_message = mock_stream
            mock_get.return_value = mock_client

            response = await client.post(
                f"/api/v1/game/{session.id}/custom-input",
                json={"text": "hi"},
            )

        assert response.status_code == 200  # SSE still returns 200
        body = response.text
        events = []
        for line in body.split("\n"):
            if line.startswith("data: "):
                events.append(json.loads(line[6:]))

        error_events = [e for e in events if e["type"] == "error"]
        assert len(error_events) >= 1
        assert "连接失败" in error_events[0]["message"] or "Corvus" in error_events[0]["message"]

    @pytest.mark.asyncio
    async def test_custom_input_legacy_still_works(self, client, db_session):
        """AC-019 (preview): Legacy engine custom-input still returns JSON (not SSE)."""
        # Create a legacy GameSession (not CorvusGameSession)
        # This test verifies that non-Corvus sessions still use the old path
        test_user_id = str(uuid.uuid4())
        app.dependency_overrides[get_current_user_id] = lambda: test_user_id

        # Create a legacy game session
        from app.models.game import GameSession
        from app.models.script import Script, Route, Node

        script = Script(
            slug="test-legacy-script",
            title="Test Script",
            description="Test",
            genre="fantasy",
        )
        db_session.add(script)
        await db_session.flush()

        route = Route(script_id=script.id, title="Test Route")
        db_session.add(route)
        await db_session.flush()

        node = Node(
            route_id=route.id,
            node_type="dialogue",
            content={"text": "Hello"},
        )
        db_session.add(node)
        await db_session.flush()

        legacy_session = GameSession(
            user_id=UUID(test_user_id),
            script_id=script.id,
            route_id=route.id,
            current_node_id=node.id,
            status="active",
        )
        db_session.add(legacy_session)
        await db_session.flush()

        # This should NOT return SSE — it should try the legacy path
        # (may fail if narrative engine needs more setup, but should NOT return SSE)
        response = await client.post(
            f"/api/v1/game/{legacy_session.id}/custom-input",
            json={"text": "hello"},
        )

        # Should NOT be text/event-stream
        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" not in content_type

    @pytest.mark.asyncio
    async def test_custom_input_corvus_wrong_status(self, client, db_session):
        """AC-011: Corvus session not in 'playing' status returns error."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=test_user_id,
            status="waiting_select_player",  # Not playing
            corvus_internal_game_id="test-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        response = await client.post(
            f"/api/v1/game/{session.id}/custom-input",
            json={"text": "hi"},
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_custom_input_corvus_not_owner(self, client, db_session):
        """AC-011: Cannot use another user's Corvus session."""
        test_user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=other_user_id,
            status="playing",
            corvus_internal_game_id="test-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        response = await client.post(
            f"/api/v1/game/{session.id}/custom-input",
            json={"text": "hi"},
        )

        assert response.status_code == 403


# ── CorvusClient.stream_message unit tests (AC-026) ─────────────────────


class TestCorvusClientStreamMessage:
    """AC-026: CorvusClient.stream_message SSE reading (mocked HTTP)."""

    @pytest.mark.asyncio
    async def test_stream_message_yields_events(self):
        """AC-026: stream_message yields parsed SSE events from Corvus."""
        from app.services.corvus_client import CorvusClient

        client = CorvusClient()

        # Mock httpx stream response
        sse_lines = [
            'data: {"type":"token","content":"你好"}',
            "",
            'data: {"type":"token","content":"世界"}',
            "",
            'data: {"type":"stream_end"}',
            "",
        ]

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()

        async def aiter_lines():
            for line in sse_lines:
                yield line

        mock_resp.aiter_lines = aiter_lines

        class MockStreamContext:
            async def __aenter__(self):
                return mock_resp

            async def __aexit__(self, *args):
                pass

        mock_http = AsyncMock()
        mock_http.stream = MagicMock(return_value=MockStreamContext())

        with patch.object(client, "_get_client", return_value=mock_http):
            events = []
            async for event in client.stream_message("test-game", "hello"):
                events.append(event)

        assert len(events) == 3
        assert events[0] == {"type": "token", "content": "你好"}
        assert events[1] == {"type": "token", "content": "世界"}
        assert events[2] == {"type": "stream_end"}

    @pytest.mark.asyncio
    async def test_stream_message_handles_invalid_json(self):
        """AC-026: Invalid JSON in SSE data is skipped (not crash)."""
        from app.services.corvus_client import CorvusClient

        client = CorvusClient()

        sse_lines = [
            'data: {"valid":"json"}',
            "",
            'data: {invalid json}',
            "",
            'data: {"type":"stream_end"}',
            "",
        ]

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()

        async def aiter_lines():
            for line in sse_lines:
                yield line

        mock_resp.aiter_lines = aiter_lines

        class MockStreamContext:
            async def __aenter__(self):
                return mock_resp

            async def __aexit__(self, *args):
                pass

        mock_http = AsyncMock()
        mock_http.stream = MagicMock(return_value=MockStreamContext())

        with patch.object(client, "_get_client", return_value=mock_http):
            events = []
            async for event in client.stream_message("test-game", "hello"):
                events.append(event)

        # Invalid JSON line should be skipped, valid ones yielded
        assert len(events) == 2
        assert events[0] == {"valid": "json"}
        assert events[1] == {"type": "stream_end"}


# ── CorvusAdapter.stream_turn unit tests ─────────────────────────────────


class TestCorvusAdapterStreamTurn:
    """Unit tests for CorvusAdapter.stream_turn logic."""

    @pytest.mark.asyncio
    async def test_stream_turn_yields_translated_events(self, db_session):
        """AC-009/010: stream_turn yields SSE lines with translated events."""
        test_user_id = uuid.uuid4()

        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="corvus-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        async def mock_stream(game_id, content):
            yield {"type": "token", "content": "你"}
            yield {"type": "token", "content": "好"}
            yield {"type": "done", "content": "你好", "characterId": "c1", "characterName": "白夜"}
            yield {"type": "stream_end"}

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.stream_message = mock_stream
            mock_get.return_value = mock_client

            adapter = CorvusAdapter(db_session)
            lines = []
            async for line in adapter.stream_turn(
                game_session_id=session.id,
                user_id=test_user_id,
                user_input="你好",
            ):
                lines.append(line)

        # Each line should be "data: {...}\n\n"
        assert len(lines) == 4  # 2 tokens + 1 done + 1 stream_end
        for line in lines:
            assert line.startswith("data: ")
            assert line.endswith("\n\n")

        # Parse and verify
        events = [json.loads(l[6:].strip()) for l in lines]
        assert events[0] == {"type": "text", "content": "你"}
        assert events[1] == {"type": "text", "content": "好"}
        assert events[2]["type"] == "done"
        assert events[2]["text"] == "你好"
        assert events[3] == {"type": "stream_end"}

    @pytest.mark.asyncio
    async def test_stream_turn_connection_error(self, db_session):
        """AC-011: stream_turn yields error event on connection failure."""
        test_user_id = uuid.uuid4()

        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="corvus-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        import httpx

        async def mock_stream(game_id, content):
            raise httpx.ConnectError("Connection refused")
            yield  # never reached

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.stream_message = mock_stream
            mock_get.return_value = mock_client

            adapter = CorvusAdapter(db_session)
            lines = []
            async for line in adapter.stream_turn(
                game_session_id=session.id,
                user_id=test_user_id,
                user_input="hi",
            ):
                lines.append(line)

        assert len(lines) == 1
        event = json.loads(lines[0][6:].strip())
        assert event["type"] == "error"
        assert "连接失败" in event["message"] or "Corvus" in event["message"]

    @pytest.mark.asyncio
    async def test_stream_turn_session_not_found(self, db_session):
        """AC-011: stream_turn raises AppException for non-existent session."""
        from app.core.exceptions import AppException

        with patch("app.services.corvus_adapter.get_corvus_client"):
            adapter = CorvusAdapter(db_session)
            with pytest.raises(AppException) as exc_info:
                async for _ in adapter.stream_turn(
                    game_session_id=uuid.uuid4(),
                    user_id=uuid.uuid4(),
                    user_input="hi",
                ):
                    pass
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_stream_turn_not_playing(self, db_session):
        """AC-011: stream_turn raises AppException if session not in playing status."""
        from app.core.exceptions import AppException

        test_user_id = uuid.uuid4()
        session = CorvusGameSession(
            user_id=test_user_id,
            status="waiting_select_player",
            corvus_internal_game_id="slug",
        )
        db_session.add(session)
        await db_session.flush()

        with patch("app.services.corvus_adapter.get_corvus_client"):
            adapter = CorvusAdapter(db_session)
            with pytest.raises(AppException) as exc_info:
                async for _ in adapter.stream_turn(
                    game_session_id=session.id,
                    user_id=test_user_id,
                    user_input="hi",
                ):
                    pass
            assert exc_info.value.status_code == 400
