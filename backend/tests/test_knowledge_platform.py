from __future__ import annotations

from app.core.settings import TestingSettings
from app.knowledge.chunking.engine import ChunkingEngine
from app.knowledge.dependencies import provide_knowledge_service
from app.knowledge.validators import KnowledgeValidator


class _FakeKnowledgeService:
    async def list_collections(self):
        return []


def test_knowledge_collections_route_is_registered(client, app) -> None:
    app.dependency_overrides[provide_knowledge_service] = lambda: _FakeKnowledgeService()
    try:
        response = client.get("/knowledge/collections")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == []


def test_fixed_chunking_splits_text() -> None:
    settings = TestingSettings()
    validator = KnowledgeValidator(settings)
    chunker = ChunkingEngine(settings)
    content = "abcdefghijklmnopqrstuvwxyz" * 20
    chunks = chunker.chunk(content, strategy="fixed", chunk_size=50, chunk_overlap=10)

    assert chunks
    assert chunks[0].token_count >= 1
    assert validator.checksum(content)
