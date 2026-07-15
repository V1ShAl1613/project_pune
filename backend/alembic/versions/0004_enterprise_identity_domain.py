"""enterprise identity domain

Revision ID: 0004_enterprise_identity_domain
Revises: 0003_enterprise_rbac_authorization
Create Date: 2026-07-14 00:00:00.000000
"""

from __future__ import annotations

from alembic import op

import app.database.models  # noqa: F401
from app.database.base import Base


# revision identifiers, used by Alembic.
revision = "0004_enterprise_identity_domain"
down_revision = "0003_enterprise_rbac_authorization"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the Phase 5 tenancy and identity domain tables."""

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Drop the Phase 5 tenancy and identity domain tables."""

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
