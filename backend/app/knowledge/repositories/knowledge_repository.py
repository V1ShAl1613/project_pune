from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, AsyncIterator
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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


@dataclass(slots=True)
class KnowledgeRepository:
    """Async persistence helpers for the knowledge base."""

    session: AsyncSession

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        if self.session.in_transaction():
            async with self.session.begin_nested():
                yield self.session
            tx = self.session.get_transaction()
            if tx is not None and not tx.nested:
                await self.session.commit()
        else:
            async with self.session.begin():
                yield self.session

    async def list_collections(self) -> list[KnowledgeCollection]:
        result = await self.session.execute(select(KnowledgeCollection).where(KnowledgeCollection.deleted_at.is_(None)).order_by(KnowledgeCollection.name))
        return list(result.scalars().all())

    async def get_collection(self, collection_id: UUID) -> KnowledgeCollection | None:
        result = await self.session.execute(
            select(KnowledgeCollection)
            .options(selectinload(KnowledgeCollection.sources), selectinload(KnowledgeCollection.documents), selectinload(KnowledgeCollection.statistics), selectinload(KnowledgeCollection.policies))
            .where(KnowledgeCollection.id == collection_id)
        )
        collection = result.scalar_one_or_none()
        if collection is None or collection.deleted_at is not None:
            return None
        return collection

    async def get_collection_by_code(self, code: str) -> KnowledgeCollection | None:
        result = await self.session.execute(select(KnowledgeCollection).where(KnowledgeCollection.code == code, KnowledgeCollection.deleted_at.is_(None)))
        return result.scalar_one_or_none()

    async def create_collection(self, collection: KnowledgeCollection) -> KnowledgeCollection:
        self.session.add(collection)
        await self.session.flush()
        return collection

    async def update_collection(self, collection: KnowledgeCollection, values: dict[str, Any]) -> KnowledgeCollection:
        for key, value in values.items():
            if hasattr(collection, key):
                setattr(collection, key, value)
        await self.session.flush()
        return collection

    async def list_documents(self, collection_code: str | None = None, status: str | None = None, search: str | None = None) -> list[KnowledgeDocument]:
        statement = select(KnowledgeDocument).options(selectinload(KnowledgeDocument.collection), selectinload(KnowledgeDocument.source)).where(KnowledgeDocument.deleted_at.is_(None))
        if collection_code is not None:
            statement = statement.join(KnowledgeCollection, KnowledgeDocument.collection_id == KnowledgeCollection.id).where(KnowledgeCollection.code == collection_code)
        if status is not None:
            statement = statement.where(KnowledgeDocument.status == status)
        if search:
            statement = statement.where(or_(KnowledgeDocument.title.ilike(f"%{search}%"), KnowledgeDocument.file_name.ilike(f"%{search}%"), KnowledgeDocument.category.ilike(f"%{search}%")))
        result = await self.session.execute(statement.order_by(KnowledgeDocument.updated_at.desc()))
        return list(result.scalars().unique().all())

    async def get_document(self, document_id: UUID) -> KnowledgeDocument | None:
        result = await self.session.execute(
            select(KnowledgeDocument)
            .options(
                selectinload(KnowledgeDocument.collection),
                selectinload(KnowledgeDocument.source),
                selectinload(KnowledgeDocument.versions),
                selectinload(KnowledgeDocument.chunks),
                selectinload(KnowledgeDocument.embeddings),
                selectinload(KnowledgeDocument.audits),
            )
            .where(KnowledgeDocument.id == document_id)
        )
        document = result.scalar_one_or_none()
        if document is None or document.deleted_at is not None:
            return None
        return document

    async def get_document_by_checksum(self, collection_id: UUID, checksum: str) -> KnowledgeDocument | None:
        result = await self.session.execute(select(KnowledgeDocument).where(KnowledgeDocument.collection_id == collection_id, KnowledgeDocument.checksum == checksum, KnowledgeDocument.deleted_at.is_(None)))
        return result.scalar_one_or_none()

    async def create_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        self.session.add(document)
        await self.session.flush()
        return document

    async def update_document(self, document: KnowledgeDocument, values: dict[str, Any]) -> KnowledgeDocument:
        for key, value in values.items():
            if hasattr(document, key):
                setattr(document, key, value)
        await self.session.flush()
        return document

    async def delete_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        document.mark_deleted()
        document.status = "deleted"
        await self.session.flush()
        return document

    async def create_source(self, source: KnowledgeSource) -> KnowledgeSource:
        self.session.add(source)
        await self.session.flush()
        return source

    async def create_version(self, version: DocumentVersion) -> DocumentVersion:
        self.session.add(version)
        await self.session.flush()
        return version

    async def list_versions(self, document_id: UUID) -> list[DocumentVersion]:
        result = await self.session.execute(select(DocumentVersion).where(DocumentVersion.document_id == document_id).order_by(DocumentVersion.version_number.desc()))
        return list(result.scalars().all())

    async def get_version(self, version_id: UUID) -> DocumentVersion | None:
        result = await self.session.execute(select(DocumentVersion).where(DocumentVersion.id == version_id))
        version = result.scalar_one_or_none()
        if version is None or version.deleted_at is not None:
            return None
        return version

    async def create_chunk(self, chunk: KnowledgeChunk) -> KnowledgeChunk:
        self.session.add(chunk)
        await self.session.flush()
        return chunk

    async def list_chunks(self, document_id: UUID) -> list[KnowledgeChunk]:
        result = await self.session.execute(select(KnowledgeChunk).where(KnowledgeChunk.document_id == document_id).order_by(KnowledgeChunk.chunk_index.asc()))
        return list(result.scalars().all())

    async def create_embedding(self, embedding: Embedding) -> Embedding:
        self.session.add(embedding)
        await self.session.flush()
        return embedding

    async def list_embeddings(self, document_id: UUID | None = None) -> list[Embedding]:
        statement = select(Embedding)
        if document_id is not None:
            statement = statement.where(Embedding.document_id == document_id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_vector_metadata(self, vector_metadata: VectorMetadata) -> VectorMetadata:
        self.session.add(vector_metadata)
        await self.session.flush()
        return vector_metadata

    async def list_policies(self, collection_id: UUID) -> list[KnowledgePolicy]:
        result = await self.session.execute(select(KnowledgePolicy).where(KnowledgePolicy.collection_id == collection_id))
        return list(result.scalars().all())

    async def create_policy(self, policy: KnowledgePolicy) -> KnowledgePolicy:
        self.session.add(policy)
        await self.session.flush()
        return policy

    async def create_audit(self, audit: KnowledgeAudit) -> KnowledgeAudit:
        self.session.add(audit)
        await self.session.flush()
        return audit

    async def list_statistics(self, collection_id: UUID | None = None) -> list[KnowledgeStatistics]:
        statement = select(KnowledgeStatistics).order_by(KnowledgeStatistics.metric_date.desc())
        if collection_id is not None:
            statement = statement.where(KnowledgeStatistics.collection_id == collection_id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_statistics(self, statistics: KnowledgeStatistics) -> KnowledgeStatistics:
        self.session.add(statistics)
        await self.session.flush()
        return statistics
