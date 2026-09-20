"""Integration tests for Legacy SSE event format validation.

CR-042 DEV-001 AC-003

AC-003: SSE event format matches Corvus path:
  data: {"type":"text","content":"..."}\n\n
  data: {"type":"done",...}\n\n
  data: {"type":"error","message":"..."}\n\n
"""

import pytest
import pytest_asyncio
import json
import uuid
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token
from app.models.user import User
from app.models.script import Script, Route, Node, NodeChoice, Character
from app.models.game import GameSession
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

try:
    from pgvector.sqlalchemy import Vector
    from sqlalchemy.ext.compiler import compiles
    @compiles(Vector, "sqlite")
    def _v(t, c, **kw): return "TEXT"
except ImportError:
    pass

try:
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy.ext.compiler import compiles
    @compiles(JSONB, "sqlite")
    def _j(t, c, **kw): return "TEXT"
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
    script = Script(id=uuid.uuid4(), title="Test", slug="test", genre="fantasy")
    db_session.add(script)
    route = Route(id=uuid.uuid4(), script_id=script.id, title="Route")
    db_session.add(route)
    character = Character(
        id=uuid.uuid4(), script_id=script.id, name="Aria",
        personality={"traits": ["kind"]}, is_main=True,
    )
    db_session.add(character)
    node = Node(
        id=uuid.uuid4(), route_id=route.id, node_type="transition",
        content={"text": "Hello", "context": "Scene"},
    )
    db_session.add(node)
    choice = NodeChoice(id=uuid.uuid4(), node_id=node.id, text="Go", next_node_id=node.id)
    db_session.add(choice)
    session = GameSession(
        id=uuid.uuid4(), user_id=test_user.id, script_id=script.id,
        route_id=route.id, current_node_id=node.id, status="active",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return {"script": script, "route": route, "character": character, "node": node,
            "choice": choice, "session": session}


class TestSSEEventFormat:
    """AC-003: SSE event format validation"""

    def _parse_sse_events(self, body: str) -> list:
        """Parse SSE body into event dicts."""
        events = []
        for line in body.split('\n'):
            if line.startswith('data: '):
                try:
                    events.append(json.loads(line[6:]))
                except json.JSONDecodeError:
                    pass
        return events

    @pytest.mark.asyncio
    async def test_text_event_has_content_field(self, client, auth_token, legacy_game_setup):
        """AC-003: text event has type and content fields."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"choice_id": str(setup["choice"].id)}

        async def mock_stream_dialogue(*args, **kwargs):
            yield "Hello"
            yield " world"

        with patch("app.api.v1.game.NarrativeEngine") as MockEngine:
            MockEngine.return_value.process_choice = AsyncMock(return_value={
                "next_node_id": str(setup["node"].id),
                "choice_text": "Go",
                "affection_change": {"character_id": str(setup["character"].id), "value": 3},
            })

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
                            json=payload, headers=headers,
                        )

        events = self._parse_sse_events(response.text)
        text_events = [e for e in events if e.get("type") == "text"]
        assert len(text_events) >= 2
        for e in text_events:
            assert "content" in e
            assert isinstance(e["content"], str)

    @pytest.mark.asyncio
    async def test_done_event_format(self, client, auth_token, legacy_game_setup):
        """AC-003: done event has type=done, session_id, node_id."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"choice_id": str(setup["choice"].id)}

        async def mock_stream_dialogue(*args, **kwargs):
            yield "text"

        with patch("app.api.v1.game.NarrativeEngine") as MockEngine:
            MockEngine.return_value.process_choice = AsyncMock(return_value={
                "next_node_id": str(setup["node"].id),
                "choice_text": "Go",
            })

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
                            json=payload, headers=headers,
                        )

        events = self._parse_sse_events(response.text)
        done_events = [e for e in events if e.get("type") == "done"]
        assert len(done_events) >= 1
        done = done_events[-1]
        assert done["type"] == "done"
        assert "session_id" in done
        assert "node_id" in done

    @pytest.mark.asyncio
    async def test_error_event_format(self, client, auth_token, legacy_game_setup):
        """AC-003: error event has type=error and message field."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"choice_id": str(setup["choice"].id)}

        async def mock_stream_dialogue(*args, **kwargs):
            raise ValueError("Test error")
            yield

        with patch("app.api.v1.game.NarrativeEngine") as MockEngine:
            MockEngine.return_value.process_choice = AsyncMock(return_value={
                "next_node_id": str(setup["node"].id),
                "choice_text": "Go",
            })

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
                            json=payload, headers=headers,
                        )

        events = self._parse_sse_events(response.text)
        error_events = [e for e in events if e.get("type") == "error"]
        assert len(error_events) >= 1
        assert "message" in error_events[-1]

    @pytest.mark.asyncio
    async def test_sse_events_use_data_prefix(self, client, auth_token, legacy_game_setup):
        """AC-003: SSE lines use 'data: ' prefix."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"choice_id": str(setup["choice"].id)}

        async def mock_stream_dialogue(*args, **kwargs):
            yield "test"

        with patch("app.api.v1.game.NarrativeEngine") as MockEngine:
            MockEngine.return_value.process_choice = AsyncMock(return_value={
                "next_node_id": str(setup["node"].id),
                "choice_text": "Go",
            })

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
                            json=payload, headers=headers,
                        )

        body = response.text
        for line in body.strip().split('\n'):
            if line.strip():
                assert line.startswith('data: ')
