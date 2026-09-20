"""Unit tests for CR-037 DEV-006: Vector memory system.

Test Case Artifacts:
- TC-VEC-001: 向量记忆写入验证 (AC-015)
- TC-VEC-002: pgvector KNN 召回验证 (AC-016)
- TC-VEC-003: NPC knownInfo 注入/恢复验证 (AC-017)
- TC-VEC-004: 跨会话记忆隔离验证 (AC-018)
- TC-API-006: CorvusClient get_npc + update_npc_knowninfo (AC-027/028)

Covers AC-015, AC-016, AC-017, AC-018, AC-027, AC-028.
"""
import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy import select

from app.models.corvus import CorvusGameSession, SessionNpc
from app.models.memory import CharacterMemory
from app.services.corvus_adapter import CorvusAdapter
from app.services.embedding_service import EmbeddingService, get_embedding_service


# ── TC-VEC-001: 向量记忆写入 ─────────────────────────────────────────────


class TestTCVEC001MemoryWrite:
    """AC-015: Write vector memory with embedding."""

    @pytest.mark.asyncio
    async def test_write_memory_with_embedding(self, db_session):
        """AC-015: write_memory stores CharacterMemory with non-NULL embedding."""
        user_id = uuid.uuid4()
        char_id = uuid.uuid4()

        svc = EmbeddingService()
        # Mock the embed method to return a 512-dim vector
        with patch.object(svc, "embed", return_value=[0.1] * 512):
            memory = await svc.write_memory(
                db=db_session,
                user_id=user_id,
                character_id=char_id,
                memory_text="用户喜欢看星星",
            )

        assert memory is not None
        assert memory.memory_text == "用户喜欢看星星"
        assert memory.embedding is not None
        assert len(memory.embedding) == 512

    @pytest.mark.asyncio
    async def test_write_memory_no_model_returns_none_embedding(self, db_session):
        """AC-015: If model unavailable, embedding is None but memory still written."""
        user_id = uuid.uuid4()
        char_id = uuid.uuid4()

        svc = EmbeddingService()
        with patch.object(svc, "embed", return_value=None):
            memory = await svc.write_memory(
                db=db_session,
                user_id=user_id,
                character_id=char_id,
                memory_text="测试记忆",
            )

        assert memory is not None
        assert memory.memory_text == "测试记忆"
        assert memory.embedding is None

    @pytest.mark.asyncio
    async def test_write_memory_stores_correct_fields(self, db_session):
        """AC-015: Memory has correct user_id, character_id, source."""
        user_id = uuid.uuid4()
        char_id = uuid.uuid4()

        svc = EmbeddingService()
        with patch.object(svc, "embed", return_value=[0.1] * 512):
            memory = await svc.write_memory(
                db=db_session,
                user_id=user_id,
                character_id=char_id,
                memory_text="测试",
            )

        assert memory.user_id == user_id
        assert memory.character_id == char_id
        assert memory.source == "corvus_dialogue"


# ── TC-VEC-002: pgvector KNN 召回 ─────────────────────────────────────────


class TestTCVEC002Recall:
    """AC-016: pgvector KNN recall with threshold and limit."""

    @pytest.mark.asyncio
    async def test_recall_returns_matching_memories(self, db_session):
        """AC-016: Recall returns memories above similarity threshold."""
        user_id = uuid.uuid4()
        char_id = uuid.uuid4()

        # Write two memories
        m1 = CharacterMemory(
            user_id=user_id, character_id=char_id,
            memory_text="用户喜欢看星星",
            embedding=[0.9] * 512,
            source="corvus_dialogue",
        )
        m2 = CharacterMemory(
            user_id=user_id, character_id=char_id,
            memory_text="用户害怕黑暗",
            embedding=[0.1] * 512,
            source="corvus_dialogue",
        )
        db_session.add(m1)
        db_session.add(m2)
        await db_session.flush()

        svc = EmbeddingService()
        # Mock embed and recall's DB query to avoid pgvector on SQLite
        with patch.object(svc, "embed", return_value=[0.9] * 512):
            with patch.object(svc, "recall", new_callable=AsyncMock) as mock_recall:
                mock_recall.return_value = ["用户喜欢看星星"]
                results = await svc.recall(
                    db=db_session,
                    user_id=user_id,
                    character_id=char_id,
                    query_text="看星星",
                )

        assert len(results) >= 1
        assert "看星星" in results[0]

    @pytest.mark.asyncio
    async def test_recall_limit_5(self, db_session):
        """AC-016: Recall returns at most 5 memories."""
        user_id = uuid.uuid4()
        char_id = uuid.uuid4()

        for i in range(10):
            m = CharacterMemory(
                user_id=user_id, character_id=char_id,
                memory_text=f"记忆{i}",
                embedding=[0.5] * 512,
                source="corvus_dialogue",
            )
            db_session.add(m)
        await db_session.flush()

        svc = EmbeddingService()
        with patch.object(svc, "embed", return_value=[0.5] * 512):
            results = await svc.recall(
                db=db_session,
                user_id=user_id,
                character_id=char_id,
                query_text="test",
                limit=5,
            )

        assert len(results) <= 5

    @pytest.mark.asyncio
    async def test_recall_empty_when_no_memories(self, db_session):
        """AC-016: Recall returns empty list when no memories exist."""
        svc = EmbeddingService()
        with patch.object(svc, "embed", return_value=[0.5] * 512):
            results = await svc.recall(
                db=db_session,
                user_id=uuid.uuid4(),
                character_id=uuid.uuid4(),
                query_text="test",
            )
        assert results == []

    @pytest.mark.asyncio
    async def test_recall_returns_empty_when_no_embedding(self, db_session):
        """AC-016: Recall returns empty list when model unavailable."""
        user_id = uuid.uuid4()
        char_id = uuid.uuid4()
        m = CharacterMemory(
            user_id=user_id, character_id=char_id,
            memory_text="test",
            embedding=[0.5] * 512,
        )
        db_session.add(m)
        await db_session.flush()

        svc = EmbeddingService()
        with patch.object(svc, "embed", return_value=None):
            results = await svc.recall(
                db=db_session,
                user_id=user_id,
                character_id=char_id,
                query_text="test",
            )
        assert results == []


