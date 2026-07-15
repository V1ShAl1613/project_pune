from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.knowledge.vectorstore.qdrant_store import VectorPoint


@dataclass(slots=True)
class RankingEngine:
    """Re-rank retrieval results using score, metadata, and recency boosts."""

    def rank(self, query: str, vector_hits: list[VectorPoint], keyword_hits: list[VectorPoint], *, top_k: int, threshold: float) -> list[VectorPoint]:
        merged: dict[str, VectorPoint] = {}
        for point in [*vector_hits, *keyword_hits]:
            score = self._boost_score(point, query)
            current = merged.get(point.id)
            if current is None or score > current.score:
                merged[point.id] = VectorPoint(id=point.id, vector=point.vector, payload={**point.payload, "reranked_score": score}, score=score)
        ranked = sorted(merged.values(), key=lambda item: item.score, reverse=True)
        return [point for point in ranked[:top_k] if point.score >= threshold]

    def _boost_score(self, point: VectorPoint, query: str) -> float:
        score = float(point.score)
        payload = point.payload or {}
        if payload.get("title") and str(payload["title"]).lower() in query.lower():
            score += 0.1
        if payload.get("source_priority"):
            score += float(payload["source_priority"]) * 0.01
        if payload.get("updated_at"):
            try:
                updated_at = datetime.fromisoformat(str(payload["updated_at"]))
                days = max((datetime.now(UTC) - updated_at).days, 0)
                score += max(0.0, 0.05 - (days * 0.001))
            except Exception:
                pass
        if payload.get("confidence"):
            score += float(payload["confidence"]) * 0.05
        return score
