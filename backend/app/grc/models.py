from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Uuid

from app.database.models.base import BaseModel, TimestampMixin, UUIDMixin


class Framework(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "frameworks"
    __table_args__ = (UniqueConstraint("code", name="uq_frameworks_code"),)

    code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    family: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(64), nullable=False, default="1.0")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    control_objectives: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    regulatory_scope: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    framework_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class Policy(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "policies"
    __table_args__ = (UniqueConstraint("code", name="uq_policies_code"),)

    code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    version_label: Mapped[str] = mapped_column(String(64), nullable=False, default="v1")
    owner: Mapped[str] = mapped_column(String(255), nullable=False, default="governance")
    approval_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    frameworks: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    rules: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    exceptions: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    enforcement_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    policy_metadata: Mapped[dict[str, object]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class PolicyVersion(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "policy_versions"
    __table_args__ = (UniqueConstraint("policy_code", "version_label", name="uq_policy_versions_code_version"),)

    policy_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    version_label: Mapped[str] = mapped_column(String(64), nullable=False)
    change_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    version_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class Control(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "controls"
    __table_args__ = (UniqueConstraint("code", name="uq_controls_code"),)

    code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    control_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False, default="control-owner")
    maturity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    frameworks: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    dependencies: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    evidence_requirements: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    testing: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    control_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    version_label: Mapped[str] = mapped_column(String(64), nullable=False, default="v1")


class Assessment(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "assessments"
    __table_args__ = (UniqueConstraint("assessment_code", name="uq_assessments_code"),)

    assessment_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    assessment_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subject_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    frameworks: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    coverage: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    evidence_coverage: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    gap_analysis: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    findings: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    explainability: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    assessment_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class Audit(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "audits"
    __table_args__ = (UniqueConstraint("audit_code", name="uq_audits_code"),)

    audit_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    audit_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    scope: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    checklist: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    timeline: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    tasks: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    findings: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    audit_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class Finding(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "findings"
    __table_args__ = (UniqueConstraint("finding_code", name="uq_findings_code"),)

    finding_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    framework_code: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    control_code: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    evidence: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    remediation: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    finding_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class Evidence(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "evidence"
    __table_args__ = (UniqueConstraint("evidence_code", name="uq_evidence_code"),)

    evidence_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    classification: Mapped[str] = mapped_column(String(32), nullable=False, default="internal")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    storage_ref: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    framework_codes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    control_codes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    validation: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    evidence_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class RiskRegister(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "risk_register"
    __table_args__ = (UniqueConstraint("risk_code", name="uq_risk_register_code"),)

    risk_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    risk_category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    inherent_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    residual_risk: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    risk_treatment: Mapped[str] = mapped_column(String(64), nullable=False, default="mitigate")
    acceptance_status: Mapped[str] = mapped_column(String(32), nullable=False, default="open")
    trend: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    history: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    risk_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ComplianceReport(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "compliance_reports"
    __table_args__ = (UniqueConstraint("report_code", name="uq_compliance_reports_code"),)

    report_code: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subject_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    scorecard: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    framework_coverage: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    control_coverage: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    evidence_summary: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    open_findings: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    report_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class AIGovernanceRecord(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_governance_records"
    __table_args__ = (UniqueConstraint("model_name", "model_provider", name="uq_ai_governance_model_provider"),)

    model_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    model_provider: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    approval_status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    prompt_governance: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    dataset_governance: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    inference_governance: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    bias_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    fairness_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    transparency_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    lifecycle_stage: Mapped[str] = mapped_column(String(64), nullable=False, default="registered")
    ai_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
