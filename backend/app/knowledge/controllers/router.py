from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile
from uuid import UUID

from app.knowledge.dependencies import provide_knowledge_service
from app.knowledge.schemas import (
    ChunkRequest,
    CollectionCreateRequest,
    CollectionResponse,
    DocumentUpdateRequest,
    EmbedRequest,
    IndexRequest,
    KnowledgeChunkingResponse,
    KnowledgeDocumentResponse,
    KnowledgeEmbeddingBatchResponse,
    KnowledgeIndexResponse,
    KnowledgeProcessResponse,
    KnowledgeSearchResponse,
    KnowledgeStatisticsSnapshot,
    KnowledgeValidationResponse,
    ProcessDocumentRequest,
    SearchRequest,
    UploadDocumentRequest,
)
from app.knowledge.services.knowledge_service import KnowledgeService


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/collections", response_model=list[CollectionResponse])
async def list_collections(knowledge_service: KnowledgeService = Depends(provide_knowledge_service)) -> list[CollectionResponse]:
    return await knowledge_service.list_collections()


@router.post("/collections", response_model=CollectionResponse)
async def create_collection(payload: CollectionCreateRequest, knowledge_service: KnowledgeService = Depends(provide_knowledge_service)) -> CollectionResponse:
    return await knowledge_service.create_collection(payload)


@router.get("/documents", response_model=list[KnowledgeDocumentResponse])
async def list_documents(collection_code: str | None = None, status: str | None = None, search: str | None = None, knowledge_service: KnowledgeService = Depends(provide_knowledge_service)) -> list[KnowledgeDocumentResponse]:
    return await knowledge_service.list_documents(collection_code=collection_code, status=status, search=search)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    collection_code: str = Form(...),
    category: str = Form(default="general"),
    title: str = Form(...),
    file_type: str = Form(...),
    owner_type: str = Form(default="organization"),
    security_level: str = Form(default="internal"),
    classification: str | None = Form(default=None),
    language: str | None = Form(default=None),
    source_url: str | None = Form(default=None),
    metadata_json: str = Form(default="{}"),
    knowledge_service: KnowledgeService = Depends(provide_knowledge_service),
):
    content = (await file.read()).decode("utf-8", errors="ignore")
    import json

    payload = UploadDocumentRequest(
        collection_code=collection_code,
        category=category,
        title=title,
        file_type=file_type,
        owner_type=owner_type,
        security_level=security_level,
        classification=classification,
        language=language,
        source_url=source_url,
        metadata=json.loads(metadata_json or "{}"),
    )
    return await knowledge_service.upload_document(payload, content)


@router.post("/process", response_model=KnowledgeProcessResponse)
async def process_document(payload: ProcessDocumentRequest, knowledge_service: KnowledgeService = Depends(provide_knowledge_service)) -> KnowledgeProcessResponse:
    return await knowledge_service.process_document(payload)


@router.post("/chunk", response_model=KnowledgeChunkingResponse)
async def chunk_document(payload: ChunkRequest, knowledge_service: KnowledgeService = Depends(provide_knowledge_service)) -> KnowledgeChunkingResponse:
    return await knowledge_service.chunk_document(payload)


@router.post("/embed", response_model=KnowledgeEmbeddingBatchResponse)
async def embed_document(payload: EmbedRequest, knowledge_service: KnowledgeService = Depends(provide_knowledge_service)) -> KnowledgeEmbeddingBatchResponse:
    return await knowledge_service.embed_document(payload)


@router.post("/index", response_model=KnowledgeIndexResponse)
async def index_document(payload: IndexRequest, knowledge_service: KnowledgeService = Depends(provide_knowledge_service)) -> KnowledgeIndexResponse:
    return await knowledge_service.index_document(payload)


@router.post("/search", response_model=KnowledgeSearchResponse)
async def search(payload: SearchRequest, knowledge_service: KnowledgeService = Depends(provide_knowledge_service)) -> KnowledgeSearchResponse:
    return await knowledge_service.search(payload)


@router.get("/statistics", response_model=KnowledgeStatisticsSnapshot)
async def statistics(knowledge_service: KnowledgeService = Depends(provide_knowledge_service)) -> KnowledgeStatisticsSnapshot:
    return await knowledge_service.statistics()


@router.delete("/document/{document_id}", response_model=KnowledgeDocumentResponse)
async def delete_document(document_id: UUID, knowledge_service: KnowledgeService = Depends(provide_knowledge_service)) -> KnowledgeDocumentResponse:
    return await knowledge_service.delete_document(document_id)