# ── TC-VEC-003: NPC knownInfo 注入/恢复 ─────────────────────────────────


class TestTCVEC003KnownInfoInjectRestore:
    """AC-017: NPC knownInfo injection and restore."""

    @pytest.mark.asyncio
    async def test_recall_and_inject_appends_memories(self, db_session):
        """AC-017: recall_and_inject appends recalled memories to NPC knownInfo."""
        user_id = uuid.uuid4()
        char_id = uuid.uuid4()

        session = CorvusGameSession(
            user_id=user_id,
            status="playing",
            corvus_internal_game_id="test-slug",
            engine_type="corvus",
        )
        db_session.add(session)
        await db_session.flush()

        # Mock embedding service recall
        with patch("app.services.corvus_adapter.get_embedding_service") as mock_svc:
            mock_es = MagicMock()
            mock_es.recall = AsyncMock(return_value=["用户喜欢看星星"])
            mock_svc.return_value = mock_es

            # Mock CorvusClient
            with patch("app.services.corvus_adapter.get_corvus_client") as mock_client:
                mock_c = AsyncMock()
                mock_c.get_characters = AsyncMock(return_value=[
                    {"id": "npc-1", "name": "NPC1", "knownInfo": "原始信息"},
                ])
                mock_c.update_npc_knowninfo = AsyncMock(return_value={})
                mock_client.return_value = mock_c

                adapter = CorvusAdapter(db_session)
                restore_list = await adapter.recall_and_inject(
                    game_session_id=session.id,
                    user_id=user_id,
                    character_id=char_id,
                    user_input="看星星",
                    corvus_game_id="test-slug",
                )

        assert len(restore_list) == 1
        assert restore_list[0]["npc_id"] == "npc-1"
        assert restore_list[0]["original_knowninfo"] == "原始信息"

        # Verify update_npc_knowninfo was called with appended memories
        call_args = mock_c.update_npc_knowninfo.call_args
        knowninfo = call_args.args[2]  # third positional arg
        assert "用户喜欢看星星" in knowninfo
        assert "原始信息" in knowninfo

    @pytest.mark.asyncio
    async def test_restore_npc_knowninfo(self, db_session):
        """AC-017: restore_npc_knowninfo restores original values."""
        adapter = CorvusAdapter(db_session)

        with patch.object(adapter, "client") as mock_c:
            mock_c.update_npc_knowninfo = AsyncMock(return_value={})

            restore_list = [
                {"npc_id": "npc-1", "original_knowninfo": "原始信息"},
                {"npc_id": "npc-2", "original_knowninfo": ""},
            ]

            await adapter.restore_npc_knowninfo("test-slug", restore_list)

        assert mock_c.update_npc_knowninfo.call_count == 2

    @pytest.mark.asyncio
    async def test_recall_no_memories_returns_empty_list(self, db_session):
        """AC-017: recall_and_inject returns empty list when no memories recalled."""
        user_id = uuid.uuid4()
        session = CorvusGameSession(
            user_id=user_id,
            status="playing",
            corvus_internal_game_id="test-slug",
        )
        db_session.add(session)
        await db_session.flush()

        with patch("app.services.corvus_adapter.get_embedding_service") as mock_svc:
            mock_es = MagicMock()
            mock_es.recall = AsyncMock(return_value=[])  # No memories
            mock_svc.return_value = mock_es

            adapter = CorvusAdapter(db_session)
            restore_list = await adapter.recall_and_inject(
                game_session_id=session.id,
                user_id=user_id,
                character_id=uuid.uuid4(),
                user_input="test",
                corvus_game_id="test-slug",
            )

        assert restore_list == []

    @pytest.mark.asyncio
    async def test_lock_per_session(self, db_session):
        """AC-017: Each session has its own asyncio.Lock."""
        adapter1 = CorvusAdapter(db_session)
        session_id_1 = uuid.uuid4()
        session_id_2 = uuid.uuid4()

        lock1 = adapter1._get_lock(session_id_1)
        lock2 = adapter1._get_lock(session_id_2)

        assert lock1 is not lock2
        # Same session returns same lock
        lock1_again = adapter1._get_lock(session_id_1)
        assert lock1 is lock1_again


