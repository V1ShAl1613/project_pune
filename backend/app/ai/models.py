from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import AuditMixin, BaseModel, SoftDeleteMixin, TimestampMixin, UUIDMixin, VersionMixin


class AIProvider(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "ai_providers"
    __table_args__ = (UniqueConstraint("name", name="uq_ai_providers_name"), Index("ix_ai_providers_status", "status"))

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(64), nullable=False)
    base_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    provider_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    models: Mapped[list[AIModel]] = relationship(back_populates="provider", cascade="all, delete-orphan")


class AIModel(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "ai_models"
    __table_args__ = (
        UniqueConstraint("provider_id", "name", name="uq_ai_models_provider_name"),
        Index("ix_ai_models_provider_status", "provider_id", "status"),
        Index("ix_ai_models_default_priority", "is_default", "priority"),
    )

    provider_id: Mapped[UUID] = mapped_column(ForeignKey("ai_providers.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_type: Mapped[str] = mapped_column(String(64), nullable=False, default="local")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="available")
    model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    context_length: Mapped[int] = mapped_column(Integer, nullable=False, default=8192)
    supports_streaming: Mapped[bool] = mapped_column(default=True, nullable=False)
    supports_json: Mapped[bool] = mapped_column(default=True, nullable=False)
    supports_structured: Mapped[bool] = mapped_column(default=True, nullable=False)
    default_temperature: Mapped[float] = mapped_column(nullable=False, default=0.2)
    default_top_p: Mapped[float] = mapped_column(nullable=False, default=0.95)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    is_default: Mapped[bool] = mapped_column(default=False, nullable=False)
    tags: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    configuration: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    model_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    provider: Mapped[AIProvider] = relationship(back_populates="models")
    configurations: Mapped[list[ModelConfiguration]] = relationship(back_populates="model", cascade="all, delete-orphan")
    logs: Mapped[list[InferenceLog]] = relationship(back_populates="model", cascade="all, delete-orphan")
    health_checks: Mapped[list[ProviderHealth]] = relationship(back_populates="model", cascade="all, delete-orphan")


class Conversation(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "ai_conversations"
    __table_args__ = (
        Index("ix_ai_conversations_tenant_status", "tenant_id", "status"),
        Index("ix_ai_conversations_user_updated", "user_id", "updated_at"),
    )

    tenant_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    user_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_provider: Mapped[str] = mapped_column(String(128), nullable=False)
    conversation_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    context_window: Mapped[int] = mapped_column(Integer, nullable=False, default=8192)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    messages: Mapped[list[ConversationMessage]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessage(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "ai_conversation_messages"
    __table_args__ = (
        Index("ix_ai_conversation_messages_conversation_created", "conversation_id", "created_at"),
        Index("ix_ai_conversation_messages_role", "role"),
    )

    conversation_id: Mapped[UUID] = mapped_column(ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    message_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class InferenceLog(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "ai_inference_logs"
    __table_args__ = (
        Index("ix_ai_inference_logs_model_status", "model_id", "status"),
        Index("ix_ai_inference_logs_created_at", "created_at"),
    )

    model_id: Mapped[UUID] = mapped_column(ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    conversation_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    request_id: Mapped[str] = mapped_column(String(128), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    request_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    response_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="success")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    provider_name: Mapped[str] = mapped_column(String(128), nullable=False)

    model: Mapped[AIModel | None] = relationship(back_populates="logs")


class ProviderHealth(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "ai_provider_health"
    __table_args__ = (
        Index("ix_ai_provider_health_provider_status", "provider_id", "status"),
        Index("ix_ai_provider_health_model_id", "model_id"),
    )

    provider_id: Mapped[UUID] = mapped_column(ForeignKey("ai_providers.id", ondelete="CASCADE"), nullable=False)
    model_id: Mapped[UUID | None] = mapped_column(ForeignKey("ai_models.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="healthy")
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    memory_usage_mb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gpu_usage_pct: Mapped[float | None] = mapped_column(nullable=True)
    request_queue_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_rate: Mapped[float] = mapped_column(nullable=False, default=0.0)
    token_usage: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    health_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    model: Mapped[AIModel | None] = relationship(back_populates="health_checks")


class ModelConfiguration(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "ai_model_configurations"
    __table_args__ = (Index("ix_ai_model_configurations_model_status", "model_id", "status"),)

    model_id: Mapped[UUID] = mapped_column(ForeignKey("ai_models.id", ondelete="CASCADE"), nullable=False)
    provider_id: Mapped[UUID] = mapped_column(ForeignKey("ai_providers.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    settings: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    model: Mapped[AIModel] = relationship(back_populates="configurations")


class AISettings(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "ai_settings"
    __table_args__ = (UniqueConstraint("name", name="uq_ai_settings_name"),)

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    settings_type: Mapped[str] = mapped_column(String(64), nullable=False)
    settings: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
