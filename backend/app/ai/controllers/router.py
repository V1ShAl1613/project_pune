from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.ai.dependencies import provide_ai_service
from app.ai.schemas import (
    AIChatRequest,
    AICompletionRequest,
    AIHealthResponse,
    AIModelPullRequest,
    AIModelResponse,
    AIProviderResponse,
    AIResponse,
    ConversationCreateRequest,
    ConversationResponse,
)
from app.ai.services.ai_service import AIService


router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/models", response_model=list[AIModelResponse])
async def list_models(ai_service: AIService = Depends(provide_ai_service)) -> list[AIModelResponse]:
    return await ai_service.list_models()


@router.get("/models/{model_id}", response_model=AIModelResponse)
async def get_model(model_id: UUID, ai_service: AIService = Depends(provide_ai_service)) -> AIModelResponse:
    return await ai_service.get_model(model_id)


@router.post("/models/pull", response_model=AIModelResponse)
async def pull_model(payload: AIModelPullRequest, ai_service: AIService = Depends(provide_ai_service)) -> AIModelResponse:
    return await ai_service.pull_model(payload)


@router.delete("/models/{model_id}")
async def delete_model(model_id: UUID, ai_service: AIService = Depends(provide_ai_service)) -> dict[str, str]:
    await ai_service.delete_model(model_id)
    return {"message": "Model deleted"}


@router.get("/providers", response_model=list[AIProviderResponse])
async def list_providers(ai_service: AIService = Depends(provide_ai_service)) -> list[AIProviderResponse]:
    return await ai_service.list_providers()


@router.get("/health", response_model=AIHealthResponse)
async def health(ai_service: AIService = Depends(provide_ai_service)) -> AIHealthResponse:
    return await ai_service.health()


@router.post("/chat", response_model=AIResponse)
async def chat(payload: AIChatRequest, ai_service: AIService = Depends(provide_ai_service)) -> AIResponse:
    return await ai_service.chat(payload)


@router.post("/stream")
async def stream(payload: AIChatRequest, ai_service: AIService = Depends(provide_ai_service)) -> StreamingResponse:
    return StreamingResponse(ai_service.stream_chat(payload), media_type="text/event-stream")


@router.post("/completion", response_model=AIResponse)
async def completion(payload: AICompletionRequest, ai_service: AIService = Depends(provide_ai_service)) -> AIResponse:
    return await ai_service.completion(payload)


@router.post("/conversation", response_model=ConversationResponse)
async def create_conversation(payload: ConversationCreateRequest, ai_service: AIService = Depends(provide_ai_service)) -> ConversationResponse:
    return await ai_service.create_conversation(payload)


@router.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: UUID, ai_service: AIService = Depends(provide_ai_service)) -> ConversationResponse:
    return await ai_service.get_conversation(conversation_id)


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: UUID, ai_service: AIService = Depends(provide_ai_service)) -> dict[str, str]:
    await ai_service.delete_conversation(conversation_id)
    return {"message": "Conversation deleted"}
