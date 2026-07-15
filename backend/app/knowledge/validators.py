from __future__ import annotations

import hashlib
import mimetypes
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.settings import AppSettings
from app.knowledge.schemas import KnowledgeValidationIssue, KnowledgeValidationResponse


SUPPORTED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt",
    "md",
    "csv",
    "json",
    "xml",
    "html",
    "yaml",
    "yml",
    "log",
}


@dataclass(slots=True)
class KnowledgeValidator:
    """Validate document uploads, metadata, and content safety signals."""

    settings: AppSettings

    def validate_document(
        self,
        *,
        file_name: str,
        file_type: str,
        content: str,
        metadata: dict[str, Any] | None = None,
        language: str | None = None,
        checksum: str | None = None,
    ) -> KnowledgeValidationResponse:
        issues: list[KnowledgeValidationIssue] = []
        normalized_type = file_type.lower().lstrip(".")
        if normalized_type not in SUPPORTED_EXTENSIONS:
            issues.append(KnowledgeValidationIssue(code="unsupported_file_type", message="Document type is not supported", details={"file_type": file_type}))

        if len(content) > self.settings.knowledge_max_upload_bytes:
            issues.append(KnowledgeValidationIssue(code="file_too_large", message="Content exceeds configured maximum size", details={"max_bytes": self.settings.knowledge_max_upload_bytes}))

        if not content.strip():
            issues.append(KnowledgeValidationIssue(code="empty_content", message="Document content is empty"))

        if metadata is not None and not self._metadata_is_valid(metadata):
            issues.append(KnowledgeValidationIssue(code="metadata_validation", message="Metadata contains unsupported values"))

        if self.contains_sensitive_data(content):
            issues.append(KnowledgeValidationIssue(code="sensitive_data", message="Sensitive data detected in document content", severity="warning", details={"masked": self.mask_sensitive_data(content)}))

        if not self._encoding_is_valid(content):
            issues.append(KnowledgeValidationIssue(code="encoding_validation", message="Document encoding is not valid UTF-8"))

        return KnowledgeValidationResponse(
            is_valid=not any(issue.severity == "error" for issue in issues),
            issues=issues,
            checksum=checksum,
            content_length=len(content),
            language=language,
            metadata={"file_name": file_name, "file_type": normalized_type},
        )

    def checksum(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def language_guess(self, content: str) -> str | None:
        if not self.settings.knowledge_language_detection_enabled:
            return None
        ascii_letters = sum(1 for char in content if char.isascii() and char.isalpha())
        non_ascii_letters = sum(1 for char in content if not char.isascii() and char.isalpha())
        if ascii_letters == 0 and non_ascii_letters == 0:
            return None
        if non_ascii_letters > ascii_letters:
            return "non-en"
        return "en"

    def detect_encoding(self, content: str) -> str:
        return "utf-8" if self._encoding_is_valid(content) else "binary"

    def contains_sensitive_data(self, content: str) -> bool:
        if not self.settings.knowledge_enable_sensitive_detection:
            return False
        patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.settings.knowledge_sensitive_patterns]
        return any(pattern.search(content) for pattern in patterns)

    def mask_sensitive_data(self, content: str) -> str:
        masked = content
        patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.settings.knowledge_sensitive_patterns]
        for pattern in patterns:
            masked = pattern.sub("[REDACTED]", masked)
        return masked

    def infer_mime_type(self, file_name: str, file_type: str) -> str | None:
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type:
            return mime_type
        normalized_type = file_type.lower().lstrip(".")
        mapping = {
            "md": "text/markdown",
            "csv": "text/csv",
            "json": "application/json",
            "xml": "application/xml",
            "html": "text/html",
            "yaml": "text/yaml",
            "yml": "text/yaml",
            "log": "text/plain",
            "txt": "text/plain",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "pdf": "application/pdf",
        }
        return mapping.get(normalized_type)

    def _metadata_is_valid(self, metadata: dict[str, Any]) -> bool:
        return all(isinstance(key, str) and not key.startswith("$") for key in metadata)

    def _encoding_is_valid(self, content: str) -> bool:
        if not self.settings.knowledge_encoding_validation_enabled:
            return True
        try:
            content.encode("utf-8")
        except UnicodeEncodeError:
            return False
        return True

    def normalize_path(self, path: str) -> str:
        return str(Path(path).expanduser().resolve())
