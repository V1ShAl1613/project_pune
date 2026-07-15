from __future__ import annotations

from dataclasses import dataclass

from app.knowledge.embeddings.service import EmbeddingService
from app.knowledge.vectorstore.qdrant_store import QdrantVectorStore, VectorPoint


@dataclass(slots=True)
class Indexer:
    """Index chunk embeddings into the vector store."""

    embeddings: EmbeddingService
    vector_store: QdrantVectorStore

    def index(self, *, collection_code: str, namespace: str, chunks: list[dict[str, object]], model_name: str, provider_name: str) -> list[str]:
        texts = [str(chunk["content"]) for chunk in chunks]
        results = self.embeddings.batch_embed(texts, model_name=model_name, provider_name=provider_name)
        points = [
            VectorPoint(
                id=str(chunk["id"]),
                vector=result.vector,
                payload={**chunk, "namespace": namespace, "model_name": result.model_name, "provider_name": result.provider_name},
            )
            for chunk, result in zip(chunks, results, strict=False)
        ]
        return self.vector_store.upsert_points(collection_code, points, namespace=namespace)
