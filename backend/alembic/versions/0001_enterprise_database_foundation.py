"""enterprise database foundation

Revision ID: 0001_enterprise_database_foundation
Revises:
Create Date: 2026-07-14 00:00:00.000000
"""

from __future__ import annotations

from alembic import op

import app.database.models  # noqa: F401
from app.database.base import Base


# revision identifiers, used by Alembic.
revision = "0001_enterprise_database_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the full enterprise persistence schema."""

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Drop the full enterprise persistence schema."""

    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
