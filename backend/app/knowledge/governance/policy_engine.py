from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.settings import AppSettings


@dataclass(slots=True)
class GovernanceEngine:
    """Evaluate document and collection policies before processing or retrieval."""

    settings: AppSettings

    def evaluate(self, *, collection_security_level: str, document_security_level: str, owner_type: str, owner_id: str | None, metadata: dict[str, Any], policies: list[dict[str, Any]]) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []
        if self._requires_restriction(collection_security_level, document_security_level):
            violations.append({"code": "security_level_mismatch", "message": "Document security level exceeds collection scope"})
        for policy in policies:
            if policy.get("is_enforced") and policy.get("policy_type") == "retention" and metadata.get("retention_policy") is None:
                violations.append({"code": "retention_missing", "message": "Retention policy required"})
        allowed = not violations
        return {"allowed": allowed, "violations": violations, "owner_type": owner_type, "owner_id": owner_id}

    def should_mask(self, classification: str | None, security_level: str) -> bool:
        return security_level in {"confidential", "restricted"} or (classification or "").lower() in {"secret", "restricted"}

    def retention_due(self, created_at_iso: str, retention_days: int) -> bool:
        from datetime import datetime, timedelta

        created_at = datetime.fromisoformat(created_at_iso)
        return datetime.now(created_at.tzinfo) >= created_at + timedelta(days=retention_days)

    def _requires_restriction(self, collection_security_level: str, document_security_level: str) -> bool:
        order = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
        return order.get(document_security_level, 1) > order.get(collection_security_level, 1)
