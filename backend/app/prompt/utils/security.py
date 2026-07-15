from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable


DEFAULT_FORBIDDEN_KEYWORDS = (
    "ignore previous",
    "bypass",
    "reveal secrets",
    "system prompt",
    "developer message",
    "jailbreak",
)

DEFAULT_SECRET_PATTERNS = (
    r"api[_ -]?key",
    r"bearer\s+[A-Za-z0-9._-]+",
    r"sk-[A-Za-z0-9]{16,}",
    r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9._-]{10,}\.[A-Za-z0-9._-]{10,}",
)


@dataclass(slots=True)
class PromptSecurityEngine:
    """Prompt security checks for injection, secrets, and masking."""

    forbidden_keywords: tuple[str, ...] = DEFAULT_FORBIDDEN_KEYWORDS
    secret_patterns: tuple[str, ...] = DEFAULT_SECRET_PATTERNS
    injection_patterns: tuple[str, ...] = (
        r"\{\{\s*.*?(system|developer|assistant).*?\}\}",
        r"<script[^>]*>.*?</script>",
        r"<\?xml",
        r"```[a-zA-Z]*",
    )
    compiled_secret_patterns: list[re.Pattern[str]] = field(init=False, default_factory=list)
    compiled_injection_patterns: list[re.Pattern[str]] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self.compiled_secret_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.secret_patterns]
        self.compiled_injection_patterns = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in self.injection_patterns]

    def find_violations(self, text: str) -> list[str]:
        lowered = text.lower()
        violations = [keyword for keyword in self.forbidden_keywords if keyword in lowered]
        violations.extend(pattern.pattern for pattern in self.compiled_injection_patterns if pattern.search(text))
        return violations

    def contains_secrets(self, text: str) -> bool:
        return any(pattern.search(text) for pattern in self.compiled_secret_patterns)

    def mask_secrets(self, text: str) -> str:
        masked = text
        for pattern in self.compiled_secret_patterns:
            masked = pattern.sub("[REDACTED]", masked)
        return masked

    def sanitize_text(self, text: str) -> str:
        return text.replace("\r\n", "\n").replace("\r", "\n").strip()
