"""Unit tests for CR-037 DEV-003: CorvusClient + select-player API.

Test Case Artifacts:
- TC-API-002: select-player API + Corvus create_game integration
- TC-API-003: switch character creates new session + memory isolation

Covers AC-007, AC-008, AC-025.

Uses SQLite in-memory DB with conftest.py fixtures.
CorvusClient is mocked to avoid real HTTP calls in unit tests.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.corvus import PlayerCandidate, CorvusGameSession
from app.api.v1.auth import get_current_user_id
from app.main import app
from app.core.exceptions import AppException


# ── TC-API-002: select-player API + Corvus create_game ──────────────────


class TestTCAPI002SelectPlayerAndCorvusCreate:
    """TC-API-002: Test select-player endpoint and Corvus integration."""

    @pytest.mark.asyncio
    async def test_select_player_success(self, client, db_session):
        """AC-007: POST /api/v1/game/session/select-player returns status=playing + corvus_game_id."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        # Create a game session in waiting_select_player status
        session = CorvusGameSession(
            user_id=test_user_id,
            status="waiting_select_player",
            engine_type="corvus",
        )
        db_session.add(session)

        # Create a player candidate
        candidate = PlayerCandidate(
            user_id=test_user_id,
            name="白夜",
            personality="神秘的占星师",
            backstory="天文台的实习生",
            appearance="黑色斗篷",
            initial_inventory=[{"item": "塔罗牌"}],
        )
        db_session.add(candidate)
        await db_session.flush()

        # Mock CorvusClient.create_game to return a fake slug
        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.create_game = AsyncMock(return_value="test-game-slug-123")
            mock_get_client.return_value = mock_client

            response = await client.post(
                "/api/v1/game/session/select-player",
                json={
                    "game_session_id": str(session.id),
                    "player_candidate_id": str(candidate.id),
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["status"] == "playing"
        assert data["data"]["corvus_game_id"] == "test-game-slug-123"
        assert data["data"]["player"]["name"] == "白夜"

    @pytest.mark.asyncio
    async def test_select_player_updates_db_status(self, client, db_session):
        """AC-007: After select-player, DB session status=playing, corvus_internal_game_id non-empty."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=test_user_id,
            status="waiting_select_player",
        )
        db_session.add(session)

        candidate = PlayerCandidate(
            user_id=test_user_id,
            name="沈星澜",
        )
        db_session.add(candidate)
        await db_session.flush()

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.create_game = AsyncMock(return_value="corvus-slug-456")
            mock_get_client.return_value = mock_client

            response = await client.post(
                "/api/v1/game/session/select-player",
                json={
                    "game_session_id": str(session.id),
                    "player_candidate_id": str(candidate.id),
                },
            )

        assert response.status_code == 200

        # Verify DB state via ORM query
        from tests.conftest import TestSessionLocal
        async with TestSessionLocal() as db:
            from sqlalchemy import select
            stmt = select(CorvusGameSession).where(
                CorvusGameSession.id == session.id
            )
            result = await db.execute(stmt)
            updated = result.scalar_one_or_none()
            assert updated is not None
            assert updated.status == "playing"
            assert updated.corvus_internal_game_id == "corvus-slug-456"
            assert updated.selected_player_candidate_id == candidate.id

    @pytest.mark.asyncio
    async def test_select_player_only_selected_candidate_sent(self, client, db_session):
        """AC-007: Only the selected candidate is sent to Corvus (not the other two)."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=test_user_id,
            status="waiting_select_player",
        )
        db_session.add(session)

        # Create 3 candidates
        candidates = []
        for name in ["白夜", "沈星澜", "藤原雪"]:
            c = PlayerCandidate(user_id=test_user_id, name=name)
            db_session.add(c)
            candidates.append(c)
        await db_session.flush()

        selected = candidates[1]  # Select 沈星澜

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.create_game = AsyncMock(return_value="corvus-slug-789")
            mock_get_client.return_value = mock_client

            response = await client.post(
                "/api/v1/game/session/select-player",
                json={
                    "game_session_id": str(session.id),
                    "player_candidate_id": str(selected.id),
                },
            )

        assert response.status_code == 200

        # Verify CorvusClient.create_game was called with ONLY the selected candidate
        call_args = mock_client.create_game.call_args
        assert call_args.kwargs["player_name"] == "沈星澜"
        # Verify other candidates were NOT sent
        # The create_game call should only contain the selected candidate's data
        assert "白夜" not in str(call_args.kwargs)
        assert "藤原雪" not in str(call_args.kwargs)

    @pytest.mark.asyncio
    async def test_select_player_wrong_status(self, client, db_session):
        """AC-007: Cannot select player if session status is not waiting_select_player."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",  # Already playing
        )
        db_session.add(session)

        candidate = PlayerCandidate(
            user_id=test_user_id,
            name="白夜",
        )
        db_session.add(candidate)
        await db_session.flush()

        with patch("app.services.corvus_adapter.get_corvus_client"):
            response = await client.post(
                "/api/v1/game/session/select-player",
                json={
                    "game_session_id": str(session.id),
                    "player_candidate_id": str(candidate.id),
                },
            )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_select_player_not_owner(self, client, db_session):
        """AC-007: Cannot select player for session owned by another user."""
        test_user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        # Session owned by another user
        session = CorvusGameSession(
            user_id=other_user_id,
            status="waiting_select_player",
        )
        db_session.add(session)

        candidate = PlayerCandidate(
            user_id=test_user_id,
            name="白夜",
        )
        db_session.add(candidate)
        await db_session.flush()

        response = await client.post(
            "/api/v1/game/session/select-player",
            json={
                "game_session_id": str(session.id),
                "player_candidate_id": str(candidate.id),
            },
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_select_player_session_not_found(self, client, db_session):
        """AC-007: 404 if game session does not exist."""
        test_user_id = str(uuid.uuid4())
        app.dependency_overrides[get_current_user_id] = lambda: test_user_id

        fake_session_id = str(uuid.uuid4())
        fake_candidate_id = str(uuid.uuid4())

        response = await client.post(
            "/api/v1/game/session/select-player",
            json={
                "game_session_id": fake_session_id,
                "player_candidate_id": fake_candidate_id,
            },
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_select_player_candidate_not_found(self, client, db_session):
        """AC-007: 404 if player candidate does not exist."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        session = CorvusGameSession(
            user_id=test_user_id,
            status="waiting_select_player",
        )
        db_session.add(session)
        await db_session.flush()

        fake_candidate_id = str(uuid.uuid4())

        response = await client.post(
            "/api/v1/game/session/select-player",
            json={
                "game_session_id": str(session.id),
                "player_candidate_id": fake_candidate_id,
            },
        )

        assert response.status_code == 404


