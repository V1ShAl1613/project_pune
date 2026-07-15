from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import AuditMixin, BaseModel, SoftDeleteMixin, TimestampMixin, UUIDMixin, VersionMixin


class PromptCategory(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Canonical prompt category used to organize templates and governance."""

    __tablename__ = "prompt_categories"
    __table_args__ = (UniqueConstraint("code", name="uq_prompt_categories_code"), Index("ix_prompt_categories_status", "status"))

    code: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    category_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    prompts: Mapped[list[Prompt]] = relationship(back_populates="category", cascade="all, delete-orphan")


class Prompt(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Prompt registry entry with ownership, labels, and lifecycle state."""

    __tablename__ = "prompts"
    __table_args__ = (
        UniqueConstraint("code", name="uq_prompts_code"),
        Index("ix_prompts_category_status", "category_id", "status"),
        Index("ix_prompts_owner", "owner_type", "owner_id"),
        Index("ix_prompts_search", "name", "status"),
    )

    category_id: Mapped[UUID | None] = mapped_column(ForeignKey("prompt_categories.id", ondelete="SET NULL"), nullable=True)
    code: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_type: Mapped[str] = mapped_column(String(64), nullable=False, default="organization")
    owner_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    labels: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    archived_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    category: Mapped[PromptCategory | None] = relationship(back_populates="prompts")
    templates: Mapped[list[PromptTemplate]] = relationship(back_populates="prompt", cascade="all, delete-orphan")
    versions: Mapped[list[PromptVersion]] = relationship(back_populates="prompt", cascade="all, delete-orphan")
    variables: Mapped[list[PromptVariable]] = relationship(back_populates="prompt", cascade="all, delete-orphan")
    policies: Mapped[list[PromptPolicy]] = relationship(back_populates="prompt", cascade="all, delete-orphan")
    executions: Mapped[list[PromptExecution]] = relationship(back_populates="prompt", cascade="all, delete-orphan")
    audits: Mapped[list[PromptAudit]] = relationship(back_populates="prompt", cascade="all, delete-orphan")
    approvals: Mapped[list[PromptApproval]] = relationship(back_populates="prompt", cascade="all, delete-orphan")
    analytics: Mapped[list[PromptAnalytics]] = relationship(back_populates="prompt", cascade="all, delete-orphan")


class PromptTemplate(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Prompt template content for a specific prompt and format."""

    __tablename__ = "prompt_templates"
    __table_args__ = (
        Index("ix_prompt_templates_prompt_type", "prompt_id", "template_type"),
        Index("ix_prompt_templates_status", "status"),
    )

    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    template_type: Mapped[str] = mapped_column(String(32), nullable=False)
    template_format: Mapped[str] = mapped_column(String(32), nullable=False, default="text")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    compiled_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    template_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    prompt: Mapped[Prompt] = relationship(back_populates="templates")


class PromptVersion(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Version history for prompt content and governance actions."""

    __tablename__ = "prompt_versions"
    __table_args__ = (
        UniqueConstraint("prompt_id", "version_number", name="uq_prompt_versions_prompt_version"),
        Index("ix_prompt_versions_prompt_status", "prompt_id", "status"),
        Index("ix_prompt_versions_approval", "approval_status"),
    )

    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    approval_status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    rollback_from_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("prompt_versions.id", ondelete="SET NULL"), nullable=True)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rendered_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    version_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    prompt: Mapped[Prompt] = relationship(back_populates="versions", foreign_keys=[prompt_id])


class PromptVariable(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Prompt variable catalog entry used for validation and injection."""

    __tablename__ = "prompt_variables"
    __table_args__ = (
        UniqueConstraint("prompt_id", "name", name="uq_prompt_variables_prompt_name"),
        Index("ix_prompt_variables_prompt_scope", "prompt_id", "scope"),
    )

    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    variable_type: Mapped[str] = mapped_column(String(32), nullable=False, default="static")
    scope: Mapped[str] = mapped_column(String(32), nullable=False, default="runtime")
    source: Mapped[str | None] = mapped_column(String(128), nullable=True)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_secret: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mask_output: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    variable_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    prompt: Mapped[Prompt] = relationship(back_populates="variables")


class PromptPolicy(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Policy definition used to govern prompt lifecycle and execution."""

    __tablename__ = "prompt_policies"
    __table_args__ = (Index("ix_prompt_policies_prompt_scope", "prompt_id", "scope"),)

    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    scope: Mapped[str] = mapped_column(String(32), nullable=False)
    policy_type: Mapped[str] = mapped_column(String(32), nullable=False)
    is_enforced: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    policy_rules: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    policy_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    prompt: Mapped[Prompt] = relationship(back_populates="policies")


class PromptExecution(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Immutable execution log for prompt runs and streaming sessions."""

    __tablename__ = "prompt_executions"
    __table_args__ = (
        Index("ix_prompt_executions_prompt_status", "prompt_id", "status"),
        Index("ix_prompt_executions_created_at", "created_at"),
    )

    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    version_id: Mapped[UUID | None] = mapped_column(ForeignKey("prompt_versions.id", ondelete="SET NULL"), nullable=True)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="success")
    stream_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    input_variables: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    rendered_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    output_text: Mapped[str] = mapped_column(Text, nullable=False)
    input_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    output_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    execution_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    tokens_in: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    prompt: Mapped[Prompt] = relationship(back_populates="executions")


class PromptAudit(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Audit record for governance events such as publish, rollback, and validation."""

    __tablename__ = "prompt_audits"
    __table_args__ = (Index("ix_prompt_audits_prompt_action", "prompt_id", "action"),)

    prompt_id: Mapped[UUID | None] = mapped_column(ForeignKey("prompts.id", ondelete="SET NULL"), nullable=True)
    version_id: Mapped[UUID | None] = mapped_column(ForeignKey("prompt_versions.id", ondelete="SET NULL"), nullable=True)
    execution_id: Mapped[UUID | None] = mapped_column(ForeignKey("prompt_executions.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    actor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    before_state: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    after_state: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    audit_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    prompt: Mapped[Prompt | None] = relationship(back_populates="audits")


class PromptApproval(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Approval workflow record for prompt promotion and release."""

    __tablename__ = "prompt_approvals"
    __table_args__ = (Index("ix_prompt_approvals_prompt_status", "prompt_id", "status"),)

    prompt_id: Mapped[UUID] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False)
    version_id: Mapped[UUID] = mapped_column(ForeignKey("prompt_versions.id", ondelete="CASCADE"), nullable=False)
    approver: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    approval_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    prompt: Mapped[Prompt] = relationship(back_populates="approvals")


class PromptAnalytics(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Analytics snapshot for registry, execution, and adoption metrics."""

    __tablename__ = "prompt_analytics"
    __table_args__ = (Index("ix_prompt_analytics_prompt_metric", "prompt_id", "metric_name"),)

    prompt_id: Mapped[UUID | None] = mapped_column(ForeignKey("prompts.id", ondelete="SET NULL"), nullable=True)
    version_id: Mapped[UUID | None] = mapped_column(ForeignKey("prompt_versions.id", ondelete="SET NULL"), nullable=True)
    metric_name: Mapped[str] = mapped_column(String(128), nullable=False)
    metric_value: Mapped[float] = mapped_column(nullable=False, default=0.0)
    metric_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    dimension_data: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    analytics_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    prompt: Mapped[Prompt | None] = relationship(back_populates="analytics")


class PromptTemplateSeed(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    """Optional seed row used to persist platform template starters."""

    __tablename__ = "prompt_template_seeds"
    __table_args__ = (UniqueConstraint("code", name="uq_prompt_template_seeds_code"),)

    code: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_type: Mapped[str] = mapped_column(String(32), nullable=False)
    template_format: Mapped[str] = mapped_column(String(32), nullable=False, default="text")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    seed_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
