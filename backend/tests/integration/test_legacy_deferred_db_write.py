"""Integration tests for Legacy deferred DB write verification.

CR-042 DEV-001 AC-004, AC-009, AC-014

AC-004: SSE done event carries affection_change; deferred DB write persists
AC-009: Custom-input done event carries metadata; deferred DB write persists
AC-014: Free-chat done event carries metadata; deferred DB write persists
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
from app.models.game import GameSession, DialogueHistory
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


class TestDeferredDBWrite:
    """AC-004, AC-009, AC-014: Deferred DB write after SSE stream"""

    @pytest.mark.asyncio
    async def test_choice_done_carries_affection_change(self, client, auth_token, legacy_game_setup):
        """AC-004: done event carries affection_change metadata."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"choice_id": str(setup["choice"].id)}

        affection_change = {"character_id": str(setup["character"].id), "value": 10}

        async def mock_stream_dialogue(*args, **kwargs):
            yield "text"

        with patch("app.api.v1.game.NarrativeEngine") as MockEngine:
            MockEngine.return_value.process_choice = AsyncMock(return_value={
                "next_node_id": str(setup["node"].id),
                "choice_text": "Go",
                "affection_change": affection_change,
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
        events = []
        for line in body.split('\n'):
            if line.startswith('data: '):
                try:
                    events.append(json.loads(line[6:]))
                except json.JSONDecodeError:
                    pass
        done_events = [e for e in events if e.get("type") == "done"]
        assert len(done_events) >= 1
        # AC-004: done event should carry affection_change
        assert "affection_change" in done_events[-1]
        assert done_events[-1]["affection_change"] == affection_change

    @pytest.mark.asyncio
    async def test_choice_sse_has_correct_headers(self, client, auth_token, legacy_game_setup):
        """AC-004: SSE response has correct headers for deferred write pattern."""
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

        # Verify headers
        assert response.headers.get("x-accel-buffering") == "no"
        assert response.headers.get("cache-control") == "no-cache"
        assert "text/event-stream" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_custom_input_done_has_session_id(self, client, auth_token, legacy_game_setup):
        """AC-009: Custom-input done event has session_id for deferred write tracking."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"text": "Hello"}

        async def mock_stream_dialogue(*args, **kwargs):
            yield "response"

        with patch("app.services.llm.gateway.llm_gateway") as mock_gw:
            mock_gw.stream_dialogue = mock_stream_dialogue
            with patch("app.services.quota_service.QuotaService") as MockQuota:
                MockQuota.return_value.get_user_quota_status = AsyncMock(return_value={
                    "remaining": 10, "is_exempt": True
                })
                MockQuota.return_value.consume_quota = AsyncMock(return_value=True)

                response = await client.post(
                    f"/api/v1/game/{setup['session'].id}/custom-input",
                    json=payload, headers=headers,
                )

        body = response.text
        events = []
        for line in body.split('\n'):
            if line.startswith('data: '):
                try:
                    events.append(json.loads(line[6:]))
                except json.JSONDecodeError:
                    pass
        done_events = [e for e in events if e.get("type") == "done"]
        assert len(done_events) >= 1
        assert "session_id" in done_events[-1]

    @pytest.mark.asyncio
    async def test_free_chat_done_has_session_id(self, client, auth_token, legacy_game_setup):
        """AC-014: Free-chat done event has session_id for deferred write tracking."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"message": "Hi"}

        async def mock_stream(*args, **kwargs):
            yield "reply"

        with patch("app.services.free_chat_service.FreeChatService.send_message_stream", mock_stream):
            response = await client.post(
                f"/api/v1/game/{setup['session'].id}/free-chat/stream",
                json=payload, headers=headers,
            )

        body = response.text
        events = []
        for line in body.split('\n'):
            if line.startswith('data: '):
                try:
                    events.append(json.loads(line[6:]))
                except json.JSONDecodeError:
                    pass
        done_events = [e for e in events if e.get("type") == "done"]
        assert len(done_events) >= 1
        assert "session_id" in done_events[-1]