# ── TC-API-003: switch character creates new session + memory isolation ──


class TestTCAPI003SwitchCharacterAndMemoryIsolation:
    """TC-API-003: Test that switching characters creates a new session."""

    @pytest.mark.asyncio
    async def test_switch_character_creates_new_session(self, client, db_session):
        """AC-008: Switching character must create a new game_session_id."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        # Create first session with selected player
        session1 = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="old-game-slug",
        )
        db_session.add(session1)

        candidate1 = PlayerCandidate(user_id=test_user_id, name="白夜")
        candidate2 = PlayerCandidate(user_id=test_user_id, name="沈星澜")
        db_session.add(candidate1)
        db_session.add(candidate2)
        await db_session.flush()

        session1.selected_player_candidate_id = candidate1.id
        await db_session.flush()

        # Create a NEW session (simulating POST /session/create again)
        new_session = CorvusGameSession(
            user_id=test_user_id,
            status="waiting_select_player",
        )
        db_session.add(new_session)
        await db_session.flush()
        new_session_id = new_session.id

        # Select different candidate on the new session
        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.create_game = AsyncMock(return_value="new-game-slug")
            mock_get_client.return_value = mock_client

            response = await client.post(
                "/api/v1/game/session/select-player",
                json={
                    "game_session_id": str(new_session_id),
                    "player_candidate_id": str(candidate2.id),
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "playing"
        assert data["data"]["corvus_game_id"] == "new-game-slug"

        # Verify via TestSessionLocal (same factory as override_get_db)
        from tests.conftest import TestSessionLocal
        async with TestSessionLocal() as db:
            from sqlalchemy import select
            # Old session unchanged
            stmt_old = select(CorvusGameSession).where(
                CorvusGameSession.id == session1.id
            )
            result_old = await db.execute(stmt_old)
            old = result_old.scalar_one_or_none()
            assert old is not None
            assert old.status == "playing"
            assert old.corvus_internal_game_id == "old-game-slug"
            assert old.selected_player_candidate_id == candidate1.id

            # New session has different corvus_internal_game_id
            stmt_new = select(CorvusGameSession).where(
                CorvusGameSession.id == new_session_id
            )
            result_new = await db.execute(stmt_new)
            new_sess = result_new.scalar_one_or_none()
            assert new_sess is not None
            assert new_sess.corvus_internal_game_id == "new-game-slug"
            assert new_sess.corvus_internal_game_id != old.corvus_internal_game_id

    @pytest.mark.asyncio
    async def test_old_session_unchanged_after_switch(self, client, db_session):
        """AC-008: Old session's selected_player_candidate_id is not changed."""
        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        candidate1 = PlayerCandidate(user_id=test_user_id, name="白夜")
        candidate2 = PlayerCandidate(user_id=test_user_id, name="沈星澜")
        db_session.add(candidate1)
        db_session.add(candidate2)

        old_session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="old-slug",
        )
        db_session.add(old_session)
        await db_session.flush()
        # Set FK after flush to ensure candidate1.id exists in DB
        old_session.selected_player_candidate_id = candidate1.id
        await db_session.flush()
        await db_session.refresh(old_session)

        new_session = CorvusGameSession(
            user_id=test_user_id,
            status="waiting_select_player",
        )
        db_session.add(new_session)
        await db_session.flush()
        await db_session.refresh(new_session)
        old_session_id = old_session.id
        new_session_id = new_session.id
        candidate1_id = candidate1.id
        candidate2_id = candidate2.id

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.create_game = AsyncMock(return_value="new-slug")
            mock_get_client.return_value = mock_client

            await client.post(
                "/api/v1/game/session/select-player",
                json={
                    "game_session_id": str(new_session_id),
                    "player_candidate_id": str(candidate2.id),
                },
            )

        # Verify via TestSessionLocal
        from tests.conftest import TestSessionLocal
        async with TestSessionLocal() as db:
            from sqlalchemy import select
            # Old session unchanged
            stmt_old = select(CorvusGameSession).where(
                CorvusGameSession.id == old_session_id
            )
            result_old = await db.execute(stmt_old)
            old = result_old.scalar_one_or_none()
            assert old is not None
            assert old.selected_player_candidate_id == candidate1_id
            assert old.corvus_internal_game_id == "old-slug"

            # New session has candidate2
            stmt_new = select(CorvusGameSession).where(
                CorvusGameSession.id == new_session_id
            )
            result_new = await db.execute(stmt_new)
            new_sess = result_new.scalar_one_or_none()
            assert new_sess is not None
            assert new_sess.selected_player_candidate_id == candidate2_id
            assert new_sess.corvus_internal_game_id == "new-slug"


