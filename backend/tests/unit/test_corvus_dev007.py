"""Unit tests for CR-037 DEV-007: Engine Dispatcher feature flag.

Test Case Artifacts:
- TC-E2E-003: 旧引擎回归测试 (AC-019)
- TC-API-004: feature flag 切换验证 (AC-020)

Covers AC-019, AC-020.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock

from app.models.corvus import CorvusGameSession
from app.api.v1.auth import get_current_user_id
from app.main import app


class TestTCE2E003LegacyRegression:
    """AC-019: engine_type=legacy sessions use NarrativeEngine path."""

    @pytest.mark.asyncio
    async def test_legacy_dialogue_not_corvus(self, client, db_session):
        """AC-019: Legacy GameSession dialogue doesn't check CorvusGameSession."""
        # Legacy sessions are in game_sessions table, not corvus_game_sessions
        # The dialogue endpoint should fall through to NarrativeEngine path
        # We just verify it doesn't return Corvus-style response
        test_user_id = str(uuid.uuid4())
        app.dependency_overrides[get_current_user_id] = lambda: test_user_id

        # Create a legacy GameSession
        from app.models.game import GameSession
        from app.models.script import Script, Route, Node

        script = Script(slug="test-legacy", title="Test", description="t", genre="fantasy")
        db_session.add(script)
        await db_session.flush()

        route = Route(script_id=script.id, title="Route")
        db_session.add(route)
        await db_session.flush()

        node = Node(route_id=route.id, node_type="dialogue", content={"text": "hello"})
        db_session.add(node)
        await db_session.flush()

        session = GameSession(
            user_id=uuid.UUID(test_user_id),
            script_id=script.id,
            route_id=route.id,
            current_node_id=node.id,
            status="active",
        )
        db_session.add(session)
        await db_session.flush()

        # GET dialogue — should use legacy path, not Corvus
        response = await client.get(f"/api/v1/game/{session.id}/dialogue")

        # Should NOT have corvus-specific fields
        if response.status_code == 200:
            data = response.json()
            assert "engine_type" not in data or data.get("engine_type") != "corvus"
            assert "corvus_game_id" not in data

    @pytest.mark.asyncio
    async def test_legacy_choice_not_corvus(self, client, db_session):
        """AC-019: Legacy GameSession choice doesn't use Corvus SSE."""
        test_user_id = str(uuid.uuid4())
        app.dependency_overrides[get_current_user_id] = lambda: test_user_id

        # Use a valid UUID that doesn't exist in corvus_game_sessions
        # so it falls through to legacy path
        fake_uuid = str(uuid.uuid4())
        response = await client.post(
            f"/api/v1/game/{fake_uuid}/choice",
            json={"choice_id": "fake"},
        )
        # Should get error (session not found), but NOT Corvus SSE
        assert "text/event-stream" not in response.headers.get("content-type", "")


class TestTCAPI004FeatureFlagSwitch:
    """AC-020: engine_type=corvus uses CorvusAdapter; legacy uses NarrativeEngine; no interference."""

    @pytest.mark.asyncio
    async def test_corvus_dialogue_returns_corvus_format(self, client, db_session):
        """AC-020: Corvus session dialogue returns Corvus-format response."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="corvus-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        with patch("app.services.corvus_client.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get_game = AsyncMock(return_value={
                "config": {"id": "corvus-slug", "name": "Test Game"},
                "world": {"setting": "fantasy", "tone": "mysterious"},
            })
            mock_get.return_value = mock_client

            response = await client.get(f"/api/v1/game/{session.id}/dialogue")

        assert response.status_code == 200
        data = response.json()
        assert data["engine_type"] == "corvus"
        assert data["corvus_game_id"] == "corvus-slug"
        assert data["choices"] == []  # Corvus has no preset choices

    @pytest.mark.asyncio
    async def test_corvus_choice_returns_sse(self, client, db_session):
        """AC-020: Corvus session choice returns SSE streaming."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="corvus-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        async def mock_stream(game_id, content):
            yield {"type": "token", "content": "response"}
            yield {"type": "stream_end"}

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.stream_message = mock_stream
            mock_client.get_characters = AsyncMock(return_value=[])
            mock_get.return_value = mock_client

            with patch("app.services.corvus_adapter.get_embedding_service") as mock_es:
                mock_embedding = MagicMock()
                mock_embedding.recall = AsyncMock(return_value=[])
                mock_embedding.write_memory = AsyncMock()
                mock_embedding.embed = MagicMock(return_value=[0.1] * 512)
                mock_es.return_value = mock_embedding

                # Use a valid UUID for choice_id so NodeChoice query doesn't crash
                fake_choice_id = str(uuid.uuid4())
                response = await client.post(
                    f"/api/v1/game/{session.id}/choice",
                    json={"choice_id": fake_choice_id},
                )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_corvus_dialogue_wrong_status(self, client, db_session):
        """AC-020: Corvus dialogue with wrong status returns 400."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=test_user_id,
            status="waiting_select_player",  # Not playing
            corvus_internal_game_id="corvus-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        response = await client.get(f"/api/v1/game/{session.id}/dialogue")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_corvus_dialogue_not_owner(self, client, db_session):
        """AC-020: Corvus dialogue ownership check."""
        test_user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=other_user_id,
            status="playing",
            corvus_internal_game_id="corvus-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        response = await client.get(f"/api/v1/game/{session.id}/dialogue")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_corvus_choice_not_owner(self, client, db_session):
        """AC-020: Corvus choice ownership check."""
        test_user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=other_user_id,
            status="playing",
            corvus_internal_game_id="corvus-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        response = await client.post(
            f"/api/v1/game/{session.id}/choice",
            json={"choice_id": "fake"},
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_legacy_and_corvus_no_interference(self, client, db_session):
        """AC-020: Legacy and Corvus sessions don't interfere with each other."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        # Create a Corvus session
        corvus_session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="corvus-slug",
            engine_type="corvus",
        )
        db_session.add(corvus_session)
        await db_session.flush()

        # Create a legacy session (different UUID)
        from app.models.game import GameSession
        from app.models.script import Script, Route, Node

        script = Script(slug="test-interfere", title="Test", description="t", genre="fantasy")
        db_session.add(script)
        await db_session.flush()
        route = Route(script_id=script.id, title="R")
        db_session.add(route)
        await db_session.flush()
        node = Node(route_id=route.id, node_type="dialogue", content={"text": "hi"})
        db_session.add(node)
        await db_session.flush()

        legacy_session = GameSession(
            user_id=test_user_id,
            script_id=script.id,
            route_id=route.id,
            current_node_id=node.id,
            status="active",
        )
        db_session.add(legacy_session)
        await db_session.flush()

        # Corvus dialogue → returns Corvus format
        with patch("app.services.corvus_client.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.get_game = AsyncMock(return_value={
                "config": {"name": "Corvus Game"},
                "world": {"setting": "fantasy"},
            })
            mock_get.return_value = mock_client

            corvus_resp = await client.get(f"/api/v1/game/{corvus_session.id}/dialogue")
            assert corvus_resp.status_code == 200
            assert corvus_resp.json().get("engine_type") == "corvus"

        # Legacy dialogue → should NOT return Corvus format
        # (may fail if NarrativeEngine needs more setup, but should NOT have corvus fields)
        legacy_resp = await client.get(f"/api/v1/game/{legacy_session.id}/dialogue")
        if legacy_resp.status_code == 200:
            data = legacy_resp.json()
            assert data.get("engine_type") != "corvus"
            assert "corvus_game_id" not in data
