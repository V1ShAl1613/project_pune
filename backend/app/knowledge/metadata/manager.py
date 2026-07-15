from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class MetadataManager:
    """Assemble and normalize document metadata for governance and retrieval."""

    def build(self, *, document_id, collection_code: str, source: str | None, category: str, tags: list[str], classification: str | None, owner_id, owner_type: str, version: int, language: str | None, security_level: str, organization_id, workspace_id, checksum: str, created_at: datetime | None = None, modified_at: datetime | None = None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        now = datetime.now(UTC)
        payload = {
            "document_id": str(document_id),
            "collection": collection_code,
            "source": source,
            "category": category,
            "tags": tags,
            "classification": classification,
            "owner_id": str(owner_id) if owner_id else None,
            "owner_type": owner_type,
            "version": version,
            "language": language,
            "security_level": security_level,
            "organization_id": str(organization_id) if organization_id else None,
            "workspace_id": str(workspace_id) if workspace_id else None,
            "checksum": checksum,
            "created_at": (created_at or now).isoformat(),
            "modified_at": (modified_at or now).isoformat(),
        }
        if extra:
            payload.update(extra)
        return payload
