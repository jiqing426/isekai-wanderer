"""MemoryService unit tests (mock-based, no pgvector required)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from decimal import Decimal

from app.services.narrative.memory_service import (
    MemoryService,
    SIMILARITY_THRESHOLD,
    MAX_RECALL_RESULTS,
    MEMORY_COMPRESS_THRESHOLD,
)


class TestMemoryServiceConstants:
    def test_similarity_threshold(self):
        assert SIMILARITY_THRESHOLD == 0.8

    def test_max_recall_results(self):
        assert MAX_RECALL_RESULTS == 3

    def test_compress_threshold(self):
        assert MEMORY_COMPRESS_THRESHOLD == 50


class TestGetEmbedding:
    @pytest.mark.asyncio
    async def test_mock_embedding_generation(self):
        """Mock embedding should return a 1536-dim vector."""
        db = MagicMock()
        service = MemoryService(db)
        embedding = await service._get_embedding("test text")

        assert embedding is not None
        assert len(embedding) == 1536
        assert all(isinstance(v, float) for v in embedding)

    @pytest.mark.asyncio
    async def test_embedding_deterministic(self):
        """Same text should produce same embedding (seeded random)."""
        db = MagicMock()
        service = MemoryService(db)
        e1 = await service._get_embedding("hello world")
        e2 = await service._get_embedding("hello world")
        assert e1 == e2

    @pytest.mark.asyncio
    async def test_different_text_different_embedding(self):
        """Different text should produce different embeddings."""
        import hashlib
        db = MagicMock()
        service = MemoryService(db)

        # Patch the LLM provider's embed to return hash-based distinct vectors
        async def mock_provider_embed(text):
            h = int(hashlib.md5(text.encode()).hexdigest(), 16)
            return [float(h % 1000) / 1000.0] * 1536

        with patch("app.services.narrative.memory_service.llm_gateway") as mock_gw:
            mock_gw.provider = MagicMock()
            mock_gw.provider.embed = mock_provider_embed
            e1 = await service._get_embedding("hello")
            e2 = await service._get_embedding("goodbye")
            assert e1 != e2


class TestRecallEmpty:
    @pytest.mark.asyncio
    async def test_recall_empty_query(self):
        """Empty query should return no results."""
        db = MagicMock()
        service = MemoryService(db)
        results = await service.recall(uuid4(), uuid4(), "")
        assert results == []
