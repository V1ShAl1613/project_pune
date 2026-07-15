from __future__ import annotations

from dataclasses import dataclass

from app.knowledge.chunking.engine import ChunkingEngine
from app.knowledge.documents.processor import DocumentProcessor
from app.knowledge.embeddings.service import EmbeddingService
from app.knowledge.indexing.indexer import Indexer
from app.knowledge.retrieval.engine import RetrievalEngine
from app.knowledge.vectorstore.qdrant_store import QdrantVectorStore


@dataclass(slots=True)
class KnowledgePipeline:
    """High-level orchestration for document processing, embedding, indexing, and retrieval."""

    processor: DocumentProcessor
    chunker: ChunkingEngine
    embeddings: EmbeddingService
    vector_store: QdrantVectorStore
    retrieval: RetrievalEngine
    indexer: Indexer
