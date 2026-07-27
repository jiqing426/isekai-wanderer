"""Unit tests for embedding service (DEV-018).

Tests vector embedding generation, similarity recall, and full-text fallback.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from decimal import Decimal

from app.services.embedding.service import EmbeddingService
from app.services.embedding import embedding_service


class TestEmbeddingService:
    """Tests for EmbeddingService class."""

    @pytest.mark.asyncio
    async def test_generate_embedding_success(self):
        """Test successful embedding generation with OpenAI provider."""
        service = EmbeddingService()
        mock_embedding = [0.1] * 1536  # 1536-dim vector

        with patch.object(service, '_get_provider') as mock_get_provider:
            mock_provider = AsyncMock()
            mock_provider.embed.return_value = mock_embedding
            mock_get_provider.return_value = mock_provider

            result = await service.generate_embedding("test text")

            assert result == mock_embedding
            assert len(result) == 1536
            mock_provider.embed.assert_called_once_with("test text")

    @pytest.mark.asyncio
    async def test_generate_embedding_provider_unavailable(self):
        """Test embedding generation when provider is unavailable."""
        service = EmbeddingService()

        with patch.object(service, '_get_provider') as mock_get_provider:
            mock_get_provider.return_value = None

            result = await service.generate_embedding("test text")

            assert result is None

    @pytest.mark.asyncio
    async def test_generate_embedding_invalid_dimension(self):
        """Test embedding generation with invalid dimension."""
        service = EmbeddingService()
        mock_embedding = [0.1] * 100  # Wrong dimension

        with patch.object(service, '_get_provider') as mock_get_provider:
            mock_provider = AsyncMock()
            mock_provider.embed.return_value = mock_embedding
            mock_get_provider.return_value = mock_provider

            result = await service.generate_embedding("test text")

            assert result is None  # Should reject invalid dimension

    @pytest.mark.asyncio
    async def test_generate_embedding_exception(self):
        """Test embedding generation when provider raises exception."""
        service = EmbeddingService()

        with patch.object(service, '_get_provider') as mock_get_provider:
            mock_provider = AsyncMock()
            mock_provider.embed.side_effect = Exception("API error")
            mock_get_provider.return_value = mock_provider

            result = await service.generate_embedding("test text")

            assert result is None

    @pytest.mark.asyncio
    async def test_recall_memories_vector_search(self):
        """Test vector-based memory recall."""
        service = EmbeddingService()
        user_id = str(uuid4())
        query = "test query"

        # Mock database session
        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_rows = [
            MagicMock(
                id=uuid4(),
                memory_text="memory 1",
                source="dialogue",
                confidence=Decimal("1.0"),
                created_at=None,
                similarity=0.9,
            ),
            MagicMock(
                id=uuid4(),
                memory_text="memory 2",
                source="game_event",
                confidence=Decimal("0.8"),
                created_at=None,
                similarity=0.7,
            ),
        ]
        mock_result.all.return_value = mock_rows
        mock_db.execute.return_value = mock_result

        # Mock embedding generation
        with patch.object(service, 'generate_embedding') as mock_gen_embed:
            mock_gen_embed.return_value = [0.1] * 1536

            result = await service.recall_memories(
                db=mock_db,
                query=query,
                user_id=user_id,
                limit=5,
            )

            assert len(result) == 2
            assert result[0]["content"] == "memory 1"
            assert result[0]["similarity"] == 0.9
            assert result[1]["content"] == "memory 2"
            assert result[1]["similarity"] == 0.7
            mock_gen_embed.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_recall_memories_fulltext_fallback(self):
        """Test full-text fallback when vector search returns nothing."""
        service = EmbeddingService()
        user_id = str(uuid4())
        query = "test query"

        # Mock database session
        mock_db = AsyncMock()

        # First call (vector) returns empty, second call (fulltext) returns results
        mock_result_vector = MagicMock()
        mock_result_vector.all.return_value = []

        mock_result_fulltext = MagicMock()
        mock_rows = [
            MagicMock(
                id=uuid4(),
                memory_text="test memory content",
                source="dialogue",
                confidence=Decimal("1.0"),
                created_at=None,
            ),
        ]
        mock_result_fulltext.all.return_value = mock_rows

        mock_db.execute.side_effect = [mock_result_vector, mock_result_fulltext]

        with patch.object(service, 'generate_embedding') as mock_gen_embed:
            mock_gen_embed.return_value = [0.1] * 1536

            result = await service.recall_memories(
                db=mock_db,
                query=query,
                user_id=user_id,
                limit=5,
            )

            assert len(result) == 1
            assert result[0]["content"] == "test memory content"
            assert result[0]["similarity"] == 0.5  # Fixed score for fulltext

    @pytest.mark.asyncio
    async def test_recall_memories_with_filters(self):
        """Test memory recall with character_id and session_id filters."""
        service = EmbeddingService()
        user_id = str(uuid4())
        character_id = str(uuid4())
        session_id = str(uuid4())
        query = "test query"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_db.execute.return_value = mock_result

        with patch.object(service, 'generate_embedding') as mock_gen_embed:
            mock_gen_embed.return_value = [0.1] * 1536

            result = await service.recall_memories(
                db=mock_db,
                query=query,
                user_id=user_id,
                character_id=character_id,
                session_id=session_id,
                limit=5,
            )

            assert result == []
            # Vector search returns empty, fallback runs too → execute called twice
            assert mock_db.execute.call_count >= 1

    @pytest.mark.asyncio
    async def test_recall_memories_embedding_unavailable(self):
        """Test recall when embedding generation fails."""
        service = EmbeddingService()
        user_id = str(uuid4())
        query = "test query"

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_rows = [
            MagicMock(
                id=uuid4(),
                memory_text="fallback memory",
                source="dialogue",
                confidence=Decimal("1.0"),
                created_at=None,
            ),
        ]
        mock_result.all.return_value = mock_rows
        mock_db.execute.return_value = mock_result

        with patch.object(service, 'generate_embedding') as mock_gen_embed:
            mock_gen_embed.return_value = None  # Embedding unavailable

            result = await service.recall_memories(
                db=mock_db,
                query=query,
                user_id=user_id,
                limit=5,
            )

            # Should fallback to fulltext
            assert len(result) == 1
            assert result[0]["content"] == "fallback memory"
            assert result[0]["similarity"] == 0.5

    @pytest.mark.asyncio
    async def test_close_provider(self):
        """Test closing the embedding provider."""
        service = EmbeddingService()
        mock_provider = AsyncMock()
        service.provider = mock_provider
        service._available = True

        await service.close()

        mock_provider.close.assert_called_once()
        assert service.provider is None
        assert service._available is None


class TestEmbeddingServiceSingleton:
    """Tests for the global embedding_service instance."""

    def test_singleton_exists(self):
        """Test that embedding_service singleton is available."""
        assert embedding_service is not None
        assert isinstance(embedding_service, EmbeddingService)
