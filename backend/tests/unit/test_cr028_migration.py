"""Unit tests for CR-028 migration schema changes.

Validates that:
1. Model fields are correctly defined
2. Schema creation works (via SQLAlchemy metadata)
3. Data migration logic (is_main → playable) is correct
"""

import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text, inspect

# Register JSONB/Vector for SQLite
try:
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy.ext.compiler import compiles

    @compiles(JSONB, "sqlite")
    def compile_jsonb_sqlite(type_, compiler, **kw):
        return "TEXT"
except ImportError:
    pass

try:
    from pgvector.sqlalchemy import Vector
    from sqlalchemy.ext.compiler import compiles as compiles2

    @compiles2(Vector, "sqlite")
    def compile_vector_sqlite(type_, compiler, **kw):
        return "TEXT"
except ImportError:
    pass

from app.core.database import Base
from app.models.script import Character, Script, Route
from app.models.game import GameSession
from app.models.user import User
from app.models.user_character_unlock import UserCharacterUnlock


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db():
    async with TestSession() as session:
        yield session


class TestCR028Schema:
    """T-028-01: Verify schema changes are correct."""

    @pytest.mark.asyncio
    async def test_character_has_playable_fields(self, db: AsyncSession):
        """Character model has all 5 new CR-028 fields."""
        # Check model attributes exist
        assert hasattr(Character, 'playable')
        assert hasattr(Character, 'playable_route_id')
        assert hasattr(Character, 'play_description')
        assert hasattr(Character, 'unlock_type')
        assert hasattr(Character, 'unlock_price')

        # Create a character with all fields
        script = Script(id=uuid4(), title="Test", slug="test-cr028", genre="fantasy")
        db.add(script)
        await db.flush()

        route = Route(id=uuid4(), script_id=script.id, title="Test Route")
        db.add(route)
        await db.flush()

        char = Character(
            id=uuid4(),
            script_id=script.id,
            name="TestChar",
            playable=True,
            playable_route_id=route.id,
            play_description="Play as TestChar",
            unlock_type="paid",
            unlock_price=100,
        )
        db.add(char)
        await db.commit()
        await db.refresh(char)

        assert char.playable is True
        assert char.playable_route_id == route.id
        assert char.play_description == "Play as TestChar"
        assert char.unlock_type == "paid"
        assert char.unlock_price == 100

    @pytest.mark.asyncio
    async def test_character_defaults(self, db: AsyncSession):
        """Character CR-028 fields have correct defaults."""
        script = Script(id=uuid4(), title="Test", slug="test-defaults", genre="fantasy")
        db.add(script)
        await db.flush()

        char = Character(
            id=uuid4(),
            script_id=script.id,
            name="DefaultChar",
        )
        db.add(char)
        await db.commit()
        await db.refresh(char)

        assert char.playable is False
        assert char.playable_route_id is None
        assert char.play_description is None
        assert char.unlock_type == "free"
        assert char.unlock_price == 0

    @pytest.mark.asyncio
    async def test_game_session_has_character_fields(self, db: AsyncSession):
        """GameSession model has character_id and character_name."""
        assert hasattr(GameSession, 'character_id')
        assert hasattr(GameSession, 'character_name')

        # Create a session with character
        script = Script(id=uuid4(), title="Test", slug="test-gs-cr028", genre="fantasy")
        db.add(script)
        await db.flush()

        route = Route(id=uuid4(), script_id=script.id, title="Route")
        db.add(route)
        await db.flush()

        char = Character(
            id=uuid4(),
            script_id=script.id,
            name="Hero",
            playable=True,
        )
        db.add(char)
        await db.flush()

        user = User(id=uuid4(), email="test@test.com", email_verified=True)
        db.add(user)
        await db.flush()

        session = GameSession(
            id=uuid4(),
            user_id=user.id,
            script_id=script.id,
            route_id=route.id,
            character_id=char.id,
            character_name="Hero",
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

        assert session.character_id == char.id
        assert session.character_name == "Hero"

    @pytest.mark.asyncio
    async def test_game_session_character_nullable(self, db: AsyncSession):
        """GameSession character fields are nullable (backward compat)."""
        script = Script(id=uuid4(), title="Test", slug="test-null-cr028", genre="fantasy")
        db.add(script)
        await db.flush()

        route = Route(id=uuid4(), script_id=script.id, title="Route")
        db.add(route)
        await db.flush()

        user = User(id=uuid4(), email="null@test.com", email_verified=True)
        db.add(user)
        await db.flush()

        session = GameSession(
            id=uuid4(),
            user_id=user.id,
            script_id=script.id,
            route_id=route.id,
            character_id=None,
            character_name=None,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

        assert session.character_id is None
        assert session.character_name is None

    @pytest.mark.asyncio
    async def test_user_character_unlock_table(self, db: AsyncSession):
        """user_character_unlocks table exists with correct structure."""
        assert hasattr(UserCharacterUnlock, 'user_id')
        assert hasattr(UserCharacterUnlock, 'character_id')
        assert hasattr(UserCharacterUnlock, 'unlocked_at')

        user = User(id=uuid4(), email="unlock@test.com", email_verified=True)
        db.add(user)
        await db.flush()

        script = Script(id=uuid4(), title="Test", slug="test-unlock-cr028", genre="fantasy")
        db.add(script)
        await db.flush()

        char = Character(id=uuid4(), script_id=script.id, name="LockedChar")
        db.add(char)
        await db.flush()

        unlock = UserCharacterUnlock(
            id=uuid4(),
            user_id=user.id,
            character_id=char.id,
        )
        db.add(unlock)
        await db.commit()
        await db.refresh(unlock)

        assert unlock.user_id == user.id
        assert unlock.character_id == char.id
        assert unlock.unlocked_at is not None


class TestCR028DataMigration:
    """T-028-02: Verify data migration logic."""

    @pytest.mark.asyncio
    async def test_is_main_becomes_playable(self, db: AsyncSession):
        """is_main=true characters should become playable after migration."""
        script = Script(id=uuid4(), title="Test", slug="test-migrate", genre="fantasy")
        db.add(script)
        await db.flush()

        route = Route(id=uuid4(), script_id=script.id, title="Main Route")
        db.add(route)
        await db.flush()

        # is_main character
        char = Character(
            id=uuid4(),
            script_id=script.id,
            name="MainHero",
            is_main=True,
            description="The main hero",
            playable=False,  # Before migration
        )
        db.add(char)
        await db.commit()

        # Simulate migration logic
        await db.execute(text("""
            UPDATE characters
            SET playable = 1,
                unlock_type = 'free',
                playable_route_id = (
                    SELECT r.id FROM routes r
                    WHERE r.script_id = characters.script_id
                    ORDER BY r.created_at ASC
                    LIMIT 1
                ),
                play_description = COALESCE(
                    characters.description,
                    '扮演' || characters.name || '探索故事'
                )
            WHERE is_main = 1
              AND playable = 0
        """))
        await db.commit()
        await db.refresh(char)

        assert char.playable is True
        assert char.unlock_type == "free"
        assert char.playable_route_id == route.id
        assert char.play_description == "The main hero"

    @pytest.mark.asyncio
    async def test_migration_idempotent(self, db: AsyncSession):
        """Running migration twice should not change data."""
        script = Script(id=uuid4(), title="Test", slug="test-idempotent", genre="fantasy")
        db.add(script)
        await db.flush()

        route = Route(id=uuid4(), script_id=script.id, title="Route")
        db.add(route)
        await db.flush()

        char = Character(
            id=uuid4(),
            script_id=script.id,
            name="Hero",
            is_main=True,
            description="Hero desc",
            playable=False,
        )
        db.add(char)
        await db.commit()

        migration_sql = text("""
            UPDATE characters
            SET playable = 1,
                unlock_type = 'free',
                playable_route_id = (
                    SELECT r.id FROM routes r
                    WHERE r.script_id = characters.script_id
                    ORDER BY r.created_at ASC
                    LIMIT 1
                ),
                play_description = COALESCE(
                    characters.description,
                    '扮演' || characters.name || '探索故事'
                )
            WHERE is_main = 1
              AND playable = 0
        """)

        # Run once
        await db.execute(migration_sql)
        await db.commit()
        await db.refresh(char)
        first_playable = char.playable
        first_route = char.playable_route_id

        # Run again
        await db.execute(migration_sql)
        await db.commit()
        await db.refresh(char)

        assert char.playable == first_playable
        assert char.playable_route_id == first_route

    @pytest.mark.asyncio
    async def test_non_main_stays_not_playable(self, db: AsyncSession):
        """is_main=false characters should NOT become playable."""
        script = Script(id=uuid4(), title="Test", slug="test-nonmain", genre="fantasy")
        db.add(script)
        await db.flush()

        route = Route(id=uuid4(), script_id=script.id, title="Route")
        db.add(route)
        await db.flush()

        char = Character(
            id=uuid4(),
            script_id=script.id,
            name="NPC",
            is_main=False,
            playable=False,
        )
        db.add(char)
        await db.commit()

        await db.execute(text("""
            UPDATE characters
            SET playable = 1,
                unlock_type = 'free',
                playable_route_id = (
                    SELECT r.id FROM routes r
                    WHERE r.script_id = characters.script_id
                    ORDER BY r.created_at ASC
                    LIMIT 1
                ),
                play_description = COALESCE(
                    characters.description,
                    '扮演' || characters.name || '探索故事'
                )
            WHERE is_main = 1
              AND playable = 0
        """))
        await db.commit()
        await db.refresh(char)

        assert char.playable is False
        assert char.playable_route_id is None


class TestCR028Backfill:
    """T-028-02: Verify backfill logic for existing game_sessions."""

    @pytest.mark.asyncio
    async def test_backfill_character_name(self, db: AsyncSession):
        """GameSession with character_id but no character_name gets backfilled."""
        script = Script(id=uuid4(), title="Test", slug="test-backfill", genre="fantasy")
        db.add(script)
        await db.flush()

        route = Route(id=uuid4(), script_id=script.id, title="Route")
        db.add(route)
        await db.flush()

        char = Character(
            id=uuid4(),
            script_id=script.id,
            name="Hero",
            playable=True,
        )
        db.add(char)
        await db.flush()

        user = User(id=uuid4(), email="backfill@test.com", email_verified=True)
        db.add(user)
        await db.flush()

        # Create a game_session with character_id but no character_name
        session = GameSession(
            id=uuid4(),
            user_id=user.id,
            script_id=script.id,
            route_id=route.id,
            character_id=char.id,
            character_name=None,  # Missing
        )
        db.add(session)
        await db.commit()

        # Run backfill
        await db.execute(text("""
            UPDATE game_sessions
            SET character_name = (
                SELECT c.name FROM characters c
                WHERE c.id = game_sessions.character_id
            )
            WHERE character_id IS NOT NULL
              AND character_name IS NULL
        """))
        await db.commit()
        await db.refresh(session)

        assert session.character_name == "Hero"

    @pytest.mark.asyncio
    async def test_backfill_idempotent(self, db: AsyncSession):
        """Running backfill twice should not change data."""
        script = Script(id=uuid4(), title="Test", slug="test-backfill-idem", genre="fantasy")
        db.add(script)
        await db.flush()

        route = Route(id=uuid4(), script_id=script.id, title="Route")
        db.add(route)
        await db.flush()

        char = Character(
            id=uuid4(),
            script_id=script.id,
            name="Hero",
            playable=True,
        )
        db.add(char)
        await db.flush()

        user = User(id=uuid4(), email="backfill-idem@test.com", email_verified=True)
        db.add(user)
        await db.flush()

        session = GameSession(
            id=uuid4(),
            user_id=user.id,
            script_id=script.id,
            route_id=route.id,
            character_id=char.id,
            character_name=None,
        )
        db.add(session)
        await db.commit()

        backfill_sql = text("""
            UPDATE game_sessions
            SET character_name = (
                SELECT c.name FROM characters c
                WHERE c.id = game_sessions.character_id
            )
            WHERE character_id IS NOT NULL
              AND character_name IS NULL
        """)

        # Run once
        await db.execute(backfill_sql)
        await db.commit()
        await db.refresh(session)
        first_name = session.character_name

        # Run again
        await db.execute(backfill_sql)
        await db.commit()
        await db.refresh(session)

        assert session.character_name == first_name

    @pytest.mark.asyncio
    async def test_backfill_preserves_existing_name(self, db: AsyncSession):
        """Backfill should not overwrite existing character_name."""
        script = Script(id=uuid4(), title="Test", slug="test-backfill-preserve", genre="fantasy")
        db.add(script)
        await db.flush()

        route = Route(id=uuid4(), script_id=script.id, title="Route")
        db.add(route)
        await db.flush()

        char = Character(
            id=uuid4(),
            script_id=script.id,
            name="NewName",
            playable=True,
        )
        db.add(char)
        await db.flush()

        user = User(id=uuid4(), email="preserve@test.com", email_verified=True)
        db.add(user)
        await db.flush()

        # GameSession already has character_name set
        session = GameSession(
            id=uuid4(),
            user_id=user.id,
            script_id=script.id,
            route_id=route.id,
            character_id=char.id,
            character_name="OldName",  # Already set
        )
        db.add(session)
        await db.commit()

        # Run backfill
        await db.execute(text("""
            UPDATE game_sessions
            SET character_name = (
                SELECT c.name FROM characters c
                WHERE c.id = game_sessions.character_id
            )
            WHERE character_id IS NOT NULL
              AND character_name IS NULL
        """))
        await db.commit()
        await db.refresh(session)

        # Should preserve the original name
        assert session.character_name == "OldName"
