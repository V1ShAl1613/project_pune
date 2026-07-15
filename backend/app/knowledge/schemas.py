from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class KnowledgeStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class DocumentVersionStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ApprovalStatus(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    ROLLBACK = "rollback"


class SecurityLevel(StrEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class ChunkStrategy(StrEnum):
    FIXED = "fixed"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    MARKDOWN = "markdown"
    HTML = "html"
    CODE = "code"
    TABLE = "table"
    HYBRID = "hybrid"


class CollectionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    code: str
    name: str
    description: str | None = None
    owner_type: str = "organization"
    owner_id: UUID | None = None
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("tags")
    @classmethod
    def _trim_tags(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item and item.strip()]


class CollectionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    code: str
    name: str
    description: str | None
    status: str
    owner_type: str
    owner_id: UUID | None
    collection_tags: list[str]
    collection_metadata: dict[str, object]
    security_level: str
    created_at: datetime
    updated_at: datetime


class DocumentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    collection_code: str
    category: str = "general"
    title: str
    file_name: str
    file_type: str
    mime_type: str | None = None
    owner_type: str = "organization"
    owner_id: UUID | None = None
    organization_id: UUID | None = None
    workspace_id: UUID | None = None
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    classification: str | None = None
    language: str | None = None
    source_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
    content: str


class DocumentUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    title: str | None = None
    category: str | None = None
    status: KnowledgeStatus | None = None
    security_level: SecurityLevel | None = None
    classification: str | None = None
    language: str | None = None
    source_url: str | None = None
    tags: list[str] | None = None
    metadata: dict[str, object] | None = None


class UploadDocumentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    collection_code: str
    category: str = "general"
    title: str
    file_type: str
    owner_type: str = "organization"
    owner_id: UUID | None = None
    organization_id: UUID | None = None
    workspace_id: UUID | None = None
    security_level: SecurityLevel = SecurityLevel.INTERNAL
    classification: str | None = None
    language: str | None = None
    source_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class ProcessDocumentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    document_id: UUID
    content: str | None = None
    source_url: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class ChunkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    document_id: UUID
    strategy: ChunkStrategy = ChunkStrategy.HYBRID
    chunk_size: int = Field(default=2000, ge=128, le=10000)
    chunk_overlap: int = Field(default=200, ge=0, le=2000)
    semantic_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    metadata: dict[str, object] = Field(default_factory=dict)


class EmbedRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    document_id: UUID | None = None
    collection_code: str | None = None
    model_name: str | None = None
    provider_name: str | None = None
    chunk_ids: list[UUID] = Field(default_factory=list)
    batch_size: int = Field(default=32, ge=1, le=256)
    metadata: dict[str, object] = Field(default_factory=dict)


class IndexRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    document_id: UUID | None = None
    collection_code: str | None = None
    namespace: str = "default"
    model_name: str | None = None
    provider_name: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    collection_code: str | None = None
    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    threshold: float = Field(default=0.2, ge=0.0, le=1.0)
    namespace: str = "default"
    filters: dict[str, object] = Field(default_factory=dict)
    hybrid: bool = True
    metadata: dict[str, object] = Field(default_factory=dict)


class KnowledgeDocumentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    collection_id: UUID
    source_id: UUID | None
    category: str
    title: str
    file_name: str
    file_type: str
    mime_type: str | None
    status: str
    owner_type: str
    owner_id: UUID | None
    organization_id: UUID | None
    workspace_id: UUID | None
    security_level: str
    classification: str | None
    language: str | None
    checksum: str
    content_hash: str
    version_number: int
    document_version_status: str
    approval_status: str
    retention_policy: str | None
    content_length: int
    page_count: int | None
    word_count: int
    char_count: int
    encoding: str | None
    source_url: str | None
    document_tags: list[str]
    document_metadata: dict[str, object]
    extraction_metadata: dict[str, object]
    ingestion_metadata: dict[str, object]
    security_metadata: dict[str, object]
    version_comment: str | None
    created_at: datetime
    updated_at: datetime


class DocumentVersionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    document_id: UUID
    version_number: int
    status: str
    approval_status: str
    checksum: str
    content: str
    previous_version_id: UUID | None
    change_summary: str | None
    version_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class KnowledgeChunkResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    document_id: UUID
    collection_id: UUID
    chunk_index: int
    chunk_type: str
    content: str
    content_hash: str
    token_count: int
    character_count: int
    overlap_start: int | None
    overlap_end: int | None
    section_title: str | None
    page_number: int | None
    chunk_metadata: dict[str, object]
    status: str
    created_at: datetime
    updated_at: datetime


class EmbeddingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    document_id: UUID
    chunk_id: UUID
    collection_id: UUID
    model_name: str
    model_provider: str
    vector_id: str
    dimension: int
    status: str
    embedding_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class KnowledgePolicyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    collection_id: UUID
    scope: str
    policy_type: str
    status: str
    is_enforced: bool
    policy_rules: dict[str, object]
    policy_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class KnowledgeAuditResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    collection_id: UUID | None
    document_id: UUID | None
    version_id: UUID | None
    action: str
    actor: str | None
    before_state: dict[str, object]
    after_state: dict[str, object]
    audit_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class KnowledgeStatisticsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    collection_id: UUID
    metric_name: str
    metric_value: float
    metric_date: datetime
    dimension_data: dict[str, object]
    statistics_metadata: dict[str, object]
    status: str
    created_at: datetime
    updated_at: datetime


class KnowledgeSearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    document_id: UUID
    chunk_id: UUID
    collection_id: UUID
    score: float
    reranked_score: float
    content: str
    title: str
    file_name: str
    file_type: str
    source_id: UUID | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class KnowledgeSearchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    query: str
    collection_code: str | None = None
    total_results: int
    results: list[KnowledgeSearchResult] = Field(default_factory=list)
    search_metadata: dict[str, object] = Field(default_factory=dict)


class KnowledgeValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    code: str
    message: str
    severity: str = "error"
    details: dict[str, object] = Field(default_factory=dict)


class KnowledgeValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    is_valid: bool
    issues: list[KnowledgeValidationIssue] = Field(default_factory=list)
    checksum: str | None = None
    content_length: int = 0
    language: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class KnowledgeUploadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    document: KnowledgeDocumentResponse
    version: DocumentVersionResponse
    validation: KnowledgeValidationResponse


class KnowledgeProcessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    document: KnowledgeDocumentResponse
    version: DocumentVersionResponse | None = None
    chunks_created: int = 0
    metadata: dict[str, object] = Field(default_factory=dict)


class KnowledgeChunkingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    document_id: UUID
    chunks_created: int
    strategy: str
    chunks: list[KnowledgeChunkResponse] = Field(default_factory=list)


class KnowledgeEmbeddingBatchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    document_id: UUID | None = None
    collection_code: str | None = None
    model_name: str
    model_provider: str
    embeddings_created: int
    vector_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class KnowledgeIndexResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    document_id: UUID | None = None
    collection_code: str | None = None
    namespace: str
    indexed_chunks: int
    vector_ids: list[str] = Field(default_factory=list)
    qdrant_collection: str
    metadata: dict[str, object] = Field(default_factory=dict)


class KnowledgeStatisticsSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    documents_indexed: int = 0
    chunks_created: int = 0
    embeddings_generated: int = 0
    search_requests: int = 0
    latency_ms: float = 0.0
    failures: int = 0
    qdrant_health: str = "unknown"
    collection_statistics: list[KnowledgeStatisticsResponse] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
