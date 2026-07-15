"""Validation helpers for agents, tasks, and workflows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ValidationIssue:
    """Normalized validation issue."""

    code: str
    message: str
    severity: str = "error"
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationReport:
    """Validation result for runtime objects."""

    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)


class AgentValidator:
    """Validates the shape of agent, task, and workflow definitions."""

    def validate_agent(self, *, name: str, agent_type: str, capabilities: list[str], dependencies: list[str]) -> ValidationReport:
        issues: list[ValidationIssue] = []
        if not name.strip():
            issues.append(ValidationIssue(code="name_required", message="Agent name is required"))
        if not agent_type.strip():
            issues.append(ValidationIssue(code="agent_type_required", message="Agent type is required"))
        if len(capabilities) != len({item for item in capabilities if item.strip()}):
            issues.append(ValidationIssue(code="capabilities_duplicate", message="Capabilities must be unique", severity="warning"))
        if len(dependencies) != len({item for item in dependencies if item.strip()}):
            issues.append(ValidationIssue(code="dependencies_duplicate", message="Dependencies must be unique", severity="warning"))
        return ValidationReport(is_valid=not any(issue.severity == "error" for issue in issues), issues=issues)

    def validate_workflow(self, *, name: str, steps: list[dict[str, Any]]) -> ValidationReport:
        issues: list[ValidationIssue] = []
        if not name.strip():
            issues.append(ValidationIssue(code="workflow_name_required", message="Workflow name is required"))
        if not steps:
            issues.append(ValidationIssue(code="workflow_steps_required", message="Workflow must contain at least one step"))
        return ValidationReport(is_valid=not any(issue.severity == "error" for issue in issues), issues=issues)
