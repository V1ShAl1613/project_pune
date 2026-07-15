from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from redis.asyncio import Redis

from app.core.settings import AppSettings
from app.exceptions.base import BaseApplicationException
from app.knowledge.chunking.engine import ChunkData, ChunkingEngine
from app.knowledge.documents.processor import DocumentProcessor
from app.knowledge.embeddings.service import EmbeddingService
from app.knowledge.governance.policy_engine import GovernanceEngine
from app.knowledge.indexing.indexer import Indexer
from app.knowledge.metadata.manager import MetadataManager
from app.knowledge.models import (
    DocumentVersion,
    Embedding,
    KnowledgeAudit,
    KnowledgeChunk,
    KnowledgeCollection,
    KnowledgeDocument,
    KnowledgePolicy,
    KnowledgeSource,
    KnowledgeStatistics,
    VectorMetadata,
)
from app.knowledge.repositories.knowledge_repository import KnowledgeRepository
from app.knowledge.retrieval.engine import RetrievalEngine
from app.knowledge.ranking.engine import RankingEngine
from app.knowledge.schemas import (
    ApprovalStatus,
    ChunkRequest,
    CollectionCreateRequest,
    CollectionResponse,
    DocumentCreateRequest,
    DocumentUpdateRequest,
    DocumentVersionStatus,
    EmbedRequest,
    EmbeddingResponse,
    IndexRequest,
    KnowledgeAuditResponse,
    KnowledgeChunkResponse,
    KnowledgeChunkingResponse,
    KnowledgeDocumentResponse,
    KnowledgeEmbeddingBatchResponse,
    KnowledgeIndexResponse,
    KnowledgePolicyResponse,
    KnowledgeProcessResponse,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
    KnowledgeStatisticsResponse,
    KnowledgeStatisticsSnapshot,
    KnowledgeValidationResponse,
    KnowledgeValidationIssue,
    ProcessDocumentRequest,
    SearchRequest,
    UploadDocumentRequest,
)
from app.knowledge.validators import KnowledgeValidator
from app.knowledge.vectorstore.qdrant_store import QdrantVectorStore


