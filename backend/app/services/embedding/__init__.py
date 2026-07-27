"""Embedding service for memory recall.

Provides vector embedding generation and similarity search,
with automatic fallback to full-text search when vector service is unavailable.
"""

from .service import EmbeddingService, embedding_service

__all__ = ["EmbeddingService", "embedding_service"]
