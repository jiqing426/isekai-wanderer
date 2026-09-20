"""Unit tests for CR-037 DEV-005: world_state DB sync.

Test Case Artifacts:
- TC-DB-002: 好感度同步验证 (AC-012)
- TC-DB-003: 道具同步验证 (AC-013)
- TC-DB-004: 剧情标记同步验证 (AC-014)

Covers AC-012, AC-013, AC-014.

Uses SQLite in-memory DB with conftest.py fixtures.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, patch
from sqlalchemy import select

from app.models.corvus import CorvusGameSession, SessionNpc, InventoryItem, StoryFlag
from app.services.corvus_adapter import CorvusAdapter


async def _create_test_session(db_session, user_id=None):
    """Helper: create a CorvusGameSession in playing state."""
    session = CorvusGameSession(
        user_id=user_id or uuid.uuid4(),
        status="playing",
        corvus_internal_game_id="test-corvus-slug",
        engine_type="corvus",
    )
    db_session.add(session)
    await db_session.flush()
    return session


# ── TC-DB-002: 好感度同步验证 (AC-012) ──────────────────────────────────


class TestTCDB002AffinitySync:
    """AC-012: gm_update affinity_delta → session_npcs.affinity update."""

    @pytest.mark.asyncio
    async def test_sync_affinity_creates_npc(self, db_session):
        """AC-012: If NPC doesn't exist, create with affinity."""
        session = await _create_test_session(db_session)
        adapter = CorvusAdapter(db_session)

        gm_event = {
            "type": "gm_update",
            "summary": {
                "statChanges": [
                    {"stat": "affinity", "delta": 5, "character": "蒙面女子", "characterId": "npc-001"},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(SessionNpc).where(
            SessionNpc.game_session_id == session.id,
            SessionNpc.corvus_character_id == "npc-001",
        )
        result = await db_session.execute(stmt)
        npc = result.scalar_one_or_none()
        assert npc is not None
        assert npc.affinity == 5
        assert npc.name == "蒙面女子"

    @pytest.mark.asyncio
    async def test_sync_affinity_updates_existing(self, db_session):
        """AC-012: Update existing NPC affinity."""
        session = await _create_test_session(db_session)
        npc = SessionNpc(
            game_session_id=session.id,
            name="白夜",
            affinity=10,
            corvus_character_id="npc-001",
        )
        db_session.add(npc)
        await db_session.flush()

        adapter = CorvusAdapter(db_session)
        gm_event = {
            "type": "gm_update",
            "summary": {
                "statChanges": [
                    {"stat": "affinity", "delta": 5, "character": "白夜", "characterId": "npc-001"},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(SessionNpc).where(SessionNpc.id == npc.id)
        result = await db_session.execute(stmt)
        updated = result.scalar_one_or_none()
        assert updated.affinity == 15  # 10 + 5

    @pytest.mark.asyncio
    async def test_sync_affinity_negative_delta(self, db_session):
        """AC-012: Negative delta decreases affinity."""
        session = await _create_test_session(db_session)
        npc = SessionNpc(
            game_session_id=session.id,
            name="沈星澜",
            affinity=20,
            corvus_character_id="npc-002",
        )
        db_session.add(npc)
        await db_session.flush()

        adapter = CorvusAdapter(db_session)
        gm_event = {
            "type": "gm_update",
            "summary": {
                "statChanges": [
                    {"stat": "affinity", "delta": -8, "character": "沈星澜", "characterId": "npc-002"},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(SessionNpc).where(SessionNpc.id == npc.id)
        result = await db_session.execute(stmt)
        updated = result.scalar_one_or_none()
        assert updated.affinity == 12  # 20 - 8

    @pytest.mark.asyncio
    async def test_sync_affinity_ignores_non_affinity_stats(self, db_session):
        """AC-012: Non-affinity stat changes are ignored."""
        session = await _create_test_session(db_session)
        adapter = CorvusAdapter(db_session)

        gm_event = {
            "type": "gm_update",
            "summary": {
                "statChanges": [
                    {"stat": "health", "delta": 10, "character": "test"},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(SessionNpc).where(SessionNpc.game_session_id == session.id)
        result = await db_session.execute(stmt)
        npcs = result.scalars().all()
        assert len(npcs) == 0  # No NPC created for non-affinity stat

    @pytest.mark.asyncio
    async def test_sync_affinity_multiple_npcs(self, db_session):
        """AC-012: Multiple NPC affinity updates in one gm_update."""
        session = await _create_test_session(db_session)
        npc1 = SessionNpc(game_session_id=session.id, name="NPC1", affinity=10, corvus_character_id="c1")
        npc2 = SessionNpc(game_session_id=session.id, name="NPC2", affinity=20, corvus_character_id="c2")
        db_session.add(npc1)
        db_session.add(npc2)
        await db_session.flush()

        adapter = CorvusAdapter(db_session)
        gm_event = {
            "type": "gm_update",
            "summary": {
                "statChanges": [
                    {"stat": "affinity", "delta": 3, "character": "NPC1", "characterId": "c1"},
                    {"stat": "affinity", "delta": -5, "character": "NPC2", "characterId": "c2"},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(SessionNpc).where(SessionNpc.game_session_id == session.id)
        result = await db_session.execute(stmt)
        npcs = {n.corvus_character_id: n for n in result.scalars().all()}
        assert npcs["c1"].affinity == 13  # 10 + 3
        assert npcs["c2"].affinity == 15  # 20 - 5


# ── TC-DB-003: 道具同步验证 (AC-013) ────────────────────────────────────


class TestTCDB003InventorySync:
    """AC-013: gm_update inventory_changes → inventory_items create/update/delete."""

    @pytest.mark.asyncio
    async def test_sync_inventory_add_new_item(self, db_session):
        """AC-013: Add a new inventory item."""
        session = await _create_test_session(db_session)
        adapter = CorvusAdapter(db_session)

        gm_event = {
            "type": "gm_update",
            "summary": {
                "inventoryChanges": [
                    {"action": "add", "item": "塔罗牌", "quantity": 1, "description": "占卜用具"},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(InventoryItem).where(
            InventoryItem.game_session_id == session.id,
            InventoryItem.name == "塔罗牌",
        )
        result = await db_session.execute(stmt)
        item = result.scalar_one_or_none()
        assert item is not None
        assert item.quantity == 1
        assert item.description == "占卜用具"

    @pytest.mark.asyncio
    async def test_sync_inventory_add_increments_quantity(self, db_session):
        """AC-013: Adding existing item increments quantity."""
        session = await _create_test_session(db_session)
        item = InventoryItem(
            game_session_id=session.id,
            name="药水",
            quantity=3,
        )
        db_session.add(item)
        await db_session.flush()

        adapter = CorvusAdapter(db_session)
        gm_event = {
            "type": "gm_update",
            "summary": {
                "inventoryChanges": [
                    {"action": "add", "item": "药水", "quantity": 2},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(InventoryItem).where(InventoryItem.id == item.id)
        result = await db_session.execute(stmt)
        updated = result.scalar_one_or_none()
        assert updated.quantity == 5  # 3 + 2

    @pytest.mark.asyncio
    async def test_sync_inventory_update(self, db_session):
        """AC-013: Update existing item quantity."""
        session = await _create_test_session(db_session)
        item = InventoryItem(
            game_session_id=session.id,
            name="钥匙",
            quantity=1,
        )
        db_session.add(item)
        await db_session.flush()

        adapter = CorvusAdapter(db_session)
        gm_event = {
            "type": "gm_update",
            "summary": {
                "inventoryChanges": [
                    {"action": "update", "item": "钥匙", "quantity": 99},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(InventoryItem).where(InventoryItem.id == item.id)
        result = await db_session.execute(stmt)
        updated = result.scalar_one_or_none()
        assert updated.quantity == 99

    @pytest.mark.asyncio
    async def test_sync_inventory_remove(self, db_session):
        """AC-013: Remove an inventory item."""
        session = await _create_test_session(db_session)
        item = InventoryItem(
            game_session_id=session.id,
            name="地图",
            quantity=1,
        )
        db_session.add(item)
        await db_session.flush()
        item_id = item.id

        adapter = CorvusAdapter(db_session)
        gm_event = {
            "type": "gm_update",
            "summary": {
                "inventoryChanges": [
                    {"action": "remove", "item": "地图"},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(InventoryItem).where(InventoryItem.id == item_id)
        result = await db_session.execute(stmt)
        assert result.scalar_one_or_none() is None  # Deleted

    @pytest.mark.asyncio
    async def test_sync_inventory_persists_after_refresh(self, db_session):
        """AC-013: Items persist after DB refresh (刷新页面后道具仍存在)."""
        session = await _create_test_session(db_session)
        adapter = CorvusAdapter(db_session)

        gm_event = {
            "type": "gm_update",
            "summary": {
                "inventoryChanges": [
                    {"action": "add", "item": "星石", "quantity": 5},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        # Query with a fresh session to simulate page refresh
        from tests.conftest import TestSessionLocal
        async with TestSessionLocal() as db:
            stmt = select(InventoryItem).where(
                InventoryItem.game_session_id == session.id,
            )
            result = await db.execute(stmt)
            items = result.scalars().all()
            assert len(items) == 1
            assert items[0].name == "星石"
            assert items[0].quantity == 5


# ── TC-DB-004: 剧情标记同步验证 (AC-014) ────────────────────────────────


class TestTCDB004StoryFlagsSync:
    """AC-014: gm_update story_flags → story_flags upsert (unique constraint)."""

    @pytest.mark.asyncio
    async def test_sync_flags_creates_new(self, db_session):
        """AC-014: Create new story flag."""
        session = await _create_test_session(db_session)
        adapter = CorvusAdapter(db_session)

        gm_event = {
            "type": "gm_update",
            "summary": {
                "worldEvents": [
                    {"key": "met_npc_1", "value": True},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(StoryFlag).where(
            StoryFlag.game_session_id == session.id,
            StoryFlag.flag_key == "met_npc_1",
        )
        result = await db_session.execute(stmt)
        flag = result.scalar_one_or_none()
        assert flag is not None
        assert flag.flag_value == True

    @pytest.mark.asyncio
    async def test_sync_flags_updates_existing(self, db_session):
        """AC-014: Duplicate flag_key updates instead of inserting (ON CONFLICT)."""
        session = await _create_test_session(db_session)
        flag = StoryFlag(
            game_session_id=session.id,
            flag_key="chapter_complete",
            flag_value=False,
        )
        db_session.add(flag)
        await db_session.flush()

        adapter = CorvusAdapter(db_session)
        gm_event = {
            "type": "gm_update",
            "summary": {
                "worldEvents": [
                    {"key": "chapter_complete", "value": True},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(StoryFlag).where(
            StoryFlag.game_session_id == session.id,
            StoryFlag.flag_key == "chapter_complete",
        )
        result = await db_session.execute(stmt)
        flags = result.scalars().all()
        assert len(flags) == 1  # No duplicate
        assert flags[0].flag_value == True  # Updated

    @pytest.mark.asyncio
    async def test_sync_flags_multiple(self, db_session):
        """AC-014: Multiple flags in one gm_update."""
        session = await _create_test_session(db_session)
        adapter = CorvusAdapter(db_session)

        gm_event = {
            "type": "gm_update",
            "summary": {
                "worldEvents": [
                    {"key": "flag_a", "value": 1},
                    {"key": "flag_b", "value": "hello"},
                    {"key": "flag_c", "value": {"nested": True}},
                ],
            },
        }

        await adapter.sync_world_state(session.id, gm_event)

        stmt = select(StoryFlag).where(
            StoryFlag.game_session_id == session.id,
        )
        result = await db_session.execute(stmt)
        flags = {f.flag_key: f for f in result.scalars().all()}
        assert len(flags) == 3
        assert flags["flag_a"].flag_value == 1
        assert flags["flag_b"].flag_value == "hello"
        assert flags["flag_c"].flag_value == {"nested": True}

    @pytest.mark.asyncio
    async def test_sync_flags_duplicate_no_error(self, db_session):
        """AC-014: Repeating the same flag_key doesn't cause an error."""
        session = await _create_test_session(db_session)
        adapter = CorvusAdapter(db_session)

        # First sync
        gm_event_1 = {
            "type": "gm_update",
            "summary": {"worldEvents": [{"key": "test_flag", "value": "first"}]},
        }
        await adapter.sync_world_state(session.id, gm_event_1)

        # Second sync with same key
        gm_event_2 = {
            "type": "gm_update",
            "summary": {"worldEvents": [{"key": "test_flag", "value": "second"}]},
        }
        await adapter.sync_world_state(session.id, gm_event_2)

        stmt = select(StoryFlag).where(
            StoryFlag.game_session_id == session.id,
            StoryFlag.flag_key == "test_flag",
        )
        result = await db_session.execute(stmt)
        flags = result.scalars().all()
        assert len(flags) == 1  # Still only one
        assert flags[0].flag_value == "second"  # Updated


# ── Integration: sync_world_state with stream_turn ──────────────────────


class TestSyncWorldStateIntegration:
    """Verify sync_world_state is triggered during stream_turn."""

    @pytest.mark.asyncio
    async def test_gm_update_triggers_sync(self, db_session):
        """AC-012/013/014: gm_update during stream_turn triggers sync_world_state."""
        test_user_id = uuid.uuid4()
        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="corvus-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        async def mock_stream(game_id, content):
            yield {"type": "token", "content": "hello"}
            yield {"type": "gm_update", "summary": {"statChanges": [{"stat": "affinity", "delta": 5, "character": "NPC1", "characterId": "c1"}]}}
            yield {"type": "stream_end"}

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.stream_message = mock_stream
            mock_get.return_value = mock_client

            adapter = CorvusAdapter(db_session)
            lines = []
            async for line in adapter.stream_turn(
                game_session_id=session.id,
                user_id=test_user_id,
                user_input="hi",
            ):
                lines.append(line)

        # Wait for async tasks to complete
        import asyncio
        await asyncio.sleep(0.1)

        # Verify NPC was synced
        stmt = select(SessionNpc).where(
            SessionNpc.game_session_id == session.id,
            SessionNpc.corvus_character_id == "c1",
        )
        result = await db_session.execute(stmt)
        npc = result.scalar_one_or_none()
        assert npc is not None
        assert npc.affinity == 5

    @pytest.mark.asyncio
    async def test_sync_error_does_not_crash_sse(self, db_session):
        """AC-012: sync_world_state error doesn't crash SSE stream."""
        test_user_id = uuid.uuid4()
        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="corvus-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        async def mock_stream(game_id, content):
            yield {"type": "token", "content": "text"}
            yield {"type": "gm_update", "summary": {"statChanges": [{"stat": "affinity", "delta": 1, "character": "NPC", "characterId": "x"}]}}
            yield {"type": "stream_end"}

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.stream_message = mock_stream
            mock_get.return_value = mock_client

            adapter = CorvusAdapter(db_session)
            lines = []
            async for line in adapter.stream_turn(
                game_session_id=session.id,
                user_id=test_user_id,
                user_input="hi",
            ):
                lines.append(line)

        # SSE should still have text and stream_end
        import json
        events = [json.loads(l[6:].strip()) for l in lines if l.startswith("data: ")]
        types = [e["type"] for e in events]
        assert "text" in types
        assert "stream_end" in types
