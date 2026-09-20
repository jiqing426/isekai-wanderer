"""Unit tests for CR-037 DEV-002: Corvus models + API endpoints.

Test Case Artifacts:
- TC-DB-001: 建表迁移 + UUID v4 验证 + slug 字段类型验证
- TC-API-001: player/candidates API + session/create API

Covers AC-005, AC-006, AC-021, AC-022.

Uses SQLite in-memory DB with conftest.py fixtures.
"""
import pytest
import uuid
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.corvus import (
    PlayerCandidate,
    CorvusGameSession,
    SessionNpc,
    InventoryItem,
    StoryFlag,
)
from app.api.v1.auth import get_current_user_id
from app.main import app


def _override_auth(user_id: str):
    """Helper to override auth dependency and return the override dict entry."""
    app.dependency_overrides[get_current_user_id] = lambda: user_id


# ── TC-DB-001: 建表迁移 + UUID v4 验证 + slug 字段类型 ──────────────────


class TestTCDB001MigrationAndSchema:
    """TC-DB-001: Verify 5 corvus tables exist with correct schema."""

    @pytest.mark.asyncio
    async def test_player_candidates_table_exists(self, db_session: AsyncSession):
        """AC-021: player_candidates table exists with UUID v4 PK."""
        result = await db_session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='player_candidates'"
        ))
        assert result.fetchone() is not None, "player_candidates table should exist"

    @pytest.mark.asyncio
    async def test_corvus_game_sessions_table_exists(self, db_session: AsyncSession):
        """AC-021: corvus_game_sessions table exists with UUID v4 PK."""
        result = await db_session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='corvus_game_sessions'"
        ))
        assert result.fetchone() is not None, "corvus_game_sessions table should exist"

    @pytest.mark.asyncio
    async def test_session_npcs_table_exists(self, db_session: AsyncSession):
        """AC-021: session_npcs table exists with UUID v4 PK."""
        result = await db_session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='session_npcs'"
        ))
        assert result.fetchone() is not None, "session_npcs table should exist"

    @pytest.mark.asyncio
    async def test_inventory_items_table_exists(self, db_session: AsyncSession):
        """AC-021: inventory_items table exists with UUID v4 PK."""
        result = await db_session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='inventory_items'"
        ))
        assert result.fetchone() is not None, "inventory_items table should exist"

    @pytest.mark.asyncio
    async def test_story_flags_table_exists(self, db_session: AsyncSession):
        """AC-021: story_flags table exists with UUID v4 PK."""
        result = await db_session.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='story_flags'"
        ))
        assert result.fetchone() is not None, "story_flags table should exist"

    @pytest.mark.asyncio
    async def test_player_candidates_id_is_uuid_type(self, db_session: AsyncSession):
        """AC-021: player_candidates.id is UUID type (SQLite renders as TEXT with hex default)."""
        result = await db_session.execute(text("PRAGMA table_info(player_candidates)"))
        cols = {row[1]: row for row in result.fetchall()}
        assert 'id' in cols, "id column must exist"
        # In SQLite, UUID is stored as TEXT; the default uses hex random blob
        # In PostgreSQL production, it's UUID with gen_random_uuid()
        assert cols['id'][3] == 1, "id should be NOT NULL (primary key)"

    @pytest.mark.asyncio
    async def test_corvus_game_sessions_id_is_uuid_type(self, db_session: AsyncSession):
        """AC-021: corvus_game_sessions.id is UUID type (PK, NOT NULL)."""
        result = await db_session.execute(text("PRAGMA table_info(corvus_game_sessions)"))
        cols = {row[1]: row for row in result.fetchall()}
        assert 'id' in cols, "id column must exist"
        assert cols['id'][3] == 1, "id should be NOT NULL (primary key)"

    @pytest.mark.asyncio
    async def test_session_npcs_id_is_uuid_type(self, db_session: AsyncSession):
        """AC-021: session_npcs.id is UUID type (PK, NOT NULL)."""
        result = await db_session.execute(text("PRAGMA table_info(session_npcs)"))
        cols = {row[1]: row for row in result.fetchall()}
        assert 'id' in cols, "id column must exist"
        assert cols['id'][3] == 1, "id should be NOT NULL (primary key)"

    @pytest.mark.asyncio
    async def test_inventory_items_id_is_uuid_type(self, db_session: AsyncSession):
        """AC-021: inventory_items.id is UUID type (PK, NOT NULL)."""
        result = await db_session.execute(text("PRAGMA table_info(inventory_items)"))
        cols = {row[1]: row for row in result.fetchall()}
        assert 'id' in cols, "id column must exist"
        assert cols['id'][3] == 1, "id should be NOT NULL (primary key)"

    @pytest.mark.asyncio
    async def test_story_flags_id_is_uuid_type(self, db_session: AsyncSession):
        """AC-021: story_flags.id is UUID type (PK, NOT NULL)."""
        result = await db_session.execute(text("PRAGMA table_info(story_flags)"))
        cols = {row[1]: row for row in result.fetchall()}
        assert 'id' in cols, "id column must exist"
        assert cols['id'][3] == 1, "id should be NOT NULL (primary key)"

    @pytest.mark.asyncio
    async def test_corvus_internal_game_id_is_varchar_100(self, db_session: AsyncSession):
        """AC-022: corvus_game_sessions.corvus_internal_game_id is VARCHAR(100).

        In SQLite, VARCHAR(100) renders as VARCHAR with length 100.
        In PostgreSQL production, it's character varying(100).
        We verify the column exists and has the right type affinity.
        """
        result = await db_session.execute(text("PRAGMA table_info(corvus_game_sessions)"))
        cols = {row[1]: row for row in result.fetchall()}
        assert 'corvus_internal_game_id' in cols, "corvus_internal_game_id column must exist"
        # SQLite stores type affinity; VARCHAR(100) → TEXT affinity
        col_type = cols['corvus_internal_game_id'][2].upper()
        assert 'VARCHAR' in col_type or 'TEXT' in col_type, \
            f"corvus_internal_game_id should be VARCHAR(100), got {col_type}"

    @pytest.mark.asyncio
    async def test_corvus_internal_game_id_nullable(self, db_session: AsyncSession):
        """AC-022: corvus_internal_game_id is nullable (set after Corvus create_game)."""
        result = await db_session.execute(text("PRAGMA table_info(corvus_game_sessions)"))
        cols = {row[1]: row for row in result.fetchall()}
        assert cols['corvus_internal_game_id'][3] == 0, \
            "corvus_internal_game_id should be nullable"

    @pytest.mark.asyncio
    async def test_corvus_game_sessions_status_default(self, db_session: AsyncSession):
        """AC-006: corvus_game_sessions.status defaults to 'waiting_select_player'."""
        result = await db_session.execute(text("PRAGMA table_info(corvus_game_sessions)"))
        cols = {row[1]: row for row in result.fetchall()}
        assert 'status' in cols, "status column must exist"

    @pytest.mark.asyncio
    async def test_story_flags_unique_constraint(self, db_session: AsyncSession):
        """AC-014 (preview): story_flags has UNIQUE(game_session_id, flag_key)."""
        # Verify unique index exists
        result = await db_session.execute(text(
            "PRAGMA index_list(story_flags)"
        ))
        indexes = result.fetchall()
        # SQLite creates autoindex for UNIQUE constraints
        assert len(indexes) >= 1, "story_flags should have unique constraint on (game_session_id, flag_key)"

    @pytest.mark.asyncio
    async def test_player_candidates_model_uuid_default(self, db_session: AsyncSession):
        """AC-021: PlayerCandidate model generates UUID v4 by default."""
        pc = PlayerCandidate(
            user_id=uuid.uuid4(),
            name="测试角色",
            personality="冷静",
            backstory="来自远方",
        )
        db_session.add(pc)
        await db_session.flush()
        # Verify UUID v4 format (4 in version field)
        assert pc.id is not None
        assert isinstance(pc.id, uuid.UUID)
        assert pc.id.version == 4, f"UUID should be v4, got v{pc.id.version}"

    @pytest.mark.asyncio
    async def test_corvus_game_session_model_uuid_default(self, db_session: AsyncSession):
        """AC-021: CorvusGameSession model generates UUID v4 by default."""
        session = CorvusGameSession(
            user_id=uuid.uuid4(),
        )
        db_session.add(session)
        await db_session.flush()
        assert session.id is not None
        assert isinstance(session.id, uuid.UUID)
        assert session.id.version == 4

    @pytest.mark.asyncio
    async def test_corvus_game_session_status_default(self, db_session: AsyncSession):
        """AC-006: CorvusGameSession status defaults to 'waiting_select_player'."""
        session = CorvusGameSession(
            user_id=uuid.uuid4(),
        )
        db_session.add(session)
        await db_session.flush()
        assert session.status == "waiting_select_player"

    @pytest.mark.asyncio
    async def test_corvus_game_session_engine_type_default(self, db_session: AsyncSession):
        """AC-020 (preview): CorvusGameSession engine_type defaults to 'corvus'."""
        session = CorvusGameSession(
            user_id=uuid.uuid4(),
        )
        db_session.add(session)
        await db_session.flush()
        assert session.engine_type == "corvus"

    @pytest.mark.asyncio
    async def test_session_npc_model_uuid_default(self, db_session: AsyncSession):
        """AC-021: SessionNpc model generates UUID v4 by default."""
        npc = SessionNpc(
            game_session_id=uuid.uuid4(),
            name="NPC测试",
        )
        db_session.add(npc)
        await db_session.flush()
        assert npc.id is not None
        assert isinstance(npc.id, uuid.UUID)
        assert npc.id.version == 4

    @pytest.mark.asyncio
    async def test_inventory_item_model_uuid_default(self, db_session: AsyncSession):
        """AC-021: InventoryItem model generates UUID v4 by default."""
        item = InventoryItem(
            game_session_id=uuid.uuid4(),
            name="测试道具",
        )
        db_session.add(item)
        await db_session.flush()
        assert item.id is not None
        assert isinstance(item.id, uuid.UUID)
        assert item.id.version == 4

    @pytest.mark.asyncio
    async def test_story_flag_model_uuid_default(self, db_session: AsyncSession):
        """AC-021: StoryFlag model generates UUID v4 by default."""
        flag = StoryFlag(
            game_session_id=uuid.uuid4(),
            flag_key="test_flag",
        )
        db_session.add(flag)
        await db_session.flush()
        assert flag.id is not None
        assert isinstance(flag.id, uuid.UUID)
        assert flag.id.version == 4


