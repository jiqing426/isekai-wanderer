"""EmbeddingService — bge-small-zh-v1.5 local embedding for vector memory.

Generates 512-dimensional embeddings for text used in character_memories.
Provides KNN recall via pgvector cosine similarity search.

Uses sentence-transformers for the bge-small-zh-v1.5 model.
The model is loaded lazily on first use to avoid startup delay.
"""

import json
import logging
import os
import uuid
from typing import Optional

import numpy as np
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import CharacterMemory

logger = logging.getLogger(__name__)

# Similarity threshold for recall (1 - cosine_distance > 0.7)
SIMILARITY_THRESHOLD = 0.7
RECALL_LIMIT = 5
EMBEDDING_DIM = 512


class EmbeddingService:
    """Local embedding service using bge-small-zh-v1.5.

    Primary: HTTP API to host embedding service (port 8084).
    Fallback: in-process sentence-transformers if available.
    """

    _model = None  # Class-level singleton model
    _embedding_api_url = os.environ.get("EMBEDDING_API_URL", "http://10.255.0.1:8084")

    def __init__(self):
        self._model_instance = None

    def _get_model(self):
        """Lazily load the sentence-transformers model (fallback)."""
        if self._model_instance is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model_instance = SentenceTransformer("BAAI/bge-small-zh-v1.5")
                logger.info(f"[EmbeddingService] Model loaded, dim={self._model_instance.get_sentence_embedding_dimension()}")
            except ImportError:
                logger.warning("[EmbeddingService] sentence-transformers not installed, will use HTTP API")
                self._model_instance = None
            except Exception as e:
                logger.error(f"[EmbeddingService] Failed to load model: {e}")
                self._model_instance = None
        return self._model_instance

    def embed(self, text_input: str) -> Optional[list[float]]:
        """Generate a 512-dimensional embedding for the given text.

        Primary: HTTP API to host embedding service.
        Fallback: in-process sentence-transformers.
        Returns None if neither is available.
        """
        # Try HTTP API first
        try:
            import urllib.request
            data = json.dumps({"text": text_input}).encode('utf-8')
            req = urllib.request.Request(
                f"{self._embedding_api_url}/embed",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                embedding = result.get("embedding")
                if embedding:
                    return embedding
        except Exception as e:
            logger.warning(f"[EmbeddingService] HTTP API failed: {e}, trying local model")

        # Fallback to local model
        model = self._get_model()
        if model is None:
            return None

        try:
            vec = model.encode(text_input, normalize_embeddings=True)
            return vec.tolist()
        except Exception as e:
            logger.error(f"[EmbeddingService] Embedding failed: {e}")
            return None

    def embed_batch(self, texts: list[str]) -> list[Optional[list[float]]]:
        """Generate embeddings for multiple texts."""
        # Try HTTP API first (batch)
        try:
            import urllib.request
            data = json.dumps({"texts": texts}).encode('utf-8')
            req = urllib.request.Request(
                f"{self._embedding_api_url}/embed",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                embeddings = result.get("embedding")
                if embeddings and isinstance(embeddings[0], list):
                    return embeddings
                elif embeddings:
                    return [embeddings]
        except Exception as e:
            logger.warning(f"[EmbeddingService] HTTP API batch failed: {e}, trying local model")

        # Fallback to local model
        model = self._get_model()
        if model is None:
            return [None] * len(texts)

        try:
            vecs = model.encode(texts, normalize_embeddings=True)
            return [v.tolist() for v in vecs]
        except Exception as e:
            logger.error(f"[EmbeddingService] Batch embedding failed: {e}")
            return [None] * len(texts)

    async def write_memory(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        character_id: uuid.UUID,
        memory_text: str,
        source_session_id: Optional[uuid.UUID] = None,
    ) -> Optional[CharacterMemory]:
        """Write a memory with embedding to character_memories table.

        Generates embedding and stores it. Returns the created CharacterMemory
        or None if embedding failed.
        """
        embedding = self.embed(memory_text)

        memory = CharacterMemory(
            user_id=user_id,
            character_id=character_id,
            memory_text=memory_text,
            embedding=embedding,
            source="corvus_dialogue",
            source_session_id=None,  # FK points to game_sessions, not corvus_game_sessions
            confidence=1.0,
        )
        db.add(memory)
        await db.flush()
        logger.info(
            f"[EmbeddingService] Memory written: user={user_id}, char={character_id}, "
            f"embedding={'set' if embedding else 'None'}"
        )
        return memory

    async def recall(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        character_id: uuid.UUID,
        query_text: str,
        limit: int = RECALL_LIMIT,
        threshold: float = SIMILARITY_THRESHOLD,
    ) -> list[str]:
        """Recall relevant memories via pgvector KNN search.

        Filters by user_id AND character_id for isolation.
        Uses cosine distance: 1 - (embedding <=> query) > threshold.

        Returns up to `limit` memory_text strings sorted by similarity.
        """
        query_embedding = self.embed(query_text)
        if query_embedding is None:
            logger.info("[EmbeddingService] Recall: no embedding available, returning empty")
            return []

        try:
            # pgvector cosine distance search
            # embedding <=> query means cosine distance
            # similarity = 1 - distance
            # We want similarity > threshold, i.e., distance < 1 - threshold
            stmt = (
                select(
                    CharacterMemory.memory_text,
                    (1 - CharacterMemory.embedding.cosine_distance(query_embedding)).label("similarity"),
                )
                .where(
                    CharacterMemory.user_id == user_id,
                    CharacterMemory.character_id == character_id,
                    CharacterMemory.embedding.isnot(None),
                )
                .order_by(CharacterMemory.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )

            result = await db.execute(stmt)
            rows = result.all()

            # Filter by threshold
            recalled = [row[0] for row in rows if row[1] > threshold]
            logger.info(
                f"[EmbeddingService] Recall: user={user_id}, char={character_id}, "
                f"found={len(rows)}, filtered={len(recalled)}"
            )
            return recalled
        except Exception as e:
            logger.error(f"[EmbeddingService] Recall failed: {e}")
            return []


# Module-level singleton
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the singleton EmbeddingService."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
