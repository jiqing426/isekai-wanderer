"""Integration tests for free-chat/stream endpoint and deprecation header.

CR-042 DEV-001 AC-011, AC-013, AC-014, AC-015

AC-011: POST /game/{id}/free-chat/stream returns text/event-stream + X-Accel-Buffering: no
AC-013: SSE逐字输出角色回复
AC-014: done event carries metadata; deferred DB write
AC-015: Old POST /game/{id}/free-chat returns JSON 200 + Deprecation header
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
from app.models.script import Script, Route, Node, Character
from app.models.game import GameSession
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

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
        id=uuid.uuid4(), route_id=route.id, node_type="dialogue",
        content={"text": "Hello"},
    )
    db_session.add(node)
    session = GameSession(
        id=uuid.uuid4(), user_id=test_user.id, script_id=script.id,
        route_id=route.id, current_node_id=node.id, status="active",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return {"script": script, "route": route, "character": character, "node": node, "session": session}


class TestFreeChatStreamEndpoint:
    """AC-011, AC-013, AC-014"""

    @pytest.mark.asyncio
    async def test_free_chat_stream_returns_sse(self, client, auth_token, legacy_game_setup):
        """AC-011: POST /game/{id}/free-chat/stream returns text/event-stream + X-Accel-Buffering: no."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"message": "Hello Aria!"}

        async def mock_stream(*args, **kwargs):
            for token in ["Hi", " there!"]:
                yield token

        with patch("app.services.free_chat_service.FreeChatService.send_message_stream", mock_stream):
            response = await client.post(
                f"/api/v1/game/{setup['session'].id}/free-chat/stream",
                json=payload, headers=headers,
            )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        assert response.headers.get("x-accel-buffering") == "no"

    @pytest.mark.asyncio
    async def test_free_chat_stream_text_events(self, client, auth_token, legacy_game_setup):
        """AC-013: SSE逐字输出角色回复."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"message": "Tell me a story"}

        async def mock_stream(*args, **kwargs):
            for token in ["Once", " upon", " a time"]:
                yield token

        with patch("app.services.free_chat_service.FreeChatService.send_message_stream", mock_stream):
            response = await client.post(
                f"/api/v1/game/{setup['session'].id}/free-chat/stream",
                json=payload, headers=headers,
            )

        body = response.text
        assert '"type":"text"' in body or '"type": "text"' in body
        assert "Once" in body and "upon" in body

    @pytest.mark.asyncio
    async def test_free_chat_stream_done_event(self, client, auth_token, legacy_game_setup):
        """AC-014: done event carries session_id."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"message": "Hi"}

        async def mock_stream(*args, **kwargs):
            yield "Hello"
            yield " back"

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


class TestFreeChatDeprecation:
    """AC-015: Old free-chat endpoint returns JSON + Deprecation header"""

    @pytest.mark.asyncio
    async def test_old_free_chat_returns_deprecation_header(self, client, auth_token, legacy_game_setup):
        """AC-015: Old POST /game/{id}/free-chat returns JSON 200 with Deprecation: true header."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"message": "Hello"}

        with patch("app.services.free_chat_service.get_free_chat_service") as mock_svc:
            mock_svc.return_value.send_message = AsyncMock(return_value={
                "reply": "Hi there!",
                "emotion": "happy",
                "character_id": str(setup["character"].id),
            })

            # Also mock daily tasks and achievements to not interfere
            with patch("app.api.v1.daily_tasks.update_progress", AsyncMock()):
                response = await client.post(
                    f"/api/v1/game/{setup['session'].id}/free-chat",
                    json=payload, headers=headers,
                )

        assert response.status_code == 200
        assert response.headers.get("deprecation") == "true"
        body = response.json()
        assert body.get("reply") == "Hi there!"
