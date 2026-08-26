"""Integration test fixtures for CR-027."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import event
from sqlalchemy.engine import Engine
from uuid import uuid4
import os

# Disable mock middleware for tests
os.environ["DISABLE_MOCK"] = "1"

from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token
from app.models.user import User
from app.models.script import Script, Route, Node

# Register pgvector Vector type for SQLite
try:
    from pgvector.sqlalchemy import Vector
    from sqlalchemy.ext.compiler import compiles

    @compiles(Vector, "sqlite")
    def compile_vector_sqlite(type_, compiler, **kw):
        return "TEXT"
except ImportError:
    pass

# Register JSONB type for SQLite
try:
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy.ext.compiler import compiles

    @compiles(JSONB, "sqlite")
    def compile_jsonb_sqlite(type_, compiler, **kw):
        return "TEXT"
except ImportError:
    pass

# Use in-memory SQLite for integration tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """Create all tables before each test and drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Provide a database session for tests."""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user."""
    user = User(
        id=uuid4(),
        email="admin@test.com",
        display_name="admin",
        is_admin=True,
        email_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def regular_user(db_session: AsyncSession) -> User:
    """Create a regular user."""
    user = User(
        id=uuid4(),
        email="user@test.com",
        display_name="user",
        is_admin=False,
        email_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Generate JWT token for admin user."""
    return create_access_token({"sub": str(admin_user.id)})


@pytest.fixture
def user_token(regular_user: User) -> str:
    """Generate JWT token for regular user."""
    return create_access_token({"sub": str(regular_user.id)})


@pytest_asyncio.fixture
async def test_script(db_session: AsyncSession) -> Script:
    """Create a test script."""
    script = Script(
        id=uuid4(),
        title="测试剧本",
        description="测试描述",
        slug="test-script",
        genre="fantasy"
    )
    db_session.add(script)
    await db_session.commit()
    await db_session.refresh(script)
    return script


@pytest_asyncio.fixture
async def test_route(db_session: AsyncSession, test_script: Script) -> Route:
    """Create a test route."""
    route = Route(
        id=uuid4(),
        script_id=test_script.id,
        title="测试路线"
    )
    db_session.add(route)
    await db_session.commit()
    await db_session.refresh(route)
    return route


@pytest_asyncio.fixture
async def test_node(db_session: AsyncSession, test_route: Route) -> Node:
    """Create a test node."""
    node = Node(
        id=uuid4(),
        route_id=test_route.id,
        node_type="dialogue",
        content={"text": "测试节点"}
    )
    db_session.add(node)
    await db_session.commit()
    await db_session.refresh(node)
    return node


@pytest.fixture
def test_node_id(test_node: Node) -> str:
    """Get test node ID as string."""
    return str(test_node.id)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """Create test client with database override."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()
