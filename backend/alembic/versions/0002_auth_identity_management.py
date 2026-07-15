"""authentication identity management

Revision ID: 0002_auth_identity_management
Revises: 0001_enterprise_database_foundation
Create Date: 2026-07-14 00:00:00.000001
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "0002_auth_identity_management"
down_revision = "0001_enterprise_database_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=False, server_default=""))
    op.add_column("users", sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("password_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("password_history", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")))
    op.add_column("users", sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("verification_token_hash", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("verification_token_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("password_reset_token_hash", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("password_reset_token_expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("users", sa.Column("failed_login_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("last_login_ip", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("last_login_user_agent", sa.String(length=512), nullable=True))
    op.add_column("users", sa.Column("authentication_metadata", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")))
    op.create_index("ix_users_email_status", "users", ["email", "status"], unique=False)
    op.create_index("ix_users_username_status", "users", ["username", "status"], unique=False)
    op.create_index("ix_users_locked_until", "users", ["locked_until"], unique=False)

    op.add_column("sessions", sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("sessions", sa.Column("device_id", sa.String(length=128), nullable=True))
    op.add_column("sessions", sa.Column("device_name", sa.String(length=255), nullable=True))
    op.add_column("sessions", sa.Column("device_fingerprint", sa.String(length=255), nullable=True))
    op.add_column("sessions", sa.Column("geo_location", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")))
    op.create_index("ix_sessions_user_last_activity", "sessions", ["user_id", "last_activity_at"], unique=False)

    op.add_column("refresh_tokens", sa.Column("jti", sa.String(length=64), nullable=False, server_default=""))
    op.add_column("refresh_tokens", sa.Column("family_id", sa.String(length=64), nullable=False, server_default=""))
    op.add_column("refresh_tokens", sa.Column("rotated_from_jti", sa.String(length=64), nullable=True))
    op.add_column("refresh_tokens", sa.Column("revoked_reason", sa.String(length=255), nullable=True))
    op.create_unique_constraint("uq_refresh_tokens_jti", "refresh_tokens", ["jti"])
    op.create_index("ix_refresh_tokens_family_status", "refresh_tokens", ["family_id", "status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_family_status", table_name="refresh_tokens")
    op.drop_constraint("uq_refresh_tokens_jti", "refresh_tokens", type_="unique")
    op.drop_column("refresh_tokens", "revoked_reason")
    op.drop_column("refresh_tokens", "rotated_from_jti")
    op.drop_column("refresh_tokens", "family_id")
    op.drop_column("refresh_tokens", "jti")

    op.drop_index("ix_sessions_user_last_activity", table_name="sessions")
    op.drop_column("sessions", "geo_location")
    op.drop_column("sessions", "device_fingerprint")
    op.drop_column("sessions", "device_name")
    op.drop_column("sessions", "device_id")
    op.drop_column("sessions", "last_activity_at")

    op.drop_index("ix_users_locked_until", table_name="users")
    op.drop_index("ix_users_username_status", table_name="users")
    op.drop_index("ix_users_email_status", table_name="users")
    op.drop_column("users", "authentication_metadata")
    op.drop_column("users", "last_login_user_agent")
    op.drop_column("users", "last_login_ip")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_at")
    op.drop_column("users", "failed_login_count")
    op.drop_column("users", "password_reset_token_expires_at")
    op.drop_column("users", "password_reset_token_hash")
    op.drop_column("users", "verification_token_expires_at")
    op.drop_column("users", "verification_token_hash")
    op.drop_column("users", "email_verified_at")
    op.drop_column("users", "password_history")
    op.drop_column("users", "password_expires_at")
    op.drop_column("users", "password_changed_at")
    op.drop_column("users", "password_hash")
