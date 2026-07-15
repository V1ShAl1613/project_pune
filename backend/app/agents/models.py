"""SQLAlchemy models for agent registry, runtime, orchestration, and governance."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, Uuid

from app.database.models.base import BaseModel, TimestampMixin, UUIDMixin


class AgentStatus(StrEnum):
    DRAFT = "draft"
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    DESTROYED = "destroyed"


class TaskStatus(StrEnum):
    QUEUED = "queued"
    ROUTED = "routed"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class WorkflowStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Agent(BaseModel, UUIDMixin, TimestampMixin):
    """Registry entry describing a generic agent."""

    __tablename__ = "agents"

    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    namespace: Mapped[str] = mapped_column(String(128), nullable=False, default="default", index=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")
    agent_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=AgentStatus.REGISTERED.value, index=True)
    capabilities: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    dependencies: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=50, index=True)
    health: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    governance_policy: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class AgentCapability(BaseModel, UUIDMixin, TimestampMixin):
    """Capability registration for an agent."""

    __tablename__ = "agent_capabilities"

    agent_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class AgentConfiguration(BaseModel, UUIDMixin, TimestampMixin):
    """Configuration snapshot for an agent or runtime component."""

    __tablename__ = "agent_configurations"

    agent_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    value: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Workflow(BaseModel, UUIDMixin, TimestampMixin):
    """Workflow definition used by the orchestration engine."""

    __tablename__ = "workflows"

    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")
    description: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    definition: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=WorkflowStatus.DRAFT.value, index=True)
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    policy: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)


class AgentTask(BaseModel, UUIDMixin, TimestampMixin):
    """Task queued for agent execution."""

    __tablename__ = "agent_tasks"

    workflow_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True, index=True)
    agent_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    parent_task_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("agent_tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(64), nullable=False, default="general", index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=TaskStatus.QUEUED.value, index=True)
    mode: Mapped[str] = mapped_column(String(32), nullable=False, default="async")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=50, index=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    timeout_seconds: Mapped[float] = mapped_column(Float, nullable=False, default=300.0)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    output_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WorkflowExecution(BaseModel, UUIDMixin, TimestampMixin):
    """Execution record for a workflow run."""

    __tablename__ = "workflow_executions"

    workflow_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("workflows.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=WorkflowStatus.RUNNING.value, index=True)
    input_context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    output_context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class AgentExecution(BaseModel, UUIDMixin, TimestampMixin):
    """Execution record for an individual agent task."""

    __tablename__ = "agent_executions"

    agent_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), index=True)
    task_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("agent_tasks.id", ondelete="CASCADE"), index=True)
    workflow_execution_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("workflow_executions.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=TaskStatus.RUNNING.value, index=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    output_context: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AgentPolicy(BaseModel, UUIDMixin, TimestampMixin):
    """Governance policy describing approvals, limits, and retention."""

    __tablename__ = "agent_policies"

    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="1.0.0")
    rules: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    approval_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    usage_policy: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    security_policy: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    retention_policy: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class AgentAudit(BaseModel, UUIDMixin, TimestampMixin):
    """Audit trail entry for agent lifecycle and orchestration events."""

    __tablename__ = "agent_audits"

    actor: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    target_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, default="info")


class AgentMetrics(BaseModel, UUIDMixin, TimestampMixin):
    """Point-in-time metrics for registry and runtime monitoring."""

    __tablename__ = "agent_metrics"

    agent_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    metric_unit: Mapped[str] = mapped_column(String(32), nullable=False, default="count")
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
