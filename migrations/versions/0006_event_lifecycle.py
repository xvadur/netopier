"""Add explicit event lifecycle state for merge and split correction.

Revision ID: 0006_event_lifecycle
Revises: 0005_event_intelligence_core
"""

from alembic import op

revision = "0006_event_lifecycle"
down_revision = "0005_event_intelligence_core"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE event_clusters
        ADD COLUMN lifecycle_state text NOT NULL DEFAULT 'active'
        CHECK (lifecycle_state IN ('active', 'superseded', 'split_source'))
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE event_clusters DROP COLUMN lifecycle_state")
