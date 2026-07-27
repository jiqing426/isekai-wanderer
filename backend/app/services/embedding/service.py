"""Embedding service for vector search and memory recall.

Generates 1536-dim embeddings via OpenAI text-embedding-3-small.
Falls back to PostgreSQL full-text search when vector service is unavailable.
"""

import logging
from typing import List, Optional
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector

from app.core.config import settings
from app.llm.providers.openai_provider import OpenAIProvider
from app.models.memory import CharacterMemory

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for embedding generation and similarity search."""

    def __init__(self):
        self.provider: Optional[OpenAIProvider] = None
        self._available: Optional[bool] = None

    async def _get_provider(self) -> Optional[OpenAIProvider]:
        """Lazily initialize OpenAI provider for embeddings."""
        if self.provider is None:
            if settings.llm_provider == "mock" or not settings.openai_api_key:
                logger.warning("Embedding service unavailable: using mock/no API key")
                self._available = False
                return None
            try:
                self.provider = OpenAIProvider(
                    api_key=settings.openai_api_key,
                    model=settings.openai_model,
                )
                self._available = True
            except Exception as e:
                logger.error(f"Failed to initialize embedding provider: {e}")
                self._available = False
                return None
        return self.provider if self._available else None

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate 1536-dim embedding for text.

        Args:
            text: Text to embed.

        Returns:
            1536-dim vector as list of floats, or None if service unavailable.
        """
        provider = await self._get_provider()
        if provider is None:
            return None

        try:
            embedding = await provider.embed(text)
            if len(embedding) != 1536:
                logger.error(f"Invalid embedding dimension: {len(embedding)}")
                return None
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    async def recall_memories(
        self,
        db: AsyncSession,
        query: str,
        user_id: str,
        character_id: Optional[str] = None,
        session_id: Optional[str] = None,
        limit: int = 5,
        min_similarity: float = 0.3,
    ) -> List[dict]:
        """Recall memories by semantic similarity.

        Args:
            db: Database session.
            query: Query text to match.
            user_id: User ID filter (required).
            character_id: Optional character ID filter.
            session_id: Optional game session ID filter.
            limit: Max results (default 5).
            min_similarity: Minimum cosine similarity threshold (default 0.3).

        Returns:
            List of memories with similarity scores, sorted by relevance.
        """
        # Try vector search first
        memories = await self._vector_recall(
            db, query, user_id, character_id, session_id, limit, min_similarity
        )

        # Fallback to full-text search if vector search returns nothing
        if not memories:
            logger.info("Vector recall returned 0 results, falling back to full-text search")
            memories = await self._fulltext_recall(
                db, query, user_id, character_id, session_id, limit
            )

        return memories

    async def _vector_recall(
        self,
        db: AsyncSession,
        query: str,
        user_id: str,
        character_id: Optional[str],
        session_id: Optional[str],
        limit: int,
        min_similarity: float,
    ) -> List[dict]:
        """Vector similarity search using cosine distance."""
        # Generate query embedding
        query_embedding = await self.generate_embedding(query)
        if query_embedding is None:
            return []

        # Build query with cosine distance (<=>)
        # cosine_distance = 1 - cosine_similarity, so similarity = 1 - distance
        query_stmt = (
            select(
                CharacterMemory.id,
                CharacterMemory.memory_text,
                CharacterMemory.source,
                CharacterMemory.confidence,
                CharacterMemory.created_at,
                (1 - CharacterMemory.embedding.cosine_distance(query_embedding)).label("similarity"),
            )
            .where(CharacterMemory.user_id == user_id)
            .where(CharacterMemory.embedding.is_not(None))
        )

        # Apply optional filters
        if character_id:
            query_stmt = query_stmt.where(CharacterMemory.character_id == character_id)
        if session_id:
            query_stmt = query_stmt.where(CharacterMemory.source_session_id == session_id)

        # Order by similarity (highest first) and filter by threshold
        query_stmt = (
            query_stmt
            .having((1 - CharacterMemory.embedding.cosine_distance(query_embedding)) >= min_similarity)
            .order_by((1 - CharacterMemory.embedding.cosine_distance(query_embedding)).desc())
            .limit(limit)
        )

        result = await db.execute(query_stmt)
        rows = result.all()

        return [
            {
                "id": str(row.id),
                "content": row.memory_text,
                "source": row.source,
                "confidence": float(row.confidence) if row.confidence else 1.0,
                "similarity": float(row.similarity),
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]

    async def _fulltext_recall(
        self,
        db: AsyncSession,
        query: str,
        user_id: str,
        character_id: Optional[str],
        session_id: Optional[str],
        limit: int,
    ) -> List[dict]:
        """Fallback full-text search using ILIKE (LIKE case-insensitive).

        Uses simple pattern matching when vector search is unavailable.
        For production, consider using PostgreSQL tsvector with GIN index.
        """
        query_stmt = (
            select(
                CharacterMemory.id,
                CharacterMemory.memory_text,
                CharacterMemory.source,
                CharacterMemory.confidence,
                CharacterMemory.created_at,
            )
            .where(CharacterMemory.user_id == user_id)
            .where(CharacterMemory.memory_text.ilike(f"%{query}%"))
        )

        if character_id:
            query_stmt = query_stmt.where(CharacterMemory.character_id == character_id)
        if session_id:
            query_stmt = query_stmt.where(CharacterMemory.source_session_id == session_id)

        query_stmt = query_stmt.order_by(CharacterMemory.created_at.desc()).limit(limit)

        result = await db.execute(query_stmt)
        rows = result.all()

        # Assign fixed similarity score for full-text matches
        return [
            {
                "id": str(row.id),
                "content": row.memory_text,
                "source": row.source,
                "confidence": float(row.confidence) if row.confidence else 1.0,
                "similarity": 0.5,  # Fixed score for full-text fallback
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]

    async def close(self):
        """Close the embedding provider."""
        if self.provider:
            await self.provider.close()
            self.provider = None
            self._available = None


# Singleton instance
embedding_service = EmbeddingService()
