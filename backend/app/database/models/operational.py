from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import AuditMixin, BaseModel, SoftDeleteMixin, TimestampMixin, UUIDMixin, VersionMixin


class AuditLog(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, VersionMixin):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_actor_created_at", "actor_user_id", "created_at"),
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
    )

    actor_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    organization_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
    entity_type: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    before_state: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    after_state: Mapped[dict[str, object] | None] = mapped_column(JSON, nullable=True)
    context: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    request_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    request_method: Mapped[str | None] = mapped_column(String(16), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="success")


class SystemSetting(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "system_settings"
    __table_args__ = (UniqueConstraint("setting_key", name="uq_system_settings_setting_key"),)

    setting_key: Mapped[str] = mapped_column(String(128), nullable=False)
    setting_value: Mapped[str] = mapped_column(Text, nullable=False)
    data_type: Mapped[str] = mapped_column(String(32), nullable=False, default="string")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_secret: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scope: Mapped[str] = mapped_column(String(64), nullable=False, default="global")
    setting_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class Notification(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_status", "user_id", "status"),
        Index("ix_notifications_created_at", "created_at"),
    )

    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notification_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    user = relationship("User", back_populates="notifications")


class FeatureFlag(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "feature_flags"
    __table_args__ = (
        UniqueConstraint("flag_key", name="uq_feature_flags_flag_key"),
        Index("ix_feature_flags_enabled_rollout", "enabled", "rollout_percentage"),
    )

    flag_key: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rollout_percentage: Mapped[int] = mapped_column(nullable=False, default=0)
    conditions: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    scope: Mapped[str] = mapped_column(String(64), nullable=False, default="global")
    owner_team: Mapped[str | None] = mapped_column(String(255), nullable=True)
