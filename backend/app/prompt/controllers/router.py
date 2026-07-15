from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.prompt.dependencies import provide_prompt_service
from app.prompt.schemas import (
    PromptAnalyticsResponse,
    PromptCreateRequest,
    PromptCategoryResponse,
    PromptExecuteRequest,
    PromptExecutionResponse,
    PromptPublishRequest,
    PromptResponse,
    PromptRollbackRequest,
    PromptUpdateRequest,
    PromptValidateRequest,
    PromptValidationResponse,
)
from app.prompt.services.prompt_service import PromptService


router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("", response_model=list[PromptResponse])
async def list_prompts(search: str | None = None, status: str | None = None, category_code: str | None = None, prompt_service: PromptService = Depends(provide_prompt_service)) -> list[PromptResponse]:
    return await prompt_service.list_prompts(search=search, status=status, category_code=category_code)


@router.get("/categories", response_model=list[PromptCategoryResponse])
async def list_categories(prompt_service: PromptService = Depends(provide_prompt_service)) -> list[PromptCategoryResponse]:
    return await prompt_service.list_categories()


@router.get("/analytics", response_model=list[PromptAnalyticsResponse])
async def analytics(prompt_service: PromptService = Depends(provide_prompt_service)) -> list[PromptAnalyticsResponse]:
    return await prompt_service.analytics()


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(prompt_id: UUID, prompt_service: PromptService = Depends(provide_prompt_service)) -> PromptResponse:
    return await prompt_service.get_prompt(prompt_id)


@router.post("", response_model=PromptResponse)
async def create_prompt(payload: PromptCreateRequest, prompt_service: PromptService = Depends(provide_prompt_service)) -> PromptResponse:
    return await prompt_service.create_prompt(payload)


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(prompt_id: UUID, payload: PromptUpdateRequest, prompt_service: PromptService = Depends(provide_prompt_service)) -> PromptResponse:
    return await prompt_service.update_prompt(prompt_id, payload)


@router.delete("/{prompt_id}")
async def delete_prompt(prompt_id: UUID, prompt_service: PromptService = Depends(provide_prompt_service)) -> dict[str, str]:
    await prompt_service.delete_prompt(prompt_id)
    return {"message": "Prompt deleted"}


@router.post("/{prompt_id}/publish", response_model=PromptResponse)
async def publish_prompt(prompt_id: UUID, payload: PromptPublishRequest, prompt_service: PromptService = Depends(provide_prompt_service)) -> PromptResponse:
    return await prompt_service.publish_prompt(prompt_id, payload)


@router.post("/{prompt_id}/rollback", response_model=PromptResponse)
async def rollback_prompt(prompt_id: UUID, payload: PromptRollbackRequest, prompt_service: PromptService = Depends(provide_prompt_service)) -> PromptResponse:
    return await prompt_service.rollback_prompt(prompt_id, payload)


@router.post("/{prompt_id}/validate", response_model=PromptValidationResponse)
async def validate_prompt(prompt_id: UUID, payload: PromptValidateRequest, prompt_service: PromptService = Depends(provide_prompt_service)) -> PromptValidationResponse:
    return await prompt_service.validate_prompt(prompt_id, payload)


@router.post("/{prompt_id}/execute", response_model=PromptExecutionResponse)
async def execute_prompt(prompt_id: UUID, payload: PromptExecuteRequest, prompt_service: PromptService = Depends(provide_prompt_service)) -> PromptExecutionResponse | StreamingResponse:
    execution = await prompt_service.execute_prompt(prompt_id, payload)
    if hasattr(execution, "__aiter__"):
        return StreamingResponse(execution, media_type="text/event-stream")
    return execution


