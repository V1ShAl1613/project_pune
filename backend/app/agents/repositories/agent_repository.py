"""Database repository for agent runtime records."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.models import Agent, AgentAudit, AgentCapability, AgentConfiguration, AgentExecution, AgentMetrics, AgentPolicy, AgentTask, Workflow, WorkflowExecution
from app.database.repositories.base import CRUDRepository, PaginationParams, Page


class AgentRepository:
    """Convenience repository for the agent domain models."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.agents = CRUDRepository(session, Agent)
        self.capabilities = CRUDRepository(session, AgentCapability)
        self.tasks = CRUDRepository(session, AgentTask)
        self.workflows = CRUDRepository(session, Workflow)
        self.workflow_executions = CRUDRepository(session, WorkflowExecution)
        self.agent_executions = CRUDRepository(session, AgentExecution)
        self.policies = CRUDRepository(session, AgentPolicy)
        self.audits = CRUDRepository(session, AgentAudit)
        self.metrics = CRUDRepository(session, AgentMetrics)
        self.configurations = CRUDRepository(session, AgentConfiguration)

    async def list_agents(self, *, page: int = 1, page_size: int = 50, search: str | None = None) -> Page[Agent]:
        return await self.agents.paginate(PaginationParams(page=page, page_size=page_size), search=search, search_fields=("name", "namespace", "agent_type", "status"))

    async def list_tasks(self, *, page: int = 1, page_size: int = 50, search: str | None = None) -> Page[AgentTask]:
        return await self.tasks.paginate(PaginationParams(page=page, page_size=page_size), search=search, search_fields=("title", "task_type", "status"))

    async def list_workflows(self, *, page: int = 1, page_size: int = 50, search: str | None = None) -> Page[Workflow]:
        return await self.workflows.paginate(PaginationParams(page=page, page_size=page_size), search=search, search_fields=("name", "status"))

    async def create_audit(self, actor: str, action: str, target_type: str, target_id: str, details: dict[str, Any] | None = None, severity: str = "info") -> AgentAudit:
        audit = AgentAudit(actor=actor, action=action, target_type=target_type, target_id=target_id, details=details or {}, severity=severity)
        return await self.audits.create(audit)
