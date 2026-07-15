from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import AuditMixin, BaseModel, SoftDeleteMixin, TimestampMixin, UUIDMixin, VersionMixin


class KnowledgeCollection(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Collection registry used to group knowledge sources and documents."""

    __tablename__ = "knowledge_collections"
    __table_args__ = (
        UniqueConstraint("code", name="uq_knowledge_collections_code"),
        Index("ix_knowledge_collections_status", "status"),
        Index("ix_knowledge_collections_owner", "owner_type", "owner_id"),
    )

    code: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    owner_type: Mapped[str] = mapped_column(String(64), nullable=False, default="organization")
    owner_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    collection_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    collection_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    security_level: Mapped[str] = mapped_column(String(32), nullable=False, default="internal")

    sources: Mapped[list[KnowledgeSource]] = relationship(back_populates="collection", cascade="all, delete-orphan")
    documents: Mapped[list[KnowledgeDocument]] = relationship(back_populates="collection", cascade="all, delete-orphan")
    statistics: Mapped[list[KnowledgeStatistics]] = relationship(back_populates="collection", cascade="all, delete-orphan")
    policies: Mapped[list[KnowledgePolicy]] = relationship(back_populates="collection", cascade="all, delete-orphan")


class KnowledgeSource(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Source registry entry describing a knowledge ingestion origin."""

    __tablename__ = "knowledge_sources"
    __table_args__ = (
        UniqueConstraint("collection_id", "code", name="uq_knowledge_sources_collection_code"),
        Index("ix_knowledge_sources_status", "status"),
    )

    collection_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_collections.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    source_uri: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    collection: Mapped[KnowledgeCollection] = relationship(back_populates="sources")


class KnowledgeDocument(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Document registry entry with versioning, security, and metadata fields."""

    __tablename__ = "knowledge_documents"
    __table_args__ = (
        UniqueConstraint("collection_id", "checksum", name="uq_knowledge_documents_collection_checksum"),
        Index("ix_knowledge_documents_collection_status", "collection_id", "status"),
        Index("ix_knowledge_documents_owner", "owner_type", "owner_id"),
        Index("ix_knowledge_documents_language", "language"),
    )

    collection_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_collections.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[UUID | None] = mapped_column(ForeignKey("knowledge_sources.id", ondelete="SET NULL"), nullable=True)
    category: Mapped[str] = mapped_column(String(128), nullable=False, default="general")
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    file_name: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[str] = mapped_column(String(32), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    owner_type: Mapped[str] = mapped_column(String(64), nullable=False, default="organization")
    owner_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    organization_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    workspace_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    security_level: Mapped[str] = mapped_column(String(32), nullable=False, default="internal")
    classification: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str | None] = mapped_column(String(16), nullable=True)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    document_version_status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    approval_status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    retention_policy: Mapped[str | None] = mapped_column(String(64), nullable=True)
    content_length: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    encoding: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    document_tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    document_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    extraction_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    ingestion_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    security_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    version_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    collection: Mapped[KnowledgeCollection] = relationship(back_populates="documents")
    source: Mapped[KnowledgeSource | None] = relationship()
    versions: Mapped[list[DocumentVersion]] = relationship(back_populates="document", cascade="all, delete-orphan")
    chunks: Mapped[list[KnowledgeChunk]] = relationship(back_populates="document", cascade="all, delete-orphan")
    embeddings: Mapped[list[Embedding]] = relationship(back_populates="document", cascade="all, delete-orphan")
    audits: Mapped[list[KnowledgeAudit]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentVersion(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Document version history used for rollback and lifecycle control."""

    __tablename__ = "document_versions"
    __table_args__ = (
        Index("ix_document_versions_document_status", "document_id", "status"),
        Index("ix_document_versions_version_number", "document_id", "version_number"),
    )

    document_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    approval_status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    previous_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("document_versions.id", ondelete="SET NULL"), nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    version_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    document: Mapped[KnowledgeDocument] = relationship(back_populates="versions", foreign_keys=[document_id])


class KnowledgeChunk(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Text chunk derived from a knowledge document for retrieval and embedding."""

    __tablename__ = "knowledge_chunks"
    __table_args__ = (
        Index("ix_knowledge_chunks_document_order", "document_id", "chunk_index"),
        Index("ix_knowledge_chunks_collection_status", "collection_id", "status"),
    )

    document_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    collection_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_collections.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_type: Mapped[str] = mapped_column(String(64), nullable=False, default="fixed")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    character_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    overlap_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overlap_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    section_title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    document: Mapped[KnowledgeDocument] = relationship(back_populates="chunks")
    embeddings: Mapped[list[Embedding]] = relationship(back_populates="chunk", cascade="all, delete-orphan")


class Embedding(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Embedding row persisted alongside the document chunk and vector store reference."""

    __tablename__ = "embeddings"
    __table_args__ = (
        Index("ix_embeddings_chunk_status", "chunk_id", "status"),
        Index("ix_embeddings_collection_model", "collection_id", "model_name"),
    )

    document_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_chunks.id", ondelete="CASCADE"), nullable=False)
    collection_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_collections.id", ondelete="CASCADE"), nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_provider: Mapped[str] = mapped_column(String(128), nullable=False)
    vector_id: Mapped[str] = mapped_column(String(255), nullable=False)
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    embedding_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    document: Mapped[KnowledgeDocument] = relationship(back_populates="embeddings")
    chunk: Mapped[KnowledgeChunk] = relationship(back_populates="embeddings")


class VectorMetadata(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Payload metadata mirrored to the vector database for filtering and retrieval."""

    __tablename__ = "vector_metadata"
    __table_args__ = (Index("ix_vector_metadata_collection_status", "collection_id", "status"),)

    collection_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_collections.id", ondelete="CASCADE"), nullable=False)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_documents.id", ondelete="CASCADE"), nullable=False)
    chunk_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_chunks.id", ondelete="CASCADE"), nullable=False)
    vector_id: Mapped[str] = mapped_column(String(255), nullable=False)
    namespace: Mapped[str] = mapped_column(String(128), nullable=False, default="default")
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")


class KnowledgePolicy(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Governance policy attached to a collection or document."""

    __tablename__ = "knowledge_policies"
    __table_args__ = (Index("ix_knowledge_policies_collection_scope", "collection_id", "scope"),)

    collection_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_collections.id", ondelete="CASCADE"), nullable=False)
    scope: Mapped[str] = mapped_column(String(32), nullable=False)
    policy_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    is_enforced: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    policy_rules: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    policy_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    collection: Mapped[KnowledgeCollection] = relationship(back_populates="policies")


class KnowledgeAudit(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Audit trail for upload, delete, index, retrieval, and governance events."""

    __tablename__ = "knowledge_audits"
    __table_args__ = (Index("ix_knowledge_audits_document_action", "document_id", "action"),)

    collection_id: Mapped[UUID | None] = mapped_column(ForeignKey("knowledge_collections.id", ondelete="SET NULL"), nullable=True)
    document_id: Mapped[UUID | None] = mapped_column(ForeignKey("knowledge_documents.id", ondelete="SET NULL"), nullable=True)
    version_id: Mapped[UUID | None] = mapped_column(ForeignKey("document_versions.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    actor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    before_state: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    after_state: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    audit_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    document: Mapped[KnowledgeDocument | None] = relationship(back_populates="audits")


class KnowledgeStatistics(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Daily or ad hoc statistics record for a knowledge collection."""

    __tablename__ = "knowledge_statistics"
    __table_args__ = (Index("ix_knowledge_statistics_collection_metric", "collection_id", "metric_name"),)

    collection_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge_collections.id", ondelete="CASCADE"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False)
    metric_value: Mapped[float] = mapped_column(nullable=False, default=0.0)
    metric_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    dimension_data: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    statistics_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    collection: Mapped[KnowledgeCollection] = relationship(back_populates="statistics")
