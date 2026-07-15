"""Application service for agent registry, runtime, and orchestration workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.agents.context import ContextEnvelope
from app.agents.core.contracts import AgentExecutionContext, AgentExecutionResult, BaseAgent
from app.agents.governance import GovernanceEngine
from app.agents.models import Agent, AgentAudit, AgentMetrics, AgentTask, Workflow, WorkflowExecution
from app.agents.monitoring import AgentHealthSnapshot
from app.agents.orchestrator.orchestrator import TaskOrchestrator, WorkflowEngine
from app.agents.repositories.agent_repository import AgentRepository
from app.agents.runtime.engine import AgentManager
from app.agents.schemas import AgentCreateRequest, AgentUpdateRequest, TaskCreateRequest, WorkflowCreateRequest, WorkflowExecuteRequest, WorkflowResponse, WorkflowExecutionResponse, TaskResponse, AgentHealthResponse, AgentResponse
from app.agents.tasks.models import TaskEnvelope
from app.agents.workflows.models import WorkflowDefinition, WorkflowStepDefinition


@dataclass(slots=True)
class AgentService:
    """High-level use-case service for the agent platform."""

    repository: AgentRepository | None = None
    manager: AgentManager = field(default_factory=AgentManager)
    orchestrator: TaskOrchestrator = field(default_factory=TaskOrchestrator)
    workflow_engine: WorkflowEngine = field(default_factory=WorkflowEngine)
    governance_engine: GovernanceEngine = field(default_factory=GovernanceEngine)

    async def list_agents(self, *, page: int = 1, page_size: int = 50, search: str | None = None) -> list[AgentResponse]:
        if self.repository is None:
            return [self._to_agent_response(item) for item in self.manager.registry.list()]
        page_result = await self.repository.list_agents(page=page, page_size=page_size, search=search)
        return [self._to_agent_response(item) for item in page_result.items]

    async def get_agent(self, agent_id: UUID) -> AgentResponse:
        if self.repository is None:
            metadata = self.manager.registry.get_metadata(agent_id)
            if metadata is None:
                raise KeyError("Agent not found")
            return AgentResponse(
                id=metadata.agent_id,
                name=metadata.name,
                namespace=metadata.namespace,
                version=metadata.version,
                agent_type=metadata.agent_type,
                description=None,
                status=metadata.status,
                capabilities=metadata.capabilities,
                dependencies=metadata.dependencies,
                configuration=metadata.configuration,
                priority=metadata.priority,
                health=metadata.health,
                is_system=False,
                approval_required=False,
                created_at=metadata.registered_at,
                updated_at=metadata.registered_at,
            )
        agent = await self.repository.agents.get_by_id(agent_id)
        if agent is None:
            raise KeyError("Agent not found")
        return self._to_agent_response(agent)

    async def create_agent(self, payload: AgentCreateRequest) -> AgentResponse:
        agent = Agent(
            name=payload.name,
            namespace=payload.namespace,
            version=payload.version,
            agent_type=payload.agent_type,
            description=payload.description,
            status="draft",
            capabilities=payload.capabilities,
            dependencies=payload.dependencies,
            configuration=payload.configuration,
            priority=payload.priority,
            health={"status": "healthy"},
            is_system=payload.is_system,
            approval_required=payload.approval_required,
            governance_policy={},
        )
        if self.repository is None:
            agent.id = uuid4()
            now = datetime.now(timezone.utc)
            agent.created_at = now
            agent.updated_at = now
        if self.repository is not None:
            agent = await self.repository.agents.create(agent)
            await self.repository.create_audit("system", "agent_registration", "agent", str(agent.id), {"name": agent.name})
        self.manager.register(
            BaseAgentProxy(agent),
            namespace=payload.namespace,
            configuration=payload.configuration,
            priority=payload.priority,
            dependencies=payload.dependencies,
        )
        return self._to_agent_response(agent)

    async def update_agent(self, agent_id: UUID, payload: AgentUpdateRequest) -> AgentResponse:
        if self.repository is None:
            metadata = self.manager.registry.get_metadata(agent_id)
            if metadata is None:
                raise KeyError("Agent not found")
            if payload.name is not None:
                metadata.name = payload.name
            if payload.namespace is not None:
                metadata.namespace = payload.namespace
            if payload.version is not None:
                metadata.version = payload.version
            if payload.agent_type is not None:
                metadata.agent_type = payload.agent_type
            if payload.description is not None:
                metadata.configuration["description"] = payload.description
            if payload.capabilities is not None:
                metadata.capabilities = payload.capabilities
            if payload.dependencies is not None:
                metadata.dependencies = payload.dependencies
            if payload.configuration is not None:
                metadata.configuration = payload.configuration
            if payload.priority is not None:
                metadata.priority = payload.priority
            if payload.status is not None:
                metadata.status = payload.status
            return await self.get_agent(agent_id)
        agent = await self.repository.agents.get_by_id(agent_id)
        if agent is None:
            raise KeyError("Agent not found")
        await self.repository.agents.update(agent, {key: value for key, value in payload.model_dump(exclude_none=True).items() if hasattr(agent, key)})
        await self.repository.create_audit("system", "agent_update", "agent", str(agent.id), payload.model_dump(exclude_none=True))
        return self._to_agent_response(agent)

    async def delete_agent(self, agent_id: UUID) -> None:
        if self.repository is None:
            self.manager.registry.unregister(agent_id)
            return
        agent = await self.repository.agents.get_by_id(agent_id)
        if agent is None:
            raise KeyError("Agent not found")
        await self.repository.agents.delete(agent)
        await self.repository.create_audit("system", "agent_delete", "agent", str(agent.id), {})

    async def list_tasks(self, *, page: int = 1, page_size: int = 50, search: str | None = None) -> list[TaskResponse]:
        if self.repository is None:
            return []
        page_result = await self.repository.list_tasks(page=page, page_size=page_size, search=search)
        return [self._to_task_response(item) for item in page_result.items]

    async def create_task(self, payload: TaskCreateRequest) -> TaskResponse:
        task = AgentTask(
            agent_id=payload.agent_id,
            workflow_id=payload.workflow_id,
            title=payload.title,
            task_type=payload.task_type,
            status="queued",
            mode=payload.mode,
            priority=payload.priority,
            attempts=0,
            max_attempts=payload.max_attempts,
            timeout_seconds=payload.timeout_seconds,
            input_payload=payload.payload,
            output_payload={},
            context=payload.context,
            metadata={},
            error_message=None,
        )
        if self.repository is None:
            task.id = uuid4()
            now = datetime.now(timezone.utc)
            task.created_at = now
            task.updated_at = now
        if self.repository is not None:
            task = await self.repository.tasks.create(task)
            await self.repository.create_audit("system", "task_create", "task", str(task.id), payload.model_dump())
        self.orchestrator.submit(
            TaskEnvelope(
                task_id=task.id,
                agent_id=task.agent_id,
                workflow_id=task.workflow_id,
                title=task.title,
                task_type=task.task_type,
                priority=task.priority,
                payload=task.payload_json,
                context=task.context,
                metadata=task.metadata_json,
            )
        )
        return self._to_task_response(task)

    async def start_agent(self, agent_id: UUID) -> AgentResponse:
        await self.manager.lifecycle.start(agent_id)
        return await self.get_agent(agent_id)

    async def stop_agent(self, agent_id: UUID) -> AgentResponse:
        await self.manager.lifecycle.shutdown(agent_id)
        return await self.get_agent(agent_id)

    async def restart_agent(self, agent_id: UUID) -> AgentResponse:
        await self.manager.lifecycle.restart(agent_id)
        return await self.get_agent(agent_id)

    def health(self) -> AgentHealthResponse:
        snapshot: AgentHealthSnapshot = self.manager.health()
        return AgentHealthResponse(
            active_agents=snapshot.active_agents,
            running_tasks=snapshot.running_tasks,
            completed_tasks=snapshot.completed_tasks,
            failed_tasks=snapshot.failures,
            retries=snapshot.retries,
            queue_size=snapshot.queue_size,
            health_status=snapshot.health_status,
            timestamp=snapshot.updated_at,
        )

    async def create_workflow(self, payload: WorkflowCreateRequest) -> WorkflowResponse:
        definition = {"steps": [step.model_dump() for step in payload.steps]}
        workflow = Workflow(
            name=payload.name,
            version=payload.version,
            description=payload.description,
            definition=definition,
            status="validated",
            approval_required=payload.approval_required,
            policy=payload.policy,
        )
        if self.repository is None:
            workflow.id = uuid4()
            now = datetime.now(timezone.utc)
            workflow.created_at = now
            workflow.updated_at = now
        if self.repository is not None:
            workflow = await self.repository.workflows.create(workflow)
            await self.repository.create_audit("system", "workflow_create", "workflow", str(workflow.id), payload.model_dump())
        return self._to_workflow_response(workflow)

    async def list_workflows(self, *, page: int = 1, page_size: int = 50, search: str | None = None) -> list[WorkflowResponse]:
        if self.repository is None:
            return []
        page_result = await self.repository.list_workflows(page=page, page_size=page_size, search=search)
        return [self._to_workflow_response(item) for item in page_result.items]

    async def execute_workflow(self, payload: WorkflowExecuteRequest) -> WorkflowExecutionResponse:
        if self.repository is None:
            raise KeyError("Workflow execution requires a repository-backed service")
        workflow = await self.repository.workflows.get_by_id(payload.workflow_id)
        if workflow is None:
            raise KeyError("Workflow not found")
        workflow_definition = WorkflowDefinition(
            id=workflow.id,
            name=workflow.name,
            version=workflow.version,
            description=workflow.description,
            steps=[
                WorkflowStepDefinition(
                    name=step.get("name", "step"),
                    agent_type=step.get("agent_type"),
                    task_type=step.get("task_type", "general"),
                    condition=step.get("condition"),
                    retry_attempts=step.get("retry_attempts", 3),
                    timeout_seconds=step.get("timeout_seconds", 300.0),
                    parallel=step.get("parallel", False),
                    payload=step.get("payload", {}),
                )
                for step in workflow.definition.get("steps", [])
                if isinstance(step, dict)
            ],
            policy=workflow.policy,
        )
        execution_state = self.workflow_engine.execute(
            workflow=workflow_definition,
            context=ContextEnvelope(metadata=payload.context),
        )
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            status=execution_state.status,
            input_context=payload.context,
            output_context={"history": execution_state.history},
            metadata={"mode": payload.mode, "priority": payload.priority},
            started_at=execution_state.started_at,
            completed_at=execution_state.completed_at,
            failure_reason=None,
        )
        execution = await self.repository.workflow_executions.create(execution)
        await self.repository.create_audit("system", "workflow_execute", "workflow", str(workflow.id), payload.model_dump())
        return self._to_workflow_execution_response(execution)

    def _to_agent_response(self, agent: Agent) -> AgentResponse:
        return AgentResponse(
            id=agent.id or uuid4(),
            name=agent.name,
            namespace=agent.namespace,
            version=agent.version,
            agent_type=agent.agent_type,
            description=agent.description,
            status=agent.status,
            capabilities=agent.capabilities,
            dependencies=agent.dependencies,
            configuration=agent.configuration,
            priority=agent.priority,
            health=agent.health,
            is_system=agent.is_system,
            approval_required=agent.approval_required,
            created_at=agent.created_at or datetime.now(timezone.utc),
            updated_at=agent.updated_at or datetime.now(timezone.utc),
        )

    def _to_task_response(self, task: AgentTask) -> TaskResponse:
        return TaskResponse(
            id=task.id or uuid4(),
            agent_id=task.agent_id,
            workflow_id=task.workflow_id,
            title=task.title,
            task_type=task.task_type,
            status=task.status,
            mode=task.mode,
            priority=task.priority,
            attempts=task.attempts,
            max_attempts=task.max_attempts,
            timeout_seconds=task.timeout_seconds,
            input_payload=task.input_payload,
            output_payload=task.output_payload,
            context=task.context,
            metadata_json=task.metadata_json,
            error_message=task.error_message,
            created_at=task.created_at or datetime.now(timezone.utc),
            updated_at=task.updated_at or datetime.now(timezone.utc),
        )

    def _to_workflow_response(self, workflow: Workflow) -> WorkflowResponse:
        return WorkflowResponse(
            id=workflow.id or uuid4(),
            name=workflow.name,
            version=workflow.version,
            description=workflow.description,
            definition=workflow.definition,
            status=workflow.status,
            approval_required=workflow.approval_required,
            policy=workflow.policy,
            created_at=workflow.created_at or datetime.now(timezone.utc),
            updated_at=workflow.updated_at or datetime.now(timezone.utc),
        )

    def _to_workflow_execution_response(self, execution: WorkflowExecution) -> WorkflowExecutionResponse:
        return WorkflowExecutionResponse(
            id=execution.id or uuid4(),
            workflow_id=execution.workflow_id,
            status=execution.status,
            input_context=execution.input_context,
            output_context=execution.output_context,
            metadata_json=execution.metadata_json,
            started_at=execution.started_at or datetime.now(timezone.utc),
            completed_at=execution.completed_at or datetime.now(timezone.utc),
            failure_reason=execution.failure_reason,
        )


class BaseAgentProxy(BaseAgent):
    """Adapter that allows the registry to store SQLAlchemy-backed agent records as runtime agents."""

    def __init__(self, record: Agent) -> None:
        super().__init__(name=record.name, agent_type=record.agent_type, version=record.version, capabilities=list(record.capabilities))
        self.id = record.id
        self._record = record

    async def execute(self, context: AgentExecutionContext) -> AgentExecutionResult:
        return AgentExecutionResult(success=True, output={"agent_id": str(self._record.id), "context": context.metadata})
