from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PromptLifecycleStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PromptVersionStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class PromptApprovalStatus(StrEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    ROLLBACK = "rollback"


class PromptTemplateType(StrEnum):
    SYSTEM = "system"
    DEVELOPER = "developer"
    USER = "user"
    CONTEXT = "context"
    INSTRUCTION = "instruction"
    JSON = "json"
    MARKDOWN = "markdown"
    XML = "xml"
    YAML = "yaml"
    DYNAMIC = "dynamic"


class PromptVariableType(StrEnum):
    STATIC = "static"
    DYNAMIC = "dynamic"
    RUNTIME = "runtime"
    ENVIRONMENT = "environment"
    SECRET = "secret"
    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    SESSION = "session"
    USER = "user"


class PromptPolicyScope(StrEnum):
    SECURITY = "security"
    EXECUTION = "execution"
    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    MODEL = "model"
    APPROVAL = "approval"
    VERSION = "version"
    RETENTION = "retention"


class PromptCategoryCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    code: str
    name: str
    description: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class PromptVariableRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    name: str
    variable_type: PromptVariableType = PromptVariableType.RUNTIME
    scope: str = "runtime"
    source: str | None = None
    required: bool = False
    default_value: str | None = None
    is_secret: bool = False
    mask_output: bool = True
    description: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class PromptPolicyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    scope: PromptPolicyScope
    policy_type: str
    is_enforced: bool = True
    status: str = "active"
    rules: dict[str, object] = Field(default_factory=dict)
    metadata: dict[str, object] = Field(default_factory=dict)


class PromptTemplateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    template_type: PromptTemplateType
    template_format: str = "text"
    content: str
    metadata: dict[str, object] = Field(default_factory=dict)


class PromptCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    code: str
    name: str
    description: str | None = None
    category_code: str | None = None
    owner_type: str = "organization"
    owner_id: UUID | None = None
    labels: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    status: PromptLifecycleStatus = PromptLifecycleStatus.DRAFT
    metadata: dict[str, object] = Field(default_factory=dict)
    template: PromptTemplateRequest
    variables: list[PromptVariableRequest] = Field(default_factory=list)
    policies: list[PromptPolicyRequest] = Field(default_factory=list)

    @field_validator("labels", "tags")
    @classmethod
    def _trim_values(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if item and item.strip()]


class PromptUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    name: str | None = None
    description: str | None = None
    category_code: str | None = None
    owner_type: str | None = None
    owner_id: UUID | None = None
    labels: list[str] | None = None
    tags: list[str] | None = None
    status: PromptLifecycleStatus | None = None
    metadata: dict[str, object] | None = None
    template: PromptTemplateRequest | None = None
    variables: list[PromptVariableRequest] | None = None
    policies: list[PromptPolicyRequest] | None = None


class PromptPublishRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    approver: str | None = None
    comment: str | None = None
    version_id: UUID | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class PromptRollbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    version_id: UUID
    comment: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class PromptValidateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    template: PromptTemplateRequest | None = None
    variables: dict[str, object] = Field(default_factory=dict)
    context: dict[str, object] = Field(default_factory=dict)
    output_format: str | None = None
    max_length: int | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class PromptExecuteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    version_id: UUID | None = None
    model_name: str | None = None
    provider_name: str | None = None
    variables: dict[str, object] = Field(default_factory=dict)
    context: dict[str, object] = Field(default_factory=dict)
    stream: bool = False
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    max_tokens: int | None = Field(default=None, ge=1)
    response_format: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class PromptCategoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    code: str
    name: str
    description: str | None
    status: str
    category_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class PromptTemplateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    prompt_id: UUID
    template_type: str
    template_format: str
    content: str
    compiled_content: str | None
    status: str
    is_active: bool
    template_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class PromptVariableResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    prompt_id: UUID
    name: str
    variable_type: str
    scope: str
    source: str | None
    required: bool
    default_value: str | None
    is_secret: bool
    mask_output: bool
    description: str | None
    variable_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class PromptPolicyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    prompt_id: UUID
    scope: str
    policy_type: str
    is_enforced: bool
    status: str
    policy_rules: dict[str, object]
    policy_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class PromptVersionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    prompt_id: UUID
    version_number: int
    status: str
    approval_status: str
    rollback_from_version_id: UUID | None
    checksum: str
    content: str
    rendered_content: str | None
    version_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class PromptApprovalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    prompt_id: UUID
    version_id: UUID
    approver: str | None
    status: str
    comment: str | None
    approval_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class PromptExecutionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    prompt_id: UUID
    version_id: UUID | None
    model_name: str
    provider_name: str
    status: str
    stream_enabled: bool
    input_variables: dict[str, object]
    rendered_prompt: str
    output_text: str
    input_metadata: dict[str, object]
    output_metadata: dict[str, object]
    execution_metadata: dict[str, object]
    tokens_in: int
    tokens_out: int
    latency_ms: int
    created_at: datetime
    updated_at: datetime


class PromptAnalyticsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    prompt_id: UUID | None
    version_id: UUID | None
    metric_name: str
    metric_value: float
    metric_date: datetime
    dimension_data: dict[str, object]
    analytics_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class PromptValidationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    code: str
    message: str
    severity: str = "error"
    details: dict[str, object] = Field(default_factory=dict)


class PromptValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    prompt_id: UUID | None = None
    version_id: UUID | None = None
    is_valid: bool
    token_estimate: int
    length: int
    rendered_prompt: str
    issues: list[PromptValidationIssue] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class PromptResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    category_id: UUID | None
    code: str
    name: str
    description: str | None
    owner_type: str
    owner_id: UUID | None
    status: str
    labels: list[str]
    tags: list[str]
    archived_reason: str | None
    prompt_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime
    category: PromptCategoryResponse | None = None
    templates: list[PromptTemplateResponse] = Field(default_factory=list)
    versions: list[PromptVersionResponse] = Field(default_factory=list)
    variables: list[PromptVariableResponse] = Field(default_factory=list)
    policies: list[PromptPolicyResponse] = Field(default_factory=list)
    approvals: list[PromptApprovalResponse] = Field(default_factory=list)


class PromptExecutionSimulationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    prompt_id: UUID | None = None
    version_id: UUID | None = None
    rendered_prompt: str
    output_preview: str
    is_streaming: bool
    token_estimate: int
    metadata: dict[str, object] = Field(default_factory=dict)