# ── CorvusClient unit tests (AC-025) ─────────────────────────────────────


class TestCorvusClient:
    """AC-025: CorvusClient API calls (mocked HTTP)."""

    @pytest.mark.asyncio
    async def test_create_game_returns_slug(self):
        """AC-025: CorvusClient.create_game returns a slug-format game_id."""
        from app.services.corvus_client import CorvusClient

        client = CorvusClient()
        # Mock httpx.AsyncClient
        with patch.object(client, "_get_client") as mock_get:
            mock_http = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json = MagicMock(return_value={"id": "dark-fantasy-abc123"})
            mock_http.post = AsyncMock(return_value=mock_resp)
            mock_get.return_value = mock_http

            result = await client.create_game(
                player_name="白夜",
                backstory="占星师",
                appearance="黑色斗篷",
            )

        assert result == "dark-fantasy-abc123"
        # Verify POST was called with correct player data
        call_args = mock_http.post.call_args
        body = call_args.kwargs["json"]
        assert body["player"]["name"] == "白夜"
        assert body["player"]["backstory"] == "占星师"

    @pytest.mark.asyncio
    async def test_get_game_returns_dict(self):
        """AC-025: CorvusClient.get_game returns game state dict."""
        from app.services.corvus_client import CorvusClient

        client = CorvusClient()
        with patch.object(client, "_get_client") as mock_get:
            mock_http = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json = MagicMock(return_value={
                "config": {"id": "test-game", "name": "Test"},
                "world": {"setting": "fantasy"},
            })
            mock_http.get = AsyncMock(return_value=mock_resp)
            mock_get.return_value = mock_http

            result = await client.get_game("test-game")

        assert isinstance(result, dict)
        assert result["config"]["id"] == "test-game"

    @pytest.mark.asyncio
    async def test_get_characters_returns_list(self):
        """AC-025: CorvusClient.get_characters returns NPC list."""
        from app.services.corvus_client import CorvusClient

        client = CorvusClient()
        with patch.object(client, "_get_client") as mock_get:
            mock_http = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json = MagicMock(return_value=[
                {"id": "npc1", "name": "NPC1"},
                {"id": "npc2", "name": "NPC2"},
            ])
            mock_http.get = AsyncMock(return_value=mock_resp)
            mock_get.return_value = mock_http

            result = await client.get_characters("test-game")

        assert isinstance(result, list)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_stream_message_is_async_generator(self):
        """AC-025: stream_message is an async generator (implemented in DEV-004)."""
        from app.services.corvus_client import CorvusClient

        client = CorvusClient()
        # stream_message is an async generator (async def with yield)
        # Calling it returns an async generator object, not a coroutine
        gen = client.stream_message("test", "hello")
        # Verify it's an async generator by checking __aiter__
        assert hasattr(gen, '__aiter__')
        assert hasattr(gen, '__anext__')

    @pytest.mark.asyncio
    async def test_corvus_base_url_is_localhost(self):
        """AC-025: CorvusClient base URL is 127.0.0.1:8082 (never public)."""
        from app.services.corvus_client import CORVUS_BASE_URL

        assert "127.0.0.1" in CORVUS_BASE_URL
        assert "8082" in CORVUS_BASE_URL


