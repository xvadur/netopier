"""Bind source identity to the stable Miniflux feed ID.

Revision ID: 0002_miniflux_feed_identity
Revises: 0001_initial
Create Date: 2026-09-03
"""

from alembic import op

revision = "0002_miniflux_feed_identity"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE sources ADD COLUMN miniflux_feed_id bigint UNIQUE")


def downgrade() -> None:
    op.execute("ALTER TABLE sources DROP COLUMN miniflux_feed_id")

