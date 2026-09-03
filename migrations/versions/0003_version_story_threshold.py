"""Record the threshold used by pre-benchmark story assignments.

Revision ID: 0003_version_story_threshold
Revises: 0002_miniflux_feed_identity
"""

from alembic import op

revision = "0003_version_story_threshold"
down_revision = "0002_miniflux_feed_identity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ("stories", "story_memberships", "story_revisions"):
        op.execute(
            f"""
            UPDATE {table}
            SET algorithm_version = 'temporal-centroid-v1:threshold=0.79'
            WHERE algorithm_version = 'temporal-centroid-v1'
            """
        )


def downgrade() -> None:
    for table in ("stories", "story_memberships", "story_revisions"):
        op.execute(
            f"""
            UPDATE {table}
            SET algorithm_version = 'temporal-centroid-v1'
            WHERE algorithm_version = 'temporal-centroid-v1:threshold=0.79'
            """
        )