# ── CorvusAdapter unit tests ──────────────────────────────────────────────


class TestCorvusAdapterCreateSession:
    """Unit tests for CorvusAdapter.create_session logic."""

    @pytest.mark.asyncio
    async def test_create_session_success(self, db_session: AsyncSession):
        """AC-007: CorvusAdapter.create_session creates Corvus game and updates session."""
        from app.services.corvus_adapter import CorvusAdapter

        test_user_id = uuid.uuid4()

        session = CorvusGameSession(
            user_id=test_user_id,
            status="waiting_select_player",
        )
        db_session.add(session)

        candidate = PlayerCandidate(
            user_id=test_user_id,
            name="藤原雪",
            backstory="文学教授",
            appearance="温和儒雅",
        )
        db_session.add(candidate)
        await db_session.flush()

        # Mock CorvusClient
        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.create_game = AsyncMock(return_value="corvus-slug-success")
            mock_get.return_value = mock_client

            adapter = CorvusAdapter(db_session)
            result = await adapter.create_session(
                user_id=test_user_id,
                game_session_id=session.id,
                player_candidate_id=candidate.id,
            )

        assert result["status"] == "playing"
        assert result["corvus_game_id"] == "corvus-slug-success"
        assert result["player"]["name"] == "藤原雪"
        assert session.status == "playing"
        assert session.corvus_internal_game_id == "corvus-slug-success"

    @pytest.mark.asyncio
    async def test_create_session_corvus_failure(self, db_session: AsyncSession):
        """AC-007: If Corvus API fails, session stays in waiting_select_player."""
        from app.services.corvus_adapter import CorvusAdapter

        test_user_id = uuid.uuid4()

        session = CorvusGameSession(
            user_id=test_user_id,
            status="waiting_select_player",
        )
        db_session.add(session)

        candidate = PlayerCandidate(
            user_id=test_user_id,
            name="白夜",
        )
        db_session.add(candidate)
        await db_session.flush()

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.create_game = AsyncMock(side_effect=Exception("Connection refused"))
            mock_get.return_value = mock_client

            adapter = CorvusAdapter(db_session)
            with pytest.raises(AppException) as exc_info:
                await adapter.create_session(
                    user_id=test_user_id,
                    game_session_id=session.id,
                    player_candidate_id=candidate.id,
                )

            assert exc_info.value.status_code == 503
            # Session should NOT have been updated
            assert session.status == "waiting_select_player"