@dataclass(slots=True)
class KnowledgeService:
    """Enterprise knowledge base, processing, embedding, retrieval, and governance service."""

    repository: KnowledgeRepository
    settings: AppSettings
    redis_client: Redis | None
    logger: logging.Logger

    def __post_init__(self) -> None:
        self.validator = KnowledgeValidator(self.settings)
        self.processor = DocumentProcessor(self.settings, self.validator)
        self.chunker = ChunkingEngine(self.settings)
        self.embeddings = EmbeddingService(self.settings)
        self.vector_store = QdrantVectorStore(self.settings)
        self.ranking = RankingEngine()
        self.retrieval = RetrievalEngine(self.settings, self.embeddings, self.vector_store, self.ranking)
        self.indexer = Indexer(self.embeddings, self.vector_store)
        self.metadata = MetadataManager()
        self.governance = GovernanceEngine(self.settings)

    async def list_collections(self) -> list[CollectionResponse]:
        await self._seed_default_collection()
        cached = await self._cache_get("knowledge:collections:list")
        if cached:
            return [CollectionResponse.model_validate(item) for item in cached]
        collections = await self.repository.list_collections()
        payload = [self._serialize_collection(collection).model_dump(mode="json") for collection in collections]
        await self._cache_set("knowledge:collections:list", payload, ttl=self.settings.knowledge_collection_cache_ttl_seconds)
        return [CollectionResponse.model_validate(item) for item in payload]

    async def create_collection(self, request: CollectionCreateRequest) -> CollectionResponse:
        if await self.repository.get_collection_by_code(request.code) is not None:
            raise BaseApplicationException("Collection already exists", status_code=409, error_code="knowledge_collection_conflict")
        collection = KnowledgeCollection(
            code=request.code,
            name=request.name,
            description=request.description,
            status="active",
            owner_type=request.owner_type,
            owner_id=request.owner_id,
            collection_tags=request.tags,
            collection_metadata=request.metadata,
            security_level=request.security_level.value,
        )
        async with self.repository.transaction():
            created = await self.repository.create_collection(collection)
            await self.repository.create_policy(
                KnowledgePolicy(
                    collection_id=created.id,
                    scope="collection",
                    policy_type="security",
                    status="active",
                    is_enforced=True,
                    policy_rules={"security_level": request.security_level.value},
                    policy_metadata={"seeded": True},
                )
            )
            await self._audit(created.id, None, "collection_created", after=self._serialize_collection(created).model_dump(mode="json"))
        await self._invalidate_caches()
        return self._serialize_collection(created)

    async def list_documents(self, collection_code: str | None = None, status: str | None = None, search: str | None = None) -> list[KnowledgeDocumentResponse]:
        cached = await self._cache_get(self._document_list_cache_key(collection_code, status, search))
        if cached:
            return [KnowledgeDocumentResponse.model_validate(item) for item in cached]
        documents = await self.repository.list_documents(collection_code=collection_code, status=status, search=search)
        payload = [self._serialize_document(document).model_dump(mode="json") for document in documents]
        await self._cache_set(self._document_list_cache_key(collection_code, status, search), payload, ttl=self.settings.knowledge_document_cache_ttl_seconds)
        return [KnowledgeDocumentResponse.model_validate(item) for item in payload]

    async def upload_document(self, request: UploadDocumentRequest, content: str) -> dict[str, object]:
        collection = await self._resolve_collection(request.collection_code)
        validation = self.validator.validate_document(
            file_name=request.title,
            file_type=request.file_type,
            content=content,
            metadata=request.metadata,
            language=request.language,
        )
        existing_document = await self.repository.get_document_by_checksum(collection.id, validation.checksum or "")
        if existing_document is not None:
            validation.issues.append(KnowledgeValidationIssue(code="duplicate_detection", message="Potential duplicate content detected", severity="warning", details={"existing_document_id": str(existing_document.id)}))
        if not validation.is_valid:
            raise BaseApplicationException("Document validation failed", status_code=422, error_code="knowledge_validation_failed")
        processed = self.processor.process(content, file_name=request.title, file_type=request.file_type, mime_type=None)
        document = KnowledgeDocument(
            collection_id=collection.id,
            source_id=None,
            category=request.category,
            title=request.title,
            file_name=request.title,
            file_type=request.file_type,
            mime_type=self.validator.infer_mime_type(request.title, request.file_type),
            status="draft",
            owner_type=request.owner_type,
            owner_id=request.owner_id,
            organization_id=request.organization_id,
            workspace_id=request.workspace_id,
            security_level=request.security_level.value,
            classification=request.classification,
            language=processed["language"],
            checksum=processed["checksum"],
            content_hash=processed["checksum"],
            version_number=1,
            document_version_status=DocumentVersionStatus.DRAFT.value,
            approval_status=ApprovalStatus.DRAFT.value,
            retention_policy=None,
            content_length=len(processed["text"]),
            page_count=processed["metadata"].get("page_count"),
            word_count=processed["metadata"].get("word_count", 0),
            char_count=processed["metadata"].get("char_count", 0),
            encoding=processed["metadata"].get("encoding"),
            source_url=request.source_url,
            document_tags=request.tags,
            document_metadata={**request.metadata, **processed["metadata"]},
            extraction_metadata=processed["metadata"],
            ingestion_metadata={"source": "upload"},
            security_metadata={"security_level": request.security_level.value, "validation": validation.model_dump(mode="json")},
            version_comment="Initial upload",
        )
        version = self._build_version(document, processed["text"], 1, "draft", "Initial upload")
        async with self.repository.transaction():
            created = await self.repository.create_document(document)
            created_version = await self.repository.create_version(version)
            await self.repository.create_audit(KnowledgeAudit(collection_id=collection.id, document_id=created.id, version_id=created_version.id, action="document_uploaded", actor="system", before_state={}, after_state=self._serialize_document(created).model_dump(mode="json"), audit_metadata=validation.model_dump(mode="json")))
        await self._invalidate_caches()
        return {
            "document": self._serialize_document(created),
            "version": self._serialize_version(version),
            "validation": validation,
        }

    async def process_document(self, request: ProcessDocumentRequest) -> KnowledgeProcessResponse:
        document = await self.repository.get_document(request.document_id)
        if document is None:
            raise BaseApplicationException("Document not found", status_code=404, error_code="knowledge_document_not_found")
        content = request.content or await self._latest_document_content(document.id)
        processed = self.processor.process(content, file_name=document.file_name, file_type=document.file_type, mime_type=document.mime_type)
        document.language = processed["language"]
        document.checksum = processed["checksum"]
        document.content_hash = processed["checksum"]
        document.content_length = len(processed["text"])
        document.word_count = processed["metadata"].get("word_count", 0)
        document.char_count = processed["metadata"].get("char_count", 0)
        document.extraction_metadata = processed["metadata"]
        document.document_metadata = {**document.document_metadata, **request.metadata}
        version = self._build_version(document, processed["text"], document.version_number + 1, "draft", "Processed document")
        async with self.repository.transaction():
            await self.repository.update_document(document, {"language": document.language, "checksum": document.checksum, "content_hash": document.content_hash, "content_length": document.content_length, "word_count": document.word_count, "char_count": document.char_count, "extraction_metadata": document.extraction_metadata, "document_metadata": document.document_metadata, "version_number": document.version_number + 1})
            created_version = await self.repository.create_version(version)
            await self.repository.create_audit(KnowledgeAudit(collection_id=document.collection_id, document_id=document.id, version_id=created_version.id, action="document_processed", actor="system", before_state={}, after_state=self._serialize_document(document).model_dump(mode="json"), audit_metadata=request.metadata))
        await self._invalidate_caches()
        return KnowledgeProcessResponse(document=self._serialize_document(document), version=self._serialize_version(version), chunks_created=0, metadata={"processed": True})

    async def chunk_document(self, request: ChunkRequest) -> KnowledgeChunkingResponse:
        document = await self.repository.get_document(request.document_id)
        if document is None:
            raise BaseApplicationException("Document not found", status_code=404, error_code="knowledge_document_not_found")
        content = await self._latest_document_content(document.id)
        chunks = self.chunker.chunk(content, strategy=request.strategy.value, chunk_size=request.chunk_size, chunk_overlap=request.chunk_overlap, metadata={"document_id": str(document.id), "collection_id": str(document.collection_id), **request.metadata})
        created_chunks: list[KnowledgeChunk] = []
        async with self.repository.transaction():
            for chunk_data in chunks:
                created_chunks.append(await self.repository.create_chunk(self._build_chunk(document, chunk_data, request.strategy.value)))
            await self.repository.create_audit(KnowledgeAudit(collection_id=document.collection_id, document_id=document.id, action="document_chunked", actor="system", before_state={}, after_state={"chunks_created": len(created_chunks)}, audit_metadata=request.metadata))
        await self._cache_set(self._chunk_cache_key(document.id), [self._serialize_chunk(chunk).model_dump(mode="json") for chunk in created_chunks], ttl=self.settings.knowledge_cache_ttl_seconds)
        return KnowledgeChunkingResponse(document_id=document.id, chunks_created=len(created_chunks), strategy=request.strategy.value, chunks=[self._serialize_chunk(chunk) for chunk in created_chunks])

    async def embed_document(self, request: EmbedRequest) -> KnowledgeEmbeddingBatchResponse:
        document = await self.repository.get_document(request.document_id) if request.document_id is not None else None
        chunks = await self._resolve_chunks(document, request.chunk_ids)
        texts = [chunk.content for chunk in chunks]
        results = self.embeddings.batch_embed(texts, batch_size=request.batch_size, model_name=request.model_name, provider_name=request.provider_name or "sentence-transformers")
        vector_ids: list[str] = []
        async with self.repository.transaction():
            for chunk, result in zip(chunks, results, strict=False):
                vector_id = str(uuid4())
                vector_ids.append(vector_id)
                await self.repository.create_embedding(Embedding(document_id=chunk.document_id, chunk_id=chunk.id, collection_id=chunk.collection_id, model_name=result.model_name, model_provider=result.provider_name, vector_id=vector_id, dimension=result.dimension, status="active", embedding_metadata={**request.metadata, **result.metadata}))
                await self.repository.create_audit(KnowledgeAudit(collection_id=chunk.collection_id, document_id=chunk.document_id, action="embedding_generated", actor="system", before_state={}, after_state={"vector_id": vector_id}, audit_metadata={"model_name": result.model_name, **request.metadata}))
        await self._cache_set(self._embedding_cache_key(document.collection_id if document else None), {"vector_ids": vector_ids}, ttl=self.settings.knowledge_cache_ttl_seconds)
        return KnowledgeEmbeddingBatchResponse(document_id=request.document_id, collection_code=request.collection_code, model_name=request.model_name or self.settings.knowledge_default_embedding_model, model_provider=request.provider_name or "sentence-transformers", embeddings_created=len(vector_ids), vector_ids=vector_ids, metadata=request.metadata)

    async def index_document(self, request: IndexRequest) -> KnowledgeIndexResponse:
        document = await self.repository.get_document(request.document_id) if request.document_id is not None else None
        collection = await self._resolve_collection(request.collection_code)
        chunks = await self._resolve_chunks(document, [])
        if not chunks:
            chunks = await self.repository.list_chunks(document.id) if document is not None else []
        chunk_payloads = [self._chunk_payload(chunk, document) for chunk in chunks]
        vector_ids = self.indexer.index(collection_code=collection.code, namespace=request.namespace, chunks=chunk_payloads, model_name=request.model_name or self.settings.knowledge_default_embedding_model, provider_name=request.provider_name or "sentence-transformers")
        async with self.repository.transaction():
            for chunk, vector_id in zip(chunks, vector_ids, strict=False):
                await self.repository.create_vector_metadata(VectorMetadata(collection_id=collection.id, document_id=chunk.document_id, chunk_id=chunk.id, vector_id=vector_id, namespace=request.namespace, payload=self._vector_payload(chunk, document, collection.code), status="active"))
            await self.repository.create_audit(KnowledgeAudit(collection_id=collection.id, document_id=document.id if document else None, action="document_indexed", actor="system", before_state={}, after_state={"indexed_chunks": len(vector_ids)}, audit_metadata=request.metadata))
        await self._cache_set(self._index_cache_key(collection.code, request.namespace), {"vector_ids": vector_ids}, ttl=self.settings.knowledge_pipeline_cache_ttl_seconds)
        return KnowledgeIndexResponse(document_id=request.document_id, collection_code=collection.code, namespace=request.namespace, indexed_chunks=len(vector_ids), vector_ids=vector_ids, qdrant_collection=self.vector_store.ensure_collection(collection.code), metadata=request.metadata)

    async def search(self, request: SearchRequest) -> KnowledgeSearchResponse:
        collection_code = request.collection_code or self.settings.knowledge_default_collection
        cached = await self._cache_get(self._search_cache_key(collection_code, request.query, request.namespace))
        if cached:
            return KnowledgeSearchResponse.model_validate(cached)
        results = self.retrieval.search(query=request.query, collection_code=collection_code, top_k=request.top_k, threshold=request.threshold, namespace=request.namespace, filters=request.filters)
        payload = KnowledgeSearchResponse(query=request.query, collection_code=request.collection_code, total_results=len(results), results=results, search_metadata=request.metadata)
        await self._cache_set(self._search_cache_key(collection_code, request.query, request.namespace), payload.model_dump(mode="json"), ttl=self.settings.knowledge_search_cache_ttl_seconds)
        collection = await self.repository.get_collection_by_code(collection_code)
        if collection is not None:
            await self.repository.create_audit(KnowledgeAudit(collection_id=collection.id, document_id=None, action="document_retrieved", actor="system", before_state={}, after_state={"query": request.query, "results": len(results)}, audit_metadata=request.metadata))
        return payload

    async def statistics(self) -> KnowledgeStatisticsSnapshot:
        cached = await self._cache_get("knowledge:statistics:snapshot")
        if cached:
            return KnowledgeStatisticsSnapshot.model_validate(cached)
        statistics_rows = await self.repository.list_statistics()
        collection = await self._resolve_collection(self.settings.knowledge_default_collection)
        snapshot = KnowledgeStatisticsSnapshot(
            documents_indexed=len(await self.repository.list_documents()),
            chunks_created=sum(len(await self.repository.list_chunks(document.id)) for document in await self.repository.list_documents()),
            embeddings_generated=len(await self.repository.list_embeddings()),
            search_requests=len(await self.repository.list_statistics(collection.id)),
            latency_ms=0.0,
            failures=0,
            qdrant_health=self.vector_store.health().get("status", "unknown"),
            collection_statistics=[KnowledgeStatisticsResponse.model_validate(row, from_attributes=True) for row in statistics_rows],
            metadata={"collections": len(await self.repository.list_collections())},
        )
        await self._cache_set("knowledge:statistics:snapshot", snapshot.model_dump(mode="json"), ttl=self.settings.knowledge_statistics_cache_ttl_seconds)
        return snapshot

    async def delete_document(self, document_id: UUID) -> KnowledgeDocumentResponse:
        document = await self.repository.get_document(document_id)
        if document is None:
            raise BaseApplicationException("Document not found", status_code=404, error_code="knowledge_document_not_found")
        before = self._serialize_document(document).model_dump(mode="json")
        async with self.repository.transaction():
            await self.repository.delete_document(document)
            self.vector_store.delete_document(document.collection.code if document.collection else self.settings.knowledge_default_collection, str(document.id))
            await self.repository.create_audit(KnowledgeAudit(collection_id=document.collection_id, document_id=document.id, action="document_deleted", actor="system", before_state=before, after_state=self._serialize_document(document).model_dump(mode="json"), audit_metadata={"deleted": True}))
        await self._invalidate_caches()
        return self._serialize_document(document)

    async def validate_document(self, request: ProcessDocumentRequest) -> KnowledgeValidationResponse:
        document = await self.repository.get_document(request.document_id)
        if document is None:
            raise BaseApplicationException("Document not found", status_code=404, error_code="knowledge_document_not_found")
        content = request.content or await self._latest_document_content(document.id)
        validation = self.validator.validate_document(file_name=document.file_name, file_type=document.file_type, content=content, metadata={**document.document_metadata, **request.metadata}, language=document.language, checksum=document.checksum)
        duplicate_document = await self.repository.get_document_by_checksum(document.collection_id, validation.checksum or "")
        if duplicate_document is not None and duplicate_document.id != document.id:
            validation.issues.append(KnowledgeValidationIssue(code="duplicate_detection", message="Potential duplicate content detected", severity="warning", details={"existing_document_id": str(duplicate_document.id)}))
        await self.repository.create_audit(KnowledgeAudit(collection_id=document.collection_id, document_id=document.id, action="document_validated", actor="system", before_state={}, after_state=validation.model_dump(mode="json"), audit_metadata=request.metadata))
        return validation

    async def get_document_by_id(self, document_id: UUID) -> KnowledgeDocumentResponse:
        document = await self.repository.get_document(document_id)
        if document is None:
            raise BaseApplicationException("Document not found", status_code=404, error_code="knowledge_document_not_found")
        return self._serialize_document(document)

    async def _seed_default_collection(self) -> None:
        collection = await self.repository.get_collection_by_code(self.settings.knowledge_default_collection)
        if collection is None:
            await self.repository.create_collection(
                KnowledgeCollection(
                    code=self.settings.knowledge_default_collection,
                    name="Default Knowledge Base",
                    description="Default enterprise knowledge collection",
                    status="active",
                    owner_type=self.settings.knowledge_default_owner_type,
                    owner_id=None,
                    collection_tags=["default"],
                    collection_metadata={"seeded": True},
                    security_level=self.settings.knowledge_default_security_level,
                )
            )

    async def _resolve_collection(self, collection_code: str | None) -> KnowledgeCollection:
        await self._seed_default_collection()
        code = collection_code or self.settings.knowledge_default_collection
        collection = await self.repository.get_collection_by_code(code)
        if collection is None:
            raise BaseApplicationException("Collection not found", status_code=404, error_code="knowledge_collection_not_found")
        return collection

    async def _latest_document_content(self, document_id: UUID) -> str:
        versions = await self.repository.list_versions(document_id)
        return versions[0].content if versions else ""

    async def _resolve_chunks(self, document: KnowledgeDocument | None, chunk_ids: list[UUID]) -> list[KnowledgeChunk]:
        if document is None:
            return []
        chunks = await self.repository.list_chunks(document.id)
        if chunk_ids:
            chunk_id_set = set(chunk_ids)
            return [chunk for chunk in chunks if chunk.id in chunk_id_set]
        return chunks

    def _build_version(self, document: KnowledgeDocument, content: str, version_number: int, status: str, change_summary: str | None) -> DocumentVersion:
        return DocumentVersion(document_id=document.id, version_number=version_number, status=status, approval_status=ApprovalStatus.DRAFT.value, checksum=self.validator.checksum(content), content=content, previous_version_id=None, change_summary=change_summary, version_metadata={"created_at": datetime.now(UTC).isoformat()})

    def _build_chunk(self, document: KnowledgeDocument, chunk_data: ChunkData, strategy: str) -> KnowledgeChunk:
        return KnowledgeChunk(document_id=document.id, collection_id=document.collection_id, chunk_index=chunk_data.chunk_index, chunk_type=strategy, content=chunk_data.content, content_hash=self.chunker.chunk_hash(chunk_data.content), token_count=chunk_data.token_count, character_count=chunk_data.character_count, overlap_start=chunk_data.overlap_start, overlap_end=chunk_data.overlap_end, section_title=chunk_data.section_title, page_number=chunk_data.page_number, chunk_metadata=chunk_data.metadata or {}, status="active")

    def _chunk_payload(self, chunk: KnowledgeChunk, document: KnowledgeDocument | None) -> dict[str, object]:
        return {
            "id": str(chunk.id),
            "document_id": str(chunk.document_id),
            "collection_id": str(chunk.collection_id),
            "content": chunk.content,
            "title": document.title if document else "",
            "file_name": document.file_name if document else "",
            "file_type": document.file_type if document else "",
            "source_id": str(document.source_id) if document and document.source_id else None,
            "updated_at": (document.updated_at.isoformat() if document else datetime.now(UTC).isoformat()),
            "confidence": 1.0,
            "source_priority": 1,
        }

    def _vector_payload(self, chunk: KnowledgeChunk, document: KnowledgeDocument | None, collection_code: str) -> dict[str, object]:
        return {
            "document_id": str(chunk.document_id),
            "chunk_id": str(chunk.id),
            "collection_id": str(chunk.collection_id),
            "title": document.title if document else "",
            "file_name": document.file_name if document else "",
            "file_type": document.file_type if document else "",
            "content": chunk.content,
            "collection_code": collection_code,
            "updated_at": (document.updated_at.isoformat() if document else datetime.now(UTC).isoformat()),
            "confidence": 1.0,
            "source_priority": 1,
        }

    def _serialize_collection(self, collection: KnowledgeCollection) -> CollectionResponse:
        return CollectionResponse(id=collection.id, code=collection.code, name=collection.name, description=collection.description, status=collection.status, owner_type=collection.owner_type, owner_id=collection.owner_id, collection_tags=list(collection.collection_tags or []), collection_metadata=collection.collection_metadata, security_level=collection.security_level, created_at=collection.created_at, updated_at=collection.updated_at)

    def _serialize_document(self, document: KnowledgeDocument) -> KnowledgeDocumentResponse:
        return KnowledgeDocumentResponse(id=document.id, collection_id=document.collection_id, source_id=document.source_id, category=document.category, title=document.title, file_name=document.file_name, file_type=document.file_type, mime_type=document.mime_type, status=document.status, owner_type=document.owner_type, owner_id=document.owner_id, organization_id=document.organization_id, workspace_id=document.workspace_id, security_level=document.security_level, classification=document.classification, language=document.language, checksum=document.checksum, content_hash=document.content_hash, version_number=document.version_number, document_version_status=document.document_version_status, approval_status=document.approval_status, retention_policy=document.retention_policy, content_length=document.content_length, page_count=document.page_count, word_count=document.word_count, char_count=document.char_count, encoding=document.encoding, source_url=document.source_url, document_tags=list(document.document_tags or []), document_metadata=document.document_metadata, extraction_metadata=document.extraction_metadata, ingestion_metadata=document.ingestion_metadata, security_metadata=document.security_metadata, version_comment=document.version_comment, created_at=document.created_at, updated_at=document.updated_at)

    def _serialize_version(self, version: DocumentVersion) -> DocumentVersionResponse:
        return DocumentVersionResponse(id=version.id, document_id=version.document_id, version_number=version.version_number, status=version.status, approval_status=version.approval_status, checksum=version.checksum, content=version.content, previous_version_id=version.previous_version_id, change_summary=version.change_summary, version_metadata=version.version_metadata, created_at=version.created_at, updated_at=version.updated_at)

    def _serialize_chunk(self, chunk: KnowledgeChunk) -> KnowledgeChunkResponse:
        return KnowledgeChunkResponse(id=chunk.id, document_id=chunk.document_id, collection_id=chunk.collection_id, chunk_index=chunk.chunk_index, chunk_type=chunk.chunk_type, content=chunk.content, content_hash=chunk.content_hash, token_count=chunk.token_count, character_count=chunk.character_count, overlap_start=chunk.overlap_start, overlap_end=chunk.overlap_end, section_title=chunk.section_title, page_number=chunk.page_number, chunk_metadata=chunk.chunk_metadata, status=chunk.status, created_at=chunk.created_at, updated_at=chunk.updated_at)

    def _document_list_cache_key(self, collection_code: str | None, status: str | None, search: str | None) -> str:
        return f"knowledge:documents:{collection_code or '*'}:{status or '*'}:{search or '*'}"

    def _chunk_cache_key(self, document_id: UUID) -> str:
        return f"knowledge:chunks:{document_id}"

    def _embedding_cache_key(self, collection_id: UUID | None) -> str:
        return f"knowledge:embeddings:{collection_id or 'global'}"

    def _index_cache_key(self, collection_code: str, namespace: str) -> str:
        return f"knowledge:index:{collection_code}:{namespace}"

    def _search_cache_key(self, collection_code: str, query: str, namespace: str) -> str:
        digest = hashlib.sha256(query.encode("utf-8")).hexdigest()
        return f"knowledge:search:{collection_code}:{namespace}:{digest}"

    async def _cache_get(self, key: str):
        if self.redis_client is None:
            return None
        payload = await self.redis_client.get(key)
        return json.loads(payload) if payload else None

    async def _cache_set(self, key: str, value, ttl: int) -> None:
        if self.redis_client is None:
            return
        await self.redis_client.set(key, json.dumps(value), ex=ttl)

    async def _invalidate_caches(self) -> None:
        if self.redis_client is None:
            return
        await self.redis_client.delete("knowledge:collections:list", "knowledge:statistics:snapshot")

    async def _audit(self, collection_id, document_id, action: str, *, before: dict[str, object] | None = None, after: dict[str, object] | None = None) -> None:
        await self.repository.create_audit(KnowledgeAudit(collection_id=collection_id, document_id=document_id, action=action, actor="system", before_state=before or {}, after_state=after or {}, audit_metadata={"service": "knowledge"}))
