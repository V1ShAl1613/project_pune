from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.settings import AppSettings
from app.knowledge.embeddings.service import EmbeddingService
from app.knowledge.ranking.engine import RankingEngine
from app.knowledge.schemas import KnowledgeSearchResult
from app.knowledge.vectorstore.qdrant_store import QdrantVectorStore, VectorPoint


@dataclass(slots=True)
class RetrievalEngine:
    """Combine vector, keyword, and metadata retrieval strategies."""

    settings: AppSettings
    embeddings: EmbeddingService
    vector_store: QdrantVectorStore
    ranking: RankingEngine

    def search(self, *, query: str, collection_code: str, top_k: int, threshold: float, namespace: str = "default", filters: dict[str, Any] | None = None) -> list[KnowledgeSearchResult]:
        query_vector = self.embeddings.embed_text(query, model_name=self.settings.knowledge_default_embedding_model).vector
        vector_hits = self.vector_store.search(collection_code, query_vector, top_k=max(top_k, 20), namespace=namespace, filters=filters)
        keyword_hits = self._keyword_search(collection_code, query, top_k, namespace, filters)
        merged = self.ranking.rank(query, vector_hits, keyword_hits, top_k=top_k, threshold=threshold)
        return [
            KnowledgeSearchResult(
                document_id=point.payload["document_id"],
                chunk_id=point.payload["chunk_id"],
                collection_id=point.payload["collection_id"],
                score=point.score,
                reranked_score=point.payload.get("reranked_score", point.score),
                content=point.payload.get("content", ""),
                title=point.payload.get("title", ""),
                file_name=point.payload.get("file_name", ""),
                file_type=point.payload.get("file_type", ""),
                source_id=point.payload.get("source_id"),
                metadata={k: v for k, v in point.payload.items() if k not in {"document_id", "chunk_id", "collection_id", "content", "title", "file_name", "file_type", "source_id"}},
            )
            for point in merged
            if point.score >= threshold
        ]

    def _keyword_search(self, collection_code: str, query: str, top_k: int, namespace: str, filters: dict[str, Any] | None) -> list[VectorPoint]:
        collection = self.vector_store.snapshot(collection_code)
        if collection.get("mode") == "memory":
            return self.vector_store.search(collection_code, self.embeddings.embed_text(query).vector, top_k=top_k, namespace=namespace, filters=filters)
        return []
