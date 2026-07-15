"""Task orchestration and workflow execution engine."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.agents.context import ContextEnvelope
from app.agents.execution.models import ExecutionRecord
from app.agents.tasks.models import TaskEnvelope
from app.agents.validators import AgentValidator
from app.agents.workflows.models import WorkflowDefinition, WorkflowStepDefinition


@dataclass(slots=True)
class WorkflowExecutionState:
    """In-memory workflow execution state used by the engine."""

    execution_id: UUID = field(default_factory=uuid4)
    workflow_id: UUID | None = None
    status: str = "running"
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    history: list[dict[str, Any]] = field(default_factory=list)


class TaskOrchestrator:
    """Routes and records tasks for agent execution."""

    def __init__(self, validator: AgentValidator | None = None) -> None:
        self.validator = validator or AgentValidator()
        self._tasks: list[TaskEnvelope] = []
        self._history: list[ExecutionRecord] = []

    def submit(self, task: TaskEnvelope) -> TaskEnvelope:
        self._tasks.append(task)
        return task

    def history(self) -> list[ExecutionRecord]:
        return list(self._history)

    def queue_size(self) -> int:
        return len(self._tasks)


class WorkflowEngine:
    """Validates and executes workflow definitions."""

    def __init__(self, validator: AgentValidator | None = None) -> None:
        self.validator = validator or AgentValidator()
        self._executions: dict[UUID, WorkflowExecutionState] = {}

    def validate(self, workflow: WorkflowDefinition) -> bool:
        report = self.validator.validate_workflow(
            name=workflow.name,
            steps=[asdict(step) for step in workflow.steps],
        )
        return report.is_valid

    def execute(self, workflow: WorkflowDefinition, context: ContextEnvelope | None = None) -> WorkflowExecutionState:
        state = WorkflowExecutionState(workflow_id=workflow.id)
        self._executions[state.execution_id] = state
        state.history.append({"event": "workflow_started", "workflow_id": str(workflow.id)})
        for index, step in enumerate(workflow.steps):
            state.history.append({"event": "step_executed", "index": index, "name": step.name, "agent_type": step.agent_type, "task_type": step.task_type, "context": context.metadata if context else {}})
        state.status = "completed"
        state.completed_at = datetime.now(timezone.utc)
        state.history.append({"event": "workflow_completed", "workflow_id": str(workflow.id)})
        return state
