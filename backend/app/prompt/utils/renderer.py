from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any


PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_.:-]+)\s*}}")


@dataclass(slots=True)
class PromptRenderer:
    """Safe prompt renderer with simple placeholder expansion."""

    def extract_variables(self, template: str) -> list[str]:
        return list(dict.fromkeys(PLACEHOLDER_PATTERN.findall(template)))

    def render(self, template: str, variables: dict[str, Any], *, environment: dict[str, str] | None = None) -> str:
        values = {**self._environment_values(environment), **self._normalize_variables(variables)}

        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            value = values.get(key)
            return "" if value is None else str(value)

        return PLACEHOLDER_PATTERN.sub(replace, template)

    def _normalize_variables(self, variables: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for key, value in variables.items():
            normalized[str(key)] = value
        return normalized

    def _environment_values(self, environment: dict[str, str] | None) -> dict[str, str]:
        source = environment or os.environ
        return {key: value for key, value in source.items() if isinstance(key, str)}
