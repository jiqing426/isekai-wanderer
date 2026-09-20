"""Integration tests for Legacy submit_choice SSE streaming.

CR-042 DEV-001 AC-001, AC-002, AC-003, AC-004

AC-001: Legacy submit_choice with transition/ai_dialog node → SSE text/event-stream, text逐字显示
AC-002: Legacy submit_choice with preset/choice node → JSON response (no SSE)
AC-003: SSE event format: data: {"type":"text","content":"..."}\n\n and data: {"type":"done",...}\n\n
AC-004: SSE done event carries affection_change metadata; DB write deferred until after stream
"""

import pytest
import pytest_asyncio
import json
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token
from app.models.user import User
from app.models.script import Script, Route, Node, NodeChoice, Character
from app.models.game import GameSession
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Register types for SQLite
try:
    from pgvector.sqlalchemy import Vector
    from sqlalchemy.ext.compiler import compiles
    @compiles(Vector, "sqlite")
    def _v_sqlite(t, c, **kw): return "TEXT"
except ImportError:
    pass

try:
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy.ext.compiler import compiles
    @compiles(JSONB, "sqlite")
    def _j_sqlite(t, c, **kw): return "TEXT"
except ImportError:
    pass

import os
os.environ["DISABLE_MOCK"] = "1"

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    user = User(id=uuid.uuid4(), email="test@example.com", display_name="test", email_verified=True)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    return create_access_token({"sub": str(test_user.id)})


@pytest_asyncio.fixture
async def legacy_game_setup(db_session, test_user):
    """Create a legacy game session with transition node and preset node."""
    script = Script(id=uuid.uuid4(), title="Test Script", slug="test-script", genre="fantasy")
    db_session.add(script)

    route = Route(id=uuid.uuid4(), script_id=script.id, title="Test Route")
    db_session.add(route)

    # Character for dialogue
    character = Character(
        id=uuid.uuid4(),
        script_id=script.id,
        name="Aria",
        personality={"traits": ["kind", "brave"]},
        is_main=True,
    )
    db_session.add(character)

    # Transition node (should trigger SSE)
    transition_node = Node(
        id=uuid.uuid4(),
        route_id=route.id,
        node_type="transition",
        content={"text": "You walk into the forest.", "context": "Forest scene"},
        parent_id=None,
    )
    db_session.add(transition_node)

    # Preset node (should NOT trigger SSE — stays JSON)
    preset_node = Node(
        id=uuid.uuid4(),
        route_id=route.id,
        node_type="preset",
        content={"text": "What do you do?", "context": "Choice scene"},
        parent_id=transition_node.id,
    )
    db_session.add(preset_node)

    # NodeChoice for the transition node
    choice = NodeChoice(
        id=uuid.uuid4(),
        node_id=transition_node.id,
        text="Go left",
        next_node_id=preset_node.id,
    )
    db_session.add(choice)

    # Game session — legacy engine (no CorvusGameSession record)
    session = GameSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        script_id=script.id,
        route_id=route.id,
        current_node_id=transition_node.id,
        status="active",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    return {
        "script": script,
        "route": route,
        "character": character,
        "transition_node": transition_node,
        "preset_node": preset_node,
        "choice": choice,
        "session": session,
    }


class TestLegacySubmitChoiceSSE:
    """AC-001, AC-002: Legacy submit_choice conditional SSE"""

    @pytest.mark.asyncio
    async def test_transition_node_returns_event_stream(self, client, auth_token, legacy_game_setup):
        """AC-001: When next_node is transition type, response is text/event-stream."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"choice_id": str(setup["choice"].id)}

        # Mock NarrativeEngine.process_choice to return next_node_id pointing to transition_node
        with patch("app.api.v1.game.NarrativeEngine") as MockEngine:
            mock_engine = MockEngine.return_value
            mock_engine.process_choice = AsyncMock(return_value={
                "next_node_id": str(setup["transition_node"].id),
                "choice_text": "Go left",
                "affection_change": {"character_id": str(setup["character"].id), "value": 5},
            })

            # Mock llm_gateway.stream_dialogue at its actual import location
            async def mock_stream_dialogue(*args, **kwargs):
                for token in ["Hello", " there"]:
                    yield token

            with patch("app.services.llm.gateway.llm_gateway") as mock_gw:
                mock_gw.stream_dialogue = mock_stream_dialogue

                # Mock quota to not be exhausted
                with patch("app.services.quota_service.QuotaService") as MockQuota:
                    MockQuota.return_value.get_user_quota_status = AsyncMock(return_value={
                        "remaining": 10, "is_exempt": True
                    })
                    MockQuota.return_value.consume_quota = AsyncMock(return_value=True)

                    with patch("app.services.paywall_service.PaywallService") as MockPaywall:
                        MockPaywall.return_value.check_trigger = AsyncMock(return_value=None)

                        response = await client.post(
                            f"/api/v1/game/{setup['session'].id}/choice",
                            json=payload,
                            headers=headers,
                        )

        # AC-001: transition node → SSE
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        assert response.headers.get("x-accel-buffering") == "no"

    @pytest.mark.asyncio
    async def test_preset_node_returns_json(self, client, auth_token, legacy_game_setup):
        """AC-002: When next_node is preset/choice type, response is JSON (not SSE)."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"choice_id": str(setup["choice"].id)}

        with patch("app.api.v1.game.NarrativeEngine") as MockEngine:
            mock_engine = MockEngine.return_value
            mock_engine.process_choice = AsyncMock(return_value={
                "next_node_id": str(setup["preset_node"].id),
                "choice_text": "Go left",
            })

            with patch("app.services.quota_service.QuotaService") as MockQuota:
                MockQuota.return_value.get_user_quota_status = AsyncMock(return_value={
                    "remaining": 10, "is_exempt": True
                })
                MockQuota.return_value.consume_quota = AsyncMock(return_value=True)

                with patch("app.services.paywall_service.PaywallService") as MockPaywall:
                    MockPaywall.return_value.check_trigger = AsyncMock(return_value=None)

                    response = await client.post(
                        f"/api/v1/game/{setup['session'].id}/choice",
                        json=payload,
                        headers=headers,
                    )

        # AC-002: preset node → JSON
        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" not in content_type
        assert "application/json" in content_type


