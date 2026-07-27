"""MemoryService - extracts memories from dialogue, stores with pgvector, performs KNN recall."""

import json
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import CharacterMemory
from app.services.llm.gateway import llm_gateway, LLMMessage


# Recall similarity threshold (matching spec S003: >0.8)
SIMILARITY_THRESHOLD = 0.8
MAX_RECALL_RESULTS = 3
MEMORY_COMPRESS_THRESHOLD = 50


class MemoryService:
    """Manages character memory extraction, storage, and recall using pgvector."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ---- Memory Extraction ----

    async def extract_and_store(
        self,
        user_id: UUID,
        character_id: UUID,
        dialogue_text: str,
        session_id: Optional[UUID] = None,
    ) -> List[CharacterMemory]:
        """
        Extract memorable facts from dialogue and store with embeddings.

        1. Use LLM to extract key facts from dialogue
        2. Generate embeddings for each fact
        3. Store in character_memories table
        """
        if not dialogue_text or len(dialogue_text.strip()) < 10:
            return []

        # Step 1: Extract memories via LLM
        import asyncio
        try:
            memory_texts = await asyncio.wait_for(
                llm_gateway.extract_memory(dialogue_text, character_name=str(character_id)),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            # LLM timeout, skip memory extraction
            return []

        if not memory_texts:
            return []

        # Step 2: Generate embeddings and store
        memories = []
        for mem_text in memory_texts:
            if not mem_text or len(mem_text.strip()) < 5:
                continue

            embedding = await self._get_embedding(mem_text)
            if not embedding:
                continue

            memory = CharacterMemory(
                user_id=user_id,
                character_id=character_id,
                memory_text=mem_text,
                embedding=embedding,
                source_session_id=session_id,
                confidence=Decimal("1.0"),
                is_compressed=False,
            )
            self.db.add(memory)
            memories.append(memory)

        await self.db.flush()
        return memories

    # ---- Memory Recall (KNN) ----

    async def recall(
        self,
        user_id: UUID,
        character_id: UUID,
        query_text: str,
        limit: int = MAX_RECALL_RESULTS,
    ) -> List[Dict[str, Any]]:
        """
        Recall relevant memories using pgvector KNN search.

        Only returns memories with similarity > SIMILARITY_THRESHOLD.
        """
        if not query_text:
            return []

        query_embedding = await self._get_embedding(query_text)
        if not query_embedding:
            return []

        # pgvector cosine similarity KNN query
        # cosine_distance returns 1 - cosine_similarity, so we filter where distance < (1 - threshold)
        max_distance = 1.0 - SIMILARITY_THRESHOLD

        stmt = text("""
            SELECT
                id,
                memory_text,
                confidence,
                is_compressed,
                created_at,
                1 - (embedding <=> :query_embedding::vector) AS similarity
            FROM character_memories
            WHERE user_id = :user_id
              AND character_id = :character_id
              AND 1 - (embedding <=> :query_embedding::vector) > :threshold
            ORDER BY embedding <=> :query_embedding::vector
            LIMIT :limit
        """)

        result = await self.db.execute(
            stmt,
            {
                "user_id": str(user_id),
                "character_id": str(character_id),
                "query_embedding": str(query_embedding),
                "threshold": SIMILARITY_THRESHOLD,
                "limit": limit,
            },
        )

        rows = result.fetchall()
        return [
            {
                "id": str(row[0]),
                "memory_text": row[1],
                "confidence": float(row[2]),
                "is_compressed": row[3],
                "created_at": row[4].isoformat() if row[4] else None,
                "similarity": float(row[5]),
            }
            for row in rows
        ]

    # ---- Memory Compression (P1 simplified) ----

    async def check_compression_needed(
        self, user_id: UUID, character_id: UUID
    ) -> bool:
        """Check if memory count exceeds compression threshold."""
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(CharacterMemory)
            .where(
                CharacterMemory.user_id == user_id,
                CharacterMemory.character_id == character_id,
                CharacterMemory.is_compressed == False,
            )
        )
        result = await self.db.execute(stmt)
        count = result.scalar()
        return count >= MEMORY_COMPRESS_THRESHOLD

    async def compress_memories(
        self, user_id: UUID, character_id: UUID
    ) -> int:
        """
        Compress old memories into summaries.

        Takes oldest uncompressed memories, merges them via LLM,
        stores as compressed summary, marks originals as compressed.
        Returns number of memories compressed.
        """
        # Get oldest uncompressed memories
        stmt = (
            select(CharacterMemory)
            .where(
                CharacterMemory.user_id == user_id,
                CharacterMemory.character_id == character_id,
                CharacterMemory.is_compressed == False,
            )
            .order_by(CharacterMemory.created_at.asc())
            .limit(20)
        )
        result = await self.db.execute(stmt)
        old_memories = list(result.scalars().all())

        if len(old_memories) < 10:
            return 0

        # Build summary via LLM
        memory_texts = [m.memory_text for m in old_memories]
        combined = "\n".join(f"- {t}" for t in memory_texts)

        summary_messages = [
            LLMMessage(
                role="system",
                content="Summarize these character memories into a concise paragraph. Keep key facts, preferences, and events.",
            ),
            LLMMessage(role="user", content=combined),
        ]
        summary_response = await llm_gateway.provider.complete(summary_messages, temperature=0.3, max_tokens=500)
        summary_text = summary_response.content

        # Create compressed memory
        summary_embedding = await self._get_embedding(summary_text)
        if summary_embedding:
            compressed = CharacterMemory(
                user_id=user_id,
                character_id=character_id,
                memory_text=summary_text,
                embedding=summary_embedding,
                confidence=Decimal("0.9"),
                is_compressed=True,
            )
            self.db.add(compressed)

        # Mark originals as compressed
        for mem in old_memories:
            mem.is_compressed = True

        await self.db.flush()
        return len(old_memories)

    # ---- Embedding Generation ----

    async def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text using LLM provider."""
        try:
            provider = llm_gateway.provider
            if hasattr(provider, "embed"):
                return await provider.embed(text)

            # Fallback: use mock embedding (random vector for dev/test)
            import hashlib
            import random
            hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
            random.seed(hash_val)
            return [random.gauss(0, 0.1) for _ in range(1536)]
        except Exception:
            return None

    # ---- Utility ----

    async def get_memory_count(
        self, user_id: UUID, character_id: UUID
    ) -> int:
        """Get total memory count for a user-character pair."""
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(CharacterMemory)
            .where(
                CharacterMemory.user_id == user_id,
                CharacterMemory.character_id == character_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
