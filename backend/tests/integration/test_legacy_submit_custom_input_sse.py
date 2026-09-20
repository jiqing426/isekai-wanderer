"""Integration tests for Legacy submit_custom_input SSE streaming.

CR-042 DEV-001 AC-006, AC-007, AC-008, AC-009

AC-006: Legacy submit_custom_input returns text/event-stream
AC-007: Uses llm_gateway.stream_dialogue() (not _generate_custom_response)
AC-008: SSE逐字输出角色回应文本
AC-009: done event carries metadata; deferred DB write
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
    script = Script(id=uuid.uuid4(), title="Test Script", slug="test-script", genre="fantasy")
    db_session.add(script)
    route = Route(id=uuid.uuid4(), script_id=script.id, title="Test Route")
    db_session.add(route)
    character = Character(
        id=uuid.uuid4(), script_id=script.id, name="Aria",
        personality={"traits": ["kind"]}, is_main=True,
    )
    db_session.add(character)
    node = Node(
        id=uuid.uuid4(), route_id=route.id, node_type="ai_dialog",
        content={"text": "Hello", "context": "Greeting scene"},
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


class TestLegacySubmitCustomInputSSE:
    """AC-006, AC-007, AC-008, AC-009"""

    @pytest.mark.asyncio
    async def test_custom_input_returns_sse(self, client, auth_token, legacy_game_setup):
        """AC-006: Legacy submit_custom_input returns text/event-stream."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"text": "Hello Aria!"}

        async def mock_stream_dialogue(*args, **kwargs):
            for token in ["Hi", " there!"]:
                yield token

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

        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")
        assert response.headers.get("x-accel-buffering") == "no"

    @pytest.mark.asyncio
    async def test_custom_input_sse_text_events(self, client, auth_token, legacy_game_setup):
        """AC-008: SSE逐字输出角色回应."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"text": "Tell me about yourself"}

        async def mock_stream_dialogue(*args, **kwargs):
            for token in ["I", " am", " Aria"]:
                yield token

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
        assert '"type":"text"' in body or '"type": "text"' in body
        assert "I" in body and "am" in body and "Aria" in body

    @pytest.mark.asyncio
    async def test_custom_input_sse_done_event(self, client, auth_token, legacy_game_setup):
        """AC-009: done event carries session_id and node_id."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"text": "Hello"}

        async def mock_stream_dialogue(*args, **kwargs):
            yield "Response"
            yield " text"

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
    async def test_custom_input_sse_error_event(self, client, auth_token, legacy_game_setup):
        """AC-006: SSE error event on failure."""
        setup = legacy_game_setup
        headers = {"Authorization": f"Bearer {auth_token}"}
        payload = {"text": "Hello"}

        async def mock_stream_dialogue(*args, **kwargs):
            raise RuntimeError("LLM error")
            yield

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
        assert '"type":"error"' in body or '"type": "error"' in body