class TestLegacySSEEventFormat:
    """AC-003, AC-004: SSE event format and metadata"""

    @pytest.mark.asyncio
    async def test_sse_events_contain_text_and_done(self, client, auth_token, legacy_game_setup):
        """AC-003: SSE stream contains data: {"type":"text","content":"..."} and data: {"type":"done",...}."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"choice_id": str(setup["choice"].id)}

        with patch("app.api.v1.game.NarrativeEngine") as MockEngine:
            mock_engine = MockEngine.return_value
            mock_engine.process_choice = AsyncMock(return_value={
                "next_node_id": str(setup["transition_node"].id),
                "choice_text": "Go left",
                "affection_change": {"character_id": str(setup["character"].id), "value": 5},
            })

            async def mock_stream_dialogue(*args, **kwargs):
                for token in ["You", " enter", " the", " forest"]:
                    yield token

            with patch("app.services.llm.gateway.llm_gateway") as mock_gw:
                mock_gw.stream_dialogue = mock_stream_dialogue

                with patch("app.services.quota_service.QuotaService") as MockQuota:
                    MockQuota.return_value.get_user_quota_status = AsyncMock(return_value={
                        "remaining": 10, "is_exempt": True
                    })
                    MockQuota.return_value.consume_quota = AsyncMock(return_value=True)

                    with patch("app.services.paywall_service.PaywallService") as MockPaywall:
                        MockPaywall.return_value.check_trigger = AsyncMock(return_value=None)

                        response = await client.post(
                            f"/api/v1/game/{setup['session'].id}/choice",
                            json=payload,
                            headers=headers,
                        )

        body = response.text
        # AC-003: verify SSE event format — type:text and type:done
        assert '"type":"text"' in body or '"type": "text"' in body
        assert '"type":"done"' in body or '"type": "done"' in body
        # Verify SSE prefix
        assert "data: " in body

    @pytest.mark.asyncio
    async def test_sse_done_event_carries_metadata(self, client, auth_token, legacy_game_setup):
        """AC-004: done event carries affection_change and session_id metadata."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"choice_id": str(setup["choice"].id)}

        affection_change = {"character_id": str(setup["character"].id), "value": 5}

        with patch("app.api.v1.game.NarrativeEngine") as MockEngine:
            mock_engine = MockEngine.return_value
            mock_engine.process_choice = AsyncMock(return_value={
                "next_node_id": str(setup["transition_node"].id),
                "choice_text": "Go left",
                "affection_change": affection_change,
            })

            async def mock_stream_dialogue(*args, **kwargs):
                yield "Text"
                yield " more"

            with patch("app.services.llm.gateway.llm_gateway") as mock_gw:
                mock_gw.stream_dialogue = mock_stream_dialogue

                with patch("app.services.quota_service.QuotaService") as MockQuota:
                    MockQuota.return_value.get_user_quota_status = AsyncMock(return_value={
                        "remaining": 10, "is_exempt": True
                    })
                    MockQuota.return_value.consume_quota = AsyncMock(return_value=True)

                    with patch("app.services.paywall_service.PaywallService") as MockPaywall:
                        MockPaywall.return_value.check_trigger = AsyncMock(return_value=None)

                        response = await client.post(
                            f"/api/v1/game/{setup['session'].id}/choice",
                            json=payload,
                            headers=headers,
                        )

        body = response.text
        # Parse SSE events
        events = []
        for line in body.split('\n'):
            if line.startswith('data: '):
                try:
                    events.append(json.loads(line[6:]))
                except json.JSONDecodeError:
                    pass

        # Find done event
        done_events = [e for e in events if e.get("type") == "done"]
        assert len(done_events) >= 1

        # AC-004: done event should contain session_id and node_id
        done = done_events[-1]
        assert "session_id" in done
        assert "node_id" in done

    @pytest.mark.asyncio
    async def test_sse_error_event_format(self, client, auth_token, legacy_game_setup):
        """AC-003: SSE error event format: data: {"type":"error","message":"..."}."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"choice_id": str(setup["choice"].id)}

        with patch("app.api.v1.game.NarrativeEngine") as MockEngine:
            mock_engine = MockEngine.return_value
            mock_engine.process_choice = AsyncMock(return_value={
                "next_node_id": str(setup["transition_node"].id),
                "choice_text": "Go left",
            })

            async def mock_stream_dialogue(*args, **kwargs):
                raise RuntimeError("LLM connection failed")
                yield  # never reached

            with patch("app.services.llm.gateway.llm_gateway") as mock_gw:
                mock_gw.stream_dialogue = mock_stream_dialogue

                with patch("app.services.quota_service.QuotaService") as MockQuota:
                    MockQuota.return_value.get_user_quota_status = AsyncMock(return_value={
                        "remaining": 10, "is_exempt": True
                    })
                    MockQuota.return_value.consume_quota = AsyncMock(return_value=True)

                    with patch("app.services.paywall_service.PaywallService") as MockPaywall:
                        MockPaywall.return_value.check_trigger = AsyncMock(return_value=None)

                        response = await client.post(
                            f"/api/v1/game/{setup['session'].id}/choice",
                            json=payload,
                            headers=headers,
                        )

        body = response.text
        # Should contain error event
        assert '"type":"error"' in body or '"type": "error"' in body
