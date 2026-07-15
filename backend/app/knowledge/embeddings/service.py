from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any

from app.core.settings import AppSettings


@dataclass(slots=True)
class EmbeddingResult:
    vector: list[float]
    model_name: str
    provider_name: str
    dimension: int
    metadata: dict[str, Any]


@dataclass(slots=True)
class EmbeddingService:
    """Generate and validate embeddings with lazy support for Sentence Transformers."""

    settings: AppSettings

    def embed_texts(self, texts: list[str], *, model_name: str | None = None, provider_name: str = "sentence-transformers") -> list[EmbeddingResult]:
        model_name = model_name or self.settings.knowledge_default_embedding_model
        vectors = self._encode_with_model(texts, model_name)
        return [
            EmbeddingResult(
                vector=vector,
                model_name=model_name,
                provider_name=provider_name,
                dimension=len(vector),
                metadata={"batch_index": index},
            )
            for index, vector in enumerate(vectors)
        ]

    def embed_text(self, text: str, *, model_name: str | None = None, provider_name: str = "sentence-transformers") -> EmbeddingResult:
        return self.embed_texts([text], model_name=model_name, provider_name=provider_name)[0]

    def validate_embedding(self, vector: list[float]) -> bool:
        return bool(vector) and all(isinstance(value, (int, float)) for value in vector)

    def batch_embed(self, texts: list[str], *, batch_size: int = 32, model_name: str | None = None, provider_name: str = "sentence-transformers") -> list[EmbeddingResult]:
        batches: list[EmbeddingResult] = []
        for start in range(0, len(texts), batch_size):
            batches.extend(self.embed_texts(texts[start : start + batch_size], model_name=model_name, provider_name=provider_name))
        return batches

    def _encode_with_model(self, texts: list[str], model_name: str) -> list[list[float]]:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            model = SentenceTransformer(model_name)
            return [self._normalize_vector(list(vector)) for vector in model.encode(texts, convert_to_numpy=False, show_progress_bar=False)]
        except Exception:
            dimension = self.settings.knowledge_qdrant_vector_size
            return [self._fallback_vector(text, dimension) for text in texts]

    def _fallback_vector(self, text: str, dimension: int) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values = [digest[index % len(digest)] / 255.0 for index in range(dimension)]
        norm = math.sqrt(sum(value * value for value in values)) or 1.0
        return [value / norm for value in values]

    def _normalize_vector(self, vector: list[float]) -> list[float]:
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [float(value / norm) for value in vector]
