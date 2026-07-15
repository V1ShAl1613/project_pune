"""HTTP API for agent orchestration, registry, tasks, and workflows."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.agents.dependencies import provide_agent_service
from app.agents.schemas import (
    AgentActionRequest,
    AgentCreateRequest,
    AgentHealthResponse,
    AgentResponse,
    AgentUpdateRequest,
    MessageResponse,
    TaskCreateRequest,
    TaskResponse,
    WorkflowCreateRequest,
    WorkflowExecuteRequest,
    WorkflowExecutionResponse,
    WorkflowResponse,
)
from app.agents.services.agent_service import AgentService


router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentResponse])
async def list_agents(page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=1, le=500), search: str | None = None, agent_service: AgentService = Depends(provide_agent_service)) -> list[AgentResponse]:
    return await agent_service.list_agents(page=page, page_size=page_size, search=search)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: UUID, agent_service: AgentService = Depends(provide_agent_service)) -> AgentResponse:
    return await agent_service.get_agent(agent_id)


@router.post("", response_model=AgentResponse)
async def create_agent(payload: AgentCreateRequest, agent_service: AgentService = Depends(provide_agent_service)) -> AgentResponse:
    return await agent_service.create_agent(payload)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: UUID, payload: AgentUpdateRequest, agent_service: AgentService = Depends(provide_agent_service)) -> AgentResponse:
    return await agent_service.update_agent(agent_id, payload)


@router.delete("/{agent_id}", response_model=MessageResponse)
async def delete_agent(agent_id: UUID, agent_service: AgentService = Depends(provide_agent_service)) -> MessageResponse:
    await agent_service.delete_agent(agent_id)
    return MessageResponse(message="Agent deleted")


@router.post("/start", response_model=AgentResponse)
async def start_agent(payload: AgentActionRequest, agent_service: AgentService = Depends(provide_agent_service)) -> AgentResponse:
    return await agent_service.start_agent(payload.agent_id)


@router.post("/stop", response_model=AgentResponse)
async def stop_agent(payload: AgentActionRequest, agent_service: AgentService = Depends(provide_agent_service)) -> AgentResponse:
    return await agent_service.stop_agent(payload.agent_id)


@router.post("/restart", response_model=AgentResponse)
async def restart_agent(payload: AgentActionRequest, agent_service: AgentService = Depends(provide_agent_service)) -> AgentResponse:
    return await agent_service.restart_agent(payload.agent_id)


@router.get("/health", response_model=AgentHealthResponse)
async def agent_health(agent_service: AgentService = Depends(provide_agent_service)) -> AgentHealthResponse:
    return agent_service.health()


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=1, le=500), search: str | None = None, agent_service: AgentService = Depends(provide_agent_service)) -> list[TaskResponse]:
    return await agent_service.list_tasks(page=page, page_size=page_size, search=search)


@router.post("/tasks", response_model=TaskResponse)
async def create_task(payload: TaskCreateRequest, agent_service: AgentService = Depends(provide_agent_service)) -> TaskResponse:
    return await agent_service.create_task(payload)


@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(payload: WorkflowCreateRequest, agent_service: AgentService = Depends(provide_agent_service)) -> WorkflowResponse:
    return await agent_service.create_workflow(payload)


@router.get("/workflows", response_model=list[WorkflowResponse])
async def list_workflows(page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=1, le=500), search: str | None = None, agent_service: AgentService = Depends(provide_agent_service)) -> list[WorkflowResponse]:
    return await agent_service.list_workflows(page=page, page_size=page_size, search=search)


@router.post("/workflows/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(payload: WorkflowExecuteRequest, agent_service: AgentService = Depends(provide_agent_service)) -> WorkflowExecutionResponse:
    return await agent_service.execute_workflow(payload)
