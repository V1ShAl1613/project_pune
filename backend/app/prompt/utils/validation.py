from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass
from typing import Any

from app.prompt.schemas import PromptValidationIssue, PromptValidationResponse
from app.prompt.utils.renderer import PLACEHOLDER_PATTERN, PromptRenderer
from app.prompt.utils.security import PromptSecurityEngine


@dataclass(slots=True)
class PromptValidationEngine:
    """Validation engine for syntax, variables, content, and policy checks."""

    renderer: PromptRenderer
    security: PromptSecurityEngine

    def validate(
        self,
        template: str,
        *,
        variables: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        output_format: str | None = None,
        max_length: int | None = None,
        required_variables: list[str] | None = None,
    ) -> PromptValidationResponse:
        variables = variables or {}
        context = context or {}
        combined = {**context, **variables}
        rendered = self.renderer.render(template, combined)
        issues: list[PromptValidationIssue] = []

        if max_length is not None and len(rendered) > max_length:
            issues.append(PromptValidationIssue(code="max_length", message="Rendered prompt exceeds maximum length", details={"max_length": max_length, "actual": len(rendered)}))

        placeholder_variables = self.renderer.extract_variables(template)
        missing = [name for name in (required_variables or placeholder_variables) if name not in combined]
        if missing:
            issues.append(PromptValidationIssue(code="required_variables", message="Required variables are missing", details={"missing": missing}))

        duplicate_variables = self._duplicate_variables(placeholder_variables)
        if duplicate_variables:
            issues.append(PromptValidationIssue(code="duplicate_variables", message="Duplicate placeholders found", details={"duplicates": duplicate_variables}))

        unused_variables = [name for name in combined if name not in placeholder_variables]
        if unused_variables:
            issues.append(PromptValidationIssue(code="unused_variables", message="Unused variables supplied", severity="warning", details={"unused": unused_variables}))

        syntax_issue = self._validate_placeholder_integrity(template)
        if syntax_issue is not None:
            issues.append(syntax_issue)

        content_violations = self.security.find_violations(rendered)
        if content_violations:
            issues.append(PromptValidationIssue(code="security_policy", message="Forbidden or suspicious prompt content detected", details={"violations": content_violations}))

        if self.security.contains_secrets(rendered):
            issues.append(PromptValidationIssue(code="secret_detection", message="Sensitive data detected in prompt", details={"masked": self.security.mask_secrets(rendered)}))

        if output_format == "json":
            json_issue = self._validate_json(rendered)
            if json_issue is not None:
                issues.append(json_issue)
        elif output_format == "xml":
            xml_issue = self._validate_xml(rendered)
            if xml_issue is not None:
                issues.append(xml_issue)
        elif output_format == "markdown":
            markdown_issue = self._validate_markdown(rendered)
            if markdown_issue is not None:
                issues.append(markdown_issue)
        elif output_format == "yaml":
            yaml_issue = self._validate_yaml(rendered)
            if yaml_issue is not None:
                issues.append(yaml_issue)

        token_estimate = self.estimate_tokens(rendered)
        is_valid = not any(issue.severity == "error" for issue in issues)
        return PromptValidationResponse(
            is_valid=is_valid,
            token_estimate=token_estimate,
            length=len(rendered),
            rendered_prompt=rendered,
            issues=issues,
            metadata={"output_format": output_format},
        )

    def estimate_tokens(self, text: str) -> int:
        return max(1, (len(text) + 3) // 4)

    def _duplicate_variables(self, variables: list[str]) -> list[str]:
        duplicates: list[str] = []
        seen: set[str] = set()
        for variable in variables:
            if variable in seen and variable not in duplicates:
                duplicates.append(variable)
            seen.add(variable)
        return duplicates

    def _validate_placeholder_integrity(self, template: str) -> PromptValidationIssue | None:
        open_count = template.count("{{")
        close_count = template.count("}}");
        if open_count != close_count:
            return PromptValidationIssue(code="template_syntax", message="Unbalanced template placeholders")
        if re.search(r"{{\s*}}", template):
            return PromptValidationIssue(code="template_syntax", message="Empty placeholder detected")
        return None

    def _validate_json(self, rendered: str) -> PromptValidationIssue | None:
        try:
            json.loads(rendered)
        except json.JSONDecodeError as exc:
            return PromptValidationIssue(code="json_validation", message="Rendered prompt is not valid JSON", details={"error": str(exc)})
        return None

    def _validate_xml(self, rendered: str) -> PromptValidationIssue | None:
        try:
            ElementTree.fromstring(rendered)
        except ElementTree.ParseError as exc:
            return PromptValidationIssue(code="xml_validation", message="Rendered prompt is not valid XML", details={"error": str(exc)})
        return None

    def _validate_markdown(self, rendered: str) -> PromptValidationIssue | None:
        if rendered.count("```") % 2 != 0:
            return PromptValidationIssue(code="markdown_validation", message="Unbalanced fenced code blocks detected")
        return None

    def _validate_yaml(self, rendered: str) -> PromptValidationIssue | None:
        lines = [line for line in rendered.splitlines() if line.strip()]
        if not lines:
            return PromptValidationIssue(code="yaml_validation", message="YAML prompt cannot be empty")
        if not any(":" in line for line in lines):
            return PromptValidationIssue(code="yaml_validation", message="Rendered prompt does not resemble YAML")
        return None
