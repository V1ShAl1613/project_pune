from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.settings import AppSettings


@dataclass(slots=True)
class VectorPoint:
    id: str
    vector: list[float]
    payload: dict[str, Any]
    score: float = 0.0


@dataclass(slots=True)
class QdrantVectorStore:
    """Qdrant adapter with a memory fallback for local validation environments."""

    settings: AppSettings
    _memory_points: dict[str, list[VectorPoint]] = field(default_factory=dict)

    def _collection_name(self, collection_code: str) -> str:
        return f"{self.settings.knowledge_qdrant_collection_prefix}_{collection_code}"

    def health(self) -> dict[str, object]:
        client = self._client()
        if client is None:
            return {"status": "degraded", "mode": "memory"}
        try:
            client.get_collections()
            return {"status": "healthy", "mode": "qdrant"}
        except Exception as exc:
            return {"status": "degraded", "mode": "qdrant", "error": str(exc)}

    def ensure_collection(self, collection_code: str, vector_size: int | None = None) -> str:
        vector_size = vector_size or self.settings.knowledge_qdrant_vector_size
        collection_name = self._collection_name(collection_code)
        client = self._client()
        if client is None:
            self._memory_points.setdefault(collection_name, [])
            return collection_name

        try:
            from qdrant_client.http import models as qmodels  # type: ignore

            distance = getattr(qmodels.Distance, self.settings.knowledge_qdrant_distance.upper(), qmodels.Distance.COSINE)
            if collection_name not in {collection.name for collection in client.get_collections().collections}:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=qmodels.VectorParams(size=vector_size, distance=distance),
                    optimizers_config=qmodels.OptimizersConfigDiff(default_segment_number=self.settings.knowledge_qdrant_shards),
                    on_disk_payload=self.settings.knowledge_qdrant_on_disk_payload,
                )
        except Exception:
            self._memory_points.setdefault(collection_name, [])
        return collection_name

    def upsert_points(self, collection_code: str, points: list[VectorPoint], namespace: str = "default") -> list[str]:
        collection_name = self.ensure_collection(collection_code, len(points[0].vector) if points else None)
        client = self._client()
        if client is None:
            self._memory_points.setdefault(collection_name, []).extend(points)
            return [point.id for point in points]

        try:
            from qdrant_client.http import models as qmodels  # type: ignore

            client.upsert(
                collection_name=collection_name,
                points=[qmodels.PointStruct(id=point.id, vector=point.vector, payload={**point.payload, "namespace": namespace}) for point in points],
            )
        except Exception:
            self._memory_points.setdefault(collection_name, []).extend(points)
        return [point.id for point in points]

    def search(self, collection_code: str, query_vector: list[float], *, top_k: int = 5, namespace: str = "default", filters: dict[str, Any] | None = None) -> list[VectorPoint]:
        collection_name = self._collection_name(collection_code)
        client = self._client()
        if client is None:
            return self._memory_search(collection_name, query_vector, top_k, namespace, filters)

        try:
            from qdrant_client.http import models as qmodels  # type: ignore

            query_filter = self._build_filter(qmodels, filters or {}, namespace)
            results = client.search(collection_name=collection_name, query_vector=query_vector, limit=top_k, query_filter=query_filter)
            return [VectorPoint(id=str(result.id), vector=query_vector, payload=result.payload or {}, score=float(result.score or 0.0)) for result in results]
        except Exception:
            return self._memory_search(collection_name, query_vector, top_k, namespace, filters)

    def delete_document(self, collection_code: str, document_id: str) -> None:
        collection_name = self._collection_name(collection_code)
        client = self._client()
        if client is None:
            self._memory_points[collection_name] = [point for point in self._memory_points.get(collection_name, []) if point.payload.get("document_id") != document_id]
            return
        try:
            client.delete(collection_name=collection_name, points_selector={"filter": {"must": [{"key": "document_id", "match": {"value": document_id}}]}})
        except Exception:
            self._memory_points[collection_name] = [point for point in self._memory_points.get(collection_name, []) if point.payload.get("document_id") != document_id]

    def snapshot(self, collection_code: str) -> dict[str, object]:
        collection_name = self._collection_name(collection_code)
        client = self._client()
        if client is None:
            points = self._memory_points.get(collection_name, [])
            return {"collection": collection_name, "points": len(points), "mode": "memory"}
        try:
            info = client.get_collection(collection_name)
            return {
                "collection": collection_name,
                "points": info.points_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "mode": "qdrant",
            }
        except Exception as exc:
            points = self._memory_points.get(collection_name, [])
            return {"collection": collection_name, "points": len(points), "mode": "memory", "error": str(exc)}

    def _client(self):
        try:
            from qdrant_client import QdrantClient  # type: ignore

            return QdrantClient(url=self.settings.knowledge_qdrant_url, api_key=self.settings.knowledge_qdrant_api_key, timeout=self.settings.knowledge_qdrant_timeout_seconds)
        except Exception:
            return None

    def _build_filter(self, qmodels: Any, filters: dict[str, Any], namespace: str):
        conditions = [qmodels.FieldCondition(key="namespace", match=qmodels.MatchValue(value=namespace))]
        for key, value in filters.items():
            conditions.append(qmodels.FieldCondition(key=key, match=qmodels.MatchValue(value=value)))
        return qmodels.Filter(must=conditions)

    def _memory_search(self, collection_name: str, query_vector: list[float], top_k: int, namespace: str, filters: dict[str, Any] | None) -> list[VectorPoint]:
        points = self._memory_points.get(collection_name, [])
        filtered = [point for point in points if point.payload.get("namespace", namespace) == namespace]
        if filters:
            filtered = [point for point in filtered if all(point.payload.get(key) == value for key, value in filters.items())]
        scored = sorted(filtered, key=lambda point: self._dot_product(query_vector, point.vector), reverse=True)
        return [VectorPoint(id=point.id, vector=point.vector, payload=point.payload, score=self._dot_product(query_vector, point.vector)) for point in scored[:top_k]]

    def _dot_product(self, left: list[float], right: list[float]) -> float:
        size = min(len(left), len(right))
        return sum(left[index] * right[index] for index in range(size))
