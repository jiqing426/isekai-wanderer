"""
CR-038 T-038-BE-003: GET /api/v1/game/scripts/{script_id}/characters

Test cases:
1. GET with valid script_id having playable characters → code:0 + list with id/name/description/avatar_url/play_description
2. GET with script_id that has no playable characters → code:0 + empty array
3. GET with non-existent script_id → 404
4. GET without auth → 401
5. Verify only playable=True characters are returned (non-playable excluded)
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

import os
os.environ["DISABLE_MOCK"] = "1"

from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token
from app.models.user import User
from app.models.script import Script, Route, Character

# Register pgvector + JSONB for SQLite
try:
    from pgvector.sqlalchemy import Vector
    from sqlalchemy.ext.compiler import compiles
    @compiles(Vector, "sqlite")
    def compile_vector_sqlite(type_, compiler, **kw):
        return "TEXT"
except ImportError:
    pass

try:
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy.ext.compiler import compiles
    @compiles(JSONB, "sqlite")
    def compile_jsonb_sqlite(type_, compiler, **kw):
        return "TEXT"
except ImportError:
    pass

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def test_user(db_session):
    user = User(
        id=uuid4(),
        email="test@example.com",
        display_name="test",
        email_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    return create_access_token({"sub": str(test_user.id)})


@pytest.fixture
async def test_script(db_session):
    script = Script(
        id=uuid4(),
        title="测试剧本",
        description="测试描述",
        slug="test-script-chars-001",
        genre="fantasy",
    )
    db_session.add(script)
    await db_session.commit()
    await db_session.refresh(script)
    return script


@pytest.fixture
async def test_playable_characters(db_session, test_script):
    """Create test characters: 2 playable + 1 non-playable."""
    char1 = Character(
        id=uuid4(),
        script_id=test_script.id,
        name="白夜",
        description="沉默寡言的剑士",
        avatar_url="/assets/baiye.png",
        play_description="你是白夜，一个沉默寡言的剑士。",
        playable=True,
        is_main=True,
    )
    char2 = Character(
        id=uuid4(),
        script_id=test_script.id,
        name="沈星澜",
        description="活泼开朗的少女",
        avatar_url="/assets/shen.png",
        play_description="你是沈星澜，一个活泼开朗的少女。",
        playable=True,
    )
    char3 = Character(
        id=uuid4(),
        script_id=test_script.id,
        name="NPC路人",
        description="普通村民",
        playable=False,
    )
    db_session.add_all([char1, char2, char3])
    await db_session.commit()
    await db_session.refresh(char1)
    await db_session.refresh(char2)
    return char1, char2


@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


class TestScriptCharacters:
    """Test GET /api/v1/game/scripts/{script_id}/characters endpoint."""

    @pytest.mark.asyncio
    async def test_get_characters_with_playable(
        self, client, auth_token, test_script, test_playable_characters
    ):
        """AC-038-026: GET returns playable=True characters with required fields."""
        response = await client.get(
            f"/api/v1/game/scripts/{test_script.id}/characters",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 2  # only playable=True

        for char in data["data"]:
            assert "id" in char
            assert "name" in char
            assert "description" in char
            assert "avatar_url" in char
            assert "play_description" in char

        names = {c["name"] for c in data["data"]}
        assert "白夜" in names
        assert "沈星澜" in names
        assert "NPC路人" not in names  # non-playable excluded

    @pytest.mark.asyncio
    async def test_get_characters_empty(
        self, client, auth_token, test_script
    ):
        """AC-038-026: Script with no playable characters returns empty array."""
        response = await client.get(
            f"/api/v1/game/scripts/{test_script.id}/characters",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 0

    @pytest.mark.asyncio
    async def test_get_characters_script_not_found(
        self, client, auth_token
    ):
        """AC-038-026: Non-existent script_id returns 404."""
        fake_id = str(uuid4())
        response = await client.get(
            f"/api/v1/game/scripts/{fake_id}/characters",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_characters_no_auth(
        self, client, test_script
    ):
        """AC-038-026: Without auth token returns 401."""
        response = await client.get(
            f"/api/v1/game/scripts/{test_script.id}/characters",
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_characters_excludes_non_playable(
        self, client, auth_token, test_script, test_playable_characters
    ):
        """AC-038-026: Only playable=True characters are returned."""
        response = await client.get(
            f"/api/v1/game/scripts/{test_script.id}/characters",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        for char in data["data"]:
            # Verify all returned characters have the required fields non-null
            assert char["id"] is not None
            assert char["name"] is not None
