from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.grc.models import AIGovernanceRecord, Assessment, Audit, ComplianceReport, Control, Evidence, Finding, Framework, Policy, PolicyVersion, RiskRegister


@dataclass(slots=True)
class GRCRepository:
    session: AsyncSession | None = None
    frameworks: list[Framework] = field(default_factory=list)
    policies: list[Policy] = field(default_factory=list)
    policy_versions: list[PolicyVersion] = field(default_factory=list)
    controls: list[Control] = field(default_factory=list)
    assessments: list[Assessment] = field(default_factory=list)
    audits: list[Audit] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    risks: list[RiskRegister] = field(default_factory=list)
    reports: list[ComplianceReport] = field(default_factory=list)
    ai_governance_records: list[AIGovernanceRecord] = field(default_factory=list)

    async def add_framework(self, framework: Framework) -> Framework:
        return await self._store(self.frameworks, framework)

    async def add_policy(self, policy: Policy) -> Policy:
        return await self._store(self.policies, policy)

    async def add_policy_version(self, version: PolicyVersion) -> PolicyVersion:
        return await self._store(self.policy_versions, version)

    async def add_control(self, control: Control) -> Control:
        return await self._store(self.controls, control)

    async def add_assessment(self, assessment: Assessment) -> Assessment:
        return await self._store(self.assessments, assessment)

    async def add_audit(self, audit: Audit) -> Audit:
        return await self._store(self.audits, audit)

    async def add_finding(self, finding: Finding) -> Finding:
        return await self._store(self.findings, finding)

    async def add_evidence(self, evidence: Evidence) -> Evidence:
        return await self._store(self.evidence, evidence)

    async def add_risk(self, risk: RiskRegister) -> RiskRegister:
        return await self._store(self.risks, risk)

    async def add_report(self, report: ComplianceReport) -> ComplianceReport:
        return await self._store(self.reports, report)

    async def add_ai_governance(self, record: AIGovernanceRecord) -> AIGovernanceRecord:
        return await self._store(self.ai_governance_records, record)

    async def list_frameworks(self) -> list[Framework]:
        return list(self.frameworks)

    async def list_policies(self) -> list[Policy]:
        return list(self.policies)

    async def list_controls(self) -> list[Control]:
        return list(self.controls)

    async def list_assessments(self) -> list[Assessment]:
        return list(self.assessments)

    async def list_audits(self) -> list[Audit]:
        return list(self.audits)

    async def list_findings(self) -> list[Finding]:
        return list(self.findings)

    async def list_evidence(self) -> list[Evidence]:
        return list(self.evidence)

    async def list_risks(self) -> list[RiskRegister]:
        return list(self.risks)

    async def list_reports(self) -> list[ComplianceReport]:
        return list(self.reports)

    async def list_ai_governance(self) -> list[AIGovernanceRecord]:
        return list(self.ai_governance_records)

    async def _store(self, collection: list[Any], record: Any) -> Any:
        if self.session is None:
            collection.append(record)
            return record
        self.session.add(record)
        await self.session.flush()
        collection.append(record)
        return record
