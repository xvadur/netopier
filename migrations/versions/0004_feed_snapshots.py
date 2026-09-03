"""Persist immutable feed pagination snapshots.

Revision ID: 0004_feed_snapshots
Revises: 0003_version_story_threshold
"""

from alembic import op

revision = "0004_feed_snapshots"
down_revision = "0003_version_story_threshold"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE feed_snapshots (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            ranking_version text NOT NULL,
            story_count integer NOT NULL DEFAULT 0,
            created_at timestamptz NOT NULL DEFAULT now(),
            expires_at timestamptz NOT NULL DEFAULT now() + interval '24 hours'
        )
        """
    )
    op.execute("CREATE INDEX feed_snapshots_expiry_idx ON feed_snapshots (expires_at)")
    op.execute(
        """
        CREATE TABLE feed_snapshot_items (
            snapshot_id uuid NOT NULL REFERENCES feed_snapshots(id) ON DELETE CASCADE,
            position integer NOT NULL CHECK (position >= 0),
            story_id uuid NOT NULL REFERENCES stories(id),
            score double precision NOT NULL,
            score_factors jsonb NOT NULL,
            score_explanation_hash text NOT NULL,
            last_published_at timestamptz NOT NULL,
            PRIMARY KEY (snapshot_id, position),
            UNIQUE (snapshot_id, story_id)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS feed_snapshot_items")
    op.execute("DROP TABLE IF EXISTS feed_snapshots")
