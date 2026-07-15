"""Pydantic schemas for the enterprise multi-agent API."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class AgentLifecycleAction(StrEnum):
    START = "start"
    STOP = "stop"
    RESTART = "restart"


class AgentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    namespace: str = Field(default="default", max_length=128)
    version: str = Field(default="1.0.0", max_length=32)
    agent_type: str = Field(min_length=1, max_length=64)
    description: str | None = Field(default=None, max_length=2048)
    capabilities: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    configuration: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=50, ge=0, le=1000)
    is_system: bool = False
    approval_required: bool = False


class AgentUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, max_length=128)
    namespace: str | None = Field(default=None, max_length=128)
    version: str | None = Field(default=None, max_length=32)
    agent_type: str | None = Field(default=None, max_length=64)
    description: str | None = Field(default=None, max_length=2048)
    capabilities: list[str] | None = None
    dependencies: list[str] | None = None
    configuration: dict[str, Any] | None = None
    priority: int | None = Field(default=None, ge=0, le=1000)
    status: str | None = None
    approval_required: bool | None = None


class AgentActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: UUID
    reason: str | None = Field(default=None, max_length=512)


class AgentResponse(BaseModel):
    id: UUID
    name: str
    namespace: str
    version: str
    agent_type: str
    description: str | None
    status: str
    capabilities: list[str]
    dependencies: list[str]
    configuration: dict[str, Any]
    priority: int
    health: dict[str, Any]
    is_system: bool
    approval_required: bool
    created_at: datetime
    updated_at: datetime


class AgentHealthResponse(BaseModel):
    active_agents: int
    running_tasks: int
    completed_tasks: int
    workflow_count: int
    execution_time_ms: float
    failures: int
    retries: int
    queue_size: int
    health_status: str
    timestamp: datetime


class TaskCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=256)
    task_type: str = Field(default="general", max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=50, ge=0, le=1000)
    agent_id: UUID | None = None
    workflow_id: UUID | None = None
    mode: str = Field(default="async", max_length=32)
    timeout_seconds: float = Field(default=300.0, gt=0)
    max_attempts: int = Field(default=3, ge=1, le=20)


class TaskResponse(BaseModel):
    id: UUID
    agent_id: UUID | None
    workflow_id: UUID | None
    title: str
    task_type: str
    status: str
    mode: str
    priority: int
    attempts: int
    max_attempts: int
    timeout_seconds: float
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    context: dict[str, Any]
    metadata_json: dict[str, Any]
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class WorkflowStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    agent_type: str | None = Field(default=None, max_length=64)
    task_type: str = Field(default="general", max_length=64)
    condition: str | None = Field(default=None, max_length=512)
    retry_attempts: int = Field(default=3, ge=0, le=20)
    timeout_seconds: float = Field(default=300.0, gt=0)
    parallel: bool = False
    payload: dict[str, Any] = Field(default_factory=dict)


class WorkflowCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    version: str = Field(default="1.0.0", max_length=32)
    description: str | None = Field(default=None, max_length=2048)
    steps: list[WorkflowStep] = Field(default_factory=list)
    approval_required: bool = False
    policy: dict[str, Any] = Field(default_factory=dict)


class WorkflowExecuteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    workflow_id: UUID
    context: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=50, ge=0, le=1000)
    mode: str = Field(default="async", max_length=32)


class WorkflowResponse(BaseModel):
    id: UUID
    name: str
    version: str
    description: str | None
    definition: dict[str, Any]
    status: str
    approval_required: bool
    policy: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class WorkflowExecutionResponse(BaseModel):
    id: UUID
    workflow_id: UUID
    status: str
    input_context: dict[str, Any]
    output_context: dict[str, Any]
    metadata_json: dict[str, Any]
    started_at: datetime | None
    completed_at: datetime | None
    failure_reason: str | None


class MessageResponse(BaseModel):
    message: str