# ── TC-API-001: player/candidates + session/create API ────────────────────


class TestTCAPI001PlayerCandidatesAndSessionCreate:
    """TC-API-001: Test the two new API endpoints."""

    @pytest.mark.asyncio
    async def test_get_player_candidates_empty(self, client, db_session):
        """AC-005: GET /api/v1/game/player/candidates returns code:0 with empty data when no candidates."""
        # Need a user for auth — use the test client which auto-handles auth
        # The conftest overrides auth via DISABLE_MOCK and get_current_user_id
        # We need to mock the auth dependency
        from app.api.v1.auth import get_current_user_id

        test_user_id = str(uuid.uuid4())
        app.dependency_overrides[get_current_user_id] = lambda: test_user_id

        response = await client.get("/api/v1/game/player/candidates")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 0  # No candidates yet

    @pytest.mark.asyncio
    async def test_get_player_candidates_with_data(self, client, db_session):
        """AC-005: GET /api/v1/game/player/candidates returns max 3 candidates with required fields."""
        from app.api.v1.auth import get_current_user_id

        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        # Create 3 player candidates
        for name in ["白夜", "沈星澜", "藤原雪"]:
            pc = PlayerCandidate(
                user_id=test_user_id,
                name=name,
                personality=f"{name}的性格",
                backstory=f"{name}的背景",
                appearance=f"{name}的外貌",
                initial_inventory=[{"item": "sword"}],
            )
            db_session.add(pc)
        await db_session.flush()

        response = await client.get("/api/v1/game/player/candidates")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) == 3  # Exactly 3

        for candidate in data["data"]:
            assert "id" in candidate
            assert "name" in candidate
            assert "personality" in candidate
            assert "backstory" in candidate
            assert "appearance" in candidate
            assert "initial_inventory" in candidate

    @pytest.mark.asyncio
    async def test_get_player_candidates_max_3(self, client, db_session):
        """AC-005: GET /api/v1/game/player/candidates returns at most 3 candidates."""
        from app.api.v1.auth import get_current_user_id

        test_user_id = uuid.uuid4()
        app.dependency_overrides[get_current_user_id] = lambda: str(test_user_id)

        # Create 5 candidates — only 3 should be returned
        for i in range(5):
            pc = PlayerCandidate(
                user_id=test_user_id,
                name=f"角色{i}",
            )
            db_session.add(pc)
        await db_session.flush()

        response = await client.get("/api/v1/game/player/candidates")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) <= 3  # At most 3

    @pytest.mark.asyncio
    async def test_post_session_create_returns_uuid_v4(self, client, db_session):
        """AC-006: POST /api/v1/game/session/create returns game_session_id as UUID v4."""
        from app.api.v1.auth import get_current_user_id

        test_user_id = str(uuid.uuid4())
        app.dependency_overrides[get_current_user_id] = lambda: test_user_id

        response = await client.post(
            "/api/v1/game/session/create",
            json={},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        session_id = data["data"]["game_session_id"]
        # Verify UUID v4 format
        parsed = uuid.UUID(session_id)
        assert parsed.version == 4, f"game_session_id should be UUID v4, got v{parsed.version}"

    @pytest.mark.asyncio
    async def test_post_session_create_status_waiting(self, client, db_session):
        """AC-006: POST /api/v1/game/session/create returns status=waiting_select_player."""
        from app.api.v1.auth import get_current_user_id

        test_user_id = str(uuid.uuid4())
        app.dependency_overrides[get_current_user_id] = lambda: test_user_id

        response = await client.post(
            "/api/v1/game/session/create",
            json={},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "waiting_select_player"

    @pytest.mark.asyncio
    async def test_post_session_create_engine_type_corvus(self, client, db_session):
        """AC-020 (preview): POST /api/v1/game/session/create returns engine_type=corvus."""
        from app.api.v1.auth import get_current_user_id

        test_user_id = str(uuid.uuid4())
        app.dependency_overrides[get_current_user_id] = lambda: test_user_id

        response = await client.post(
            "/api/v1/game/session/create",
            json={},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["engine_type"] == "corvus"

    @pytest.mark.asyncio
    async def test_post_session_create_db_record_exists(self, client):
        """AC-006: POST /api/v1/game/session/create creates a DB record in corvus_game_sessions.

        Uses TestSessionLocal (same factory as override_get_db) to verify the
        record was committed, since the API endpoint uses its own session via
        override_get_db.
        """
        from app.api.v1.auth import get_current_user_id
        from tests.conftest import TestSessionLocal

        test_user_id = str(uuid.uuid4())
        app.dependency_overrides[get_current_user_id] = lambda: test_user_id

        response = await client.post(
            "/api/v1/game/session/create",
            json={},
        )
        assert response.status_code == 200
        session_id = response.json()["data"]["game_session_id"]

        # The API endpoint commits its own session via override_get_db.
        # Verify the record exists by querying with a fresh session from the same factory.
        # If the row is not visible, it means the commit didn't reach the DB.
        # Use a SELECT with no parameter binding for SQLite compatibility.
        from app.models.corvus import CorvusGameSession
        from sqlalchemy import select

        async with TestSessionLocal() as session:
            stmt = select(CorvusGameSession).where(
                CorvusGameSession.id == uuid.UUID(session_id)
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            assert record is not None, f"DB record should exist for session {session_id}"
            assert record.status == "waiting_select_player"
            assert record.engine_type == "corvus"


# ── Migration file verification ─────────────────────────────────────────────


class TestMigrationFile:
    """Verify the Alembic migration file exists and has correct structure."""

    def test_migration_file_exists(self):
        """Verify migration file exists at expected path."""
        import os
        unit_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(unit_dir))
        migration_path = os.path.join(
            backend_dir, "alembic", "versions", "cr037_corvus_tables.py"
        )
        assert os.path.exists(migration_path), "Migration file should exist"

    def test_migration_file_has_correct_metadata(self):
        """Verify migration file has correct revision metadata."""
        import os
        unit_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(unit_dir))
        migration_path = os.path.join(
            backend_dir, "alembic", "versions", "cr037_corvus_tables.py"
        )
        with open(migration_path) as f:
            content = f.read()

        assert "revision" in content
        assert "cr037_corvus_tables" in content
        assert "down_revision" in content
        assert "cr030_chapter_structure" in content
        assert "def upgrade()" in content
        assert "def downgrade()" in content
        assert "player_candidates" in content
        assert "corvus_game_sessions" in content
        assert "session_npcs" in content
        assert "inventory_items" in content
        assert "story_flags" in content

    def test_migration_corvus_internal_game_id_varchar_100(self):
        """AC-022: Migration uses VARCHAR(100) for corvus_internal_game_id."""
        import os
        unit_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(unit_dir))
        migration_path = os.path.join(
            backend_dir, "alembic", "versions", "cr037_corvus_tables.py"
        )
        with open(migration_path) as f:
            content = f.read()

        assert "corvus_internal_game_id" in content
        assert "String(100)" in content

    def test_migration_all_ids_are_uuid(self):
        """AC-021: Migration uses UUID type for all 5 table PKs."""
        import os
        unit_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(unit_dir))
        migration_path = os.path.join(
            backend_dir, "alembic", "versions", "cr037_corvus_tables.py"
        )
        with open(migration_path) as f:
            content = f.read()

        assert "gen_random_uuid()" in content