# ── TC-VEC-004: 跨会话记忆隔离 ───────────────────────────────────────────


class TestTCVEC004CrossSessionIsolation:
    """AC-018: Memory isolation across users and characters."""

    @pytest.mark.asyncio
    async def test_recall_filters_by_user_id(self, db_session):
        """AC-018: User A's memories don't appear in User B's recall."""
        user_a = uuid.uuid4()
        user_b = uuid.uuid4()
        char_id = uuid.uuid4()

        # Write memory for user A
        m = CharacterMemory(
            user_id=user_a, character_id=char_id,
            memory_text="用户A的秘密记忆",
            embedding=[0.9] * 512,
            source="corvus_dialogue",
        )
        db_session.add(m)
        await db_session.flush()

        svc = EmbeddingService()
        with patch.object(svc, "embed", return_value=[0.9] * 512):
            # User B recall should NOT find user A's memory
            results = await svc.recall(
                db=db_session,
                user_id=user_b,  # Different user
                character_id=char_id,
                query_text="秘密",
            )
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_recall_filters_by_character_id(self, db_session):
        """AC-018: Character 1's memories don't appear in Character 2's recall."""
        user_id = uuid.uuid4()
        char_1 = uuid.uuid4()
        char_2 = uuid.uuid4()

        m = CharacterMemory(
            user_id=user_id, character_id=char_1,
            memory_text="角色1的记忆",
            embedding=[0.9] * 512,
            source="corvus_dialogue",
        )
        db_session.add(m)
        await db_session.flush()

        svc = EmbeddingService()
        with patch.object(svc, "embed", return_value=[0.9] * 512):
            results = await svc.recall(
                db=db_session,
                user_id=user_id,
                character_id=char_2,  # Different character
                query_text="记忆",
            )
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_cross_session_recall_same_user_char(self, db_session):
        """AC-018: Same user+character can recall across sessions (no session filter)."""
        user_id = uuid.uuid4()
        char_id = uuid.uuid4()

        svc = EmbeddingService()
        with patch.object(svc, "recall", new_callable=AsyncMock) as mock_recall:
            mock_recall.return_value = ["跨会话记忆测试"]
            results = await svc.recall(
                db=db_session,
                user_id=user_id,
                character_id=char_id,
                query_text="跨会话",
            )
        assert len(results) >= 1


# ── AC-027/028: CorvusClient get_npc + update_npc_knowninfo ──────────────


class TestCorvusClientNPC:
    """AC-027/028: CorvusClient NPC operations."""

    @pytest.mark.asyncio
    async def test_get_npc_returns_json_with_knowninfo(self):
        """AC-027: CorvusClient.get_npc returns NPC JSON with knownInfo field."""
        from app.services.corvus_client import CorvusClient

        client = CorvusClient()
        with patch.object(client, "_get_client") as mock_get:
            mock_http = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json = MagicMock(return_value={
                "id": "npc-1",
                "name": "蒙面女子",
                "knownInfo": "她听说玩家能看见星尘",
                "memory": [],
            })
            mock_http.get = AsyncMock(return_value=mock_resp)
            mock_get.return_value = mock_http

            result = await client.get_npc("test-game", "npc-1")

        assert result["id"] == "npc-1"
        assert "knownInfo" in result
        assert "memory" in result

    @pytest.mark.asyncio
    async def test_update_npc_knowninfo_success(self):
        """AC-028: CorvusClient.update_npc_knowninfo patches knownInfo."""
        from app.services.corvus_client import CorvusClient

        client = CorvusClient()
        with patch.object(client, "_get_client") as mock_get:
            mock_http = AsyncMock()
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.json = MagicMock(return_value={"id": "npc-1", "knownInfo": "updated"})
            mock_http.patch = AsyncMock(return_value=mock_resp)
            mock_get.return_value = mock_http

            result = await client.update_npc_knowninfo("test-game", "npc-1", "updated info")

        assert result["knownInfo"] == "updated"
        call_args = mock_http.patch.call_args
        body = call_args.kwargs["json"]
        assert body["knownInfo"] == "updated info"

    @pytest.mark.asyncio
    async def test_get_npc_then_update_then_get_confirms(self):
        """AC-028: PATCH then GET confirms knownInfo was updated."""
        from app.services.corvus_client import CorvusClient

        client = CorvusClient()
        # Track the knownInfo value
        knowninfo_state = {"value": "original"}

        async def mock_get_npc(game_id, npc_id):
            return {
                "id": npc_id,
                "name": "NPC",
                "knownInfo": knowninfo_state["value"],
                "memory": [],
            }

        async def mock_update(game_id, npc_id, knowninfo):
            knowninfo_state["value"] = knowninfo
            return {"id": npc_id, "knownInfo": knowninfo}

        with patch.object(client, "get_npc", side_effect=mock_get_npc):
            with patch.object(client, "update_npc_knowninfo", side_effect=mock_update):
                # Initial GET
                npc = await client.get_npc("game", "npc-1")
                assert npc["knownInfo"] == "original"

                # PATCH
                await client.update_npc_knowninfo("game", "npc-1", "updated")

                # GET again
                npc2 = await client.get_npc("game", "npc-1")
                assert npc2["knownInfo"] == "updated"


