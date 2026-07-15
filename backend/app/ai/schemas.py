from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AIModelResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    provider_id: UUID
    name: str
    display_name: str
    model_type: str
    status: str
    model_version: str | None
    context_length: int
    supports_streaming: bool
    supports_json: bool
    supports_structured: bool
    default_temperature: float
    default_top_p: float
    priority: int
    is_default: bool
    tags: dict[str, object]
    configuration: dict[str, object]
    model_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class AIProviderResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    name: str
    provider_type: str
    base_url: str | None
    status: str
    priority: int
    provider_metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class AIModelPullRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    name: str = Field(min_length=1, max_length=255)
    provider_name: str | None = None


class AIChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    role: str = Field(min_length=1, max_length=32)
    content: str = Field(min_length=1)


class AIChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    messages: list[AIChatMessage]
    model: str | None = None
    conversation_id: UUID | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    max_tokens: int | None = Field(default=None, ge=1)
    stream: bool = False
    response_format: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, value: list[AIChatMessage]) -> list[AIChatMessage]:
        if not value:
            raise ValueError("messages cannot be empty")
        return value


class AICompletionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    prompt: str = Field(min_length=1)
    model: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=2.0)
    top_p: float | None = Field(default=None, ge=0.0, le=1.0)
    max_tokens: int | None = Field(default=None, ge=1)
    stop: list[str] = Field(default_factory=list)
    stream: bool = False
    metadata: dict[str, object] = Field(default_factory=dict)


class ConversationCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    title: str = Field(min_length=1, max_length=255)
    model: str
    provider: str
    tenant_id: UUID | None = None
    user_id: UUID | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class ConversationMessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    sequence: int
    message_metadata: dict[str, object]
    token_count: int
    created_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    tenant_id: UUID | None
    user_id: UUID | None
    title: str
    status: str
    model_name: str
    model_provider: str
    conversation_metadata: dict[str, object]
    context_window: int
    last_message_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime
    messages: list[ConversationMessageResponse] = Field(default_factory=list)


class AIHealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    status: str
    providers: list[dict[str, object]]
    models: list[dict[str, object]]
    metrics: dict[str, object]


class AIResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    id: str
    provider: str
    model: str
    content: str
    created_at: datetime
    metadata: dict[str, object]


class AIStreamingChunk(BaseModel):
    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    id: str
    provider: str
    model: str
    chunk: str
    done: bool = False
    metadata: dict[str, object] = Field(default_factory=dict)