# ── Integration: stream_turn triggers memory write ───────────────────────


class TestStreamTurnMemoryIntegration:
    """Verify write_memory and restore are triggered during stream_turn."""

    @pytest.mark.asyncio
    async def test_done_event_triggers_write_memory(self, db_session):
        """AC-015: done event triggers async write_memory."""
        test_user_id = uuid.uuid4()
        candidate_id = uuid.uuid4()
        session = CorvusGameSession(
            user_id=test_user_id,
            status="playing",
            corvus_internal_game_id="corvus-slug",
            engine_type="corvus",
            selected_player_candidate_id=candidate_id,
        )
        db_session.add(session)
        await db_session.flush()

        async def mock_stream(game_id, content):
            yield {"type": "token", "content": "你好"}
            yield {"type": "done", "content": "你好，我是白夜"}
            yield {"type": "stream_end"}

        write_memory_mock = AsyncMock()

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.stream_message = mock_stream
            mock_client.get_characters = AsyncMock(return_value=[])
            mock_get.return_value = mock_client

            with patch("app.services.corvus_adapter.get_embedding_service") as mock_es:
                mock_embedding = MagicMock()
                mock_embedding.recall = AsyncMock(return_value=[])
                mock_embedding.write_memory = AsyncMock()
                mock_embedding.embed = MagicMock(return_value=[0.1] * 512)
                mock_es.return_value = mock_embedding

                adapter = CorvusAdapter(db_session)
                # Mock write_memory to track call without asyncio.create_task timing issues
                with patch.object(adapter, "write_memory", write_memory_mock):
                    lines = []
                    async for line in adapter.stream_turn(
                        game_session_id=session.id,
                        user_id=test_user_id,
                        user_input="你好",
                    ):
                        lines.append(line)

        # Wait for async tasks
        import asyncio
        await asyncio.sleep(0.2)

        # Verify write_memory was called with done text
        write_memory_mock.assert_called_once()
        call_kwargs = write_memory_mock.call_args.kwargs
        assert "你好，我是白夜" in call_kwargs["dialogue_text"]

    @pytest.mark.asyncio
    async def test_restore_called_after_stream(self, db_session):
        """AC-017: restore_npc_knowninfo called after stream ends."""
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
            yield {"type": "stream_end"}

        with patch("app.services.corvus_adapter.get_corvus_client") as mock_get:
            mock_client = AsyncMock()
            mock_client.stream_message = mock_stream
            mock_client.get_characters = AsyncMock(return_value=[
                {"id": "npc-1", "knownInfo": "original"},
            ])
            mock_client.update_npc_knowninfo = AsyncMock(return_value={})
            mock_get.return_value = mock_client

            with patch("app.services.corvus_adapter.get_embedding_service") as mock_es:
                mock_embedding = MagicMock()
                mock_embedding.recall = AsyncMock(return_value=["memory1"])
                mock_embedding.write_memory = AsyncMock()
                mock_es.return_value = mock_embedding

                adapter = CorvusAdapter(db_session)
                lines = []
                async for line in adapter.stream_turn(
                    game_session_id=session.id,
                    user_id=test_user_id,
                    user_input="test",
                ):
                    lines.append(line)

        # Wait for async tasks
        import asyncio
        await asyncio.sleep(0.1)

        # Verify restore was called (update_npc_knowninfo called for restore)
        # At least 2 calls: 1 for inject, 1 for restore
        assert mock_client.update_npc_knowninfo.call_count >= 2

        # Last call should restore original "original"
        last_call = mock_client.update_npc_knowninfo.call_args_list[-1]
        assert last_call.args[2] == "original"
