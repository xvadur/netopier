"""Add versioned event intelligence and immutable article revisions.

Revision ID: 0005_event_intelligence_core
Revises: 0004_feed_snapshots
"""

from alembic import op

revision = "0005_event_intelligence_core"
down_revision = "0004_feed_snapshots"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE article_revisions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            article_id uuid NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
            revision_number integer NOT NULL CHECK (revision_number > 0),
            title text NOT NULL,
            rss_content_text text NOT NULL,
            content_hash char(64) NOT NULL,
            raw_payload jsonb NOT NULL,
            observed_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (article_id, revision_number),
            UNIQUE (article_id, content_hash)
        )
        """
    )
    op.execute(
        """
        INSERT INTO article_revisions (
            article_id, revision_number, title, rss_content_text, content_hash,
            raw_payload, observed_at
        )
        SELECT id, 1, title, rss_content_text, content_hash, raw_payload, ingested_at
        FROM articles
        ON CONFLICT (article_id, content_hash) DO NOTHING
        """
    )
    op.execute(
        """
        CREATE TABLE event_candidates (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            article_revision_id uuid NOT NULL REFERENCES article_revisions(id) ON DELETE CASCADE,
            ordinal integer NOT NULL CHECK (ordinal >= 0),
            title text NOT NULL,
            summary text NOT NULL,
            actors text[] NOT NULL DEFAULT '{}',
            organizations text[] NOT NULL DEFAULT '{}',
            location text,
            occurred_at timestamptz NOT NULL,
            action_type text NOT NULL,
            action_object text,
            institutional_status text,
            source_excerpt text NOT NULL,
            excerpt_start integer NOT NULL CHECK (excerpt_start >= 0),
            excerpt_end integer NOT NULL CHECK (excerpt_end >= excerpt_start),
            extractor_version text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (article_revision_id, ordinal, extractor_version)
        )
        """
    )
    op.execute("CREATE INDEX event_candidates_time_idx ON event_candidates (occurred_at DESC, id)")
    op.execute("CREATE INDEX event_candidates_actors_idx ON event_candidates USING gin (actors)")
    op.execute(
        """
        CREATE TABLE event_clusters (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            version integer NOT NULL DEFAULT 1 CHECK (version > 0),
            title text NOT NULL,
            summary text NOT NULL,
            actors text[] NOT NULL DEFAULT '{}',
            organizations text[] NOT NULL DEFAULT '{}',
            location text,
            occurred_start timestamptz NOT NULL,
            occurred_end timestamptz NOT NULL,
            action_types text[] NOT NULL DEFAULT '{}',
            institutional_status text,
            centroid vector(384) NOT NULL,
            confidence double precision NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
            novelty text NOT NULL DEFAULT 'new',
            evidence_strength text NOT NULL DEFAULT 'single_source',
            article_count integer NOT NULL DEFAULT 1,
            source_family_count integer NOT NULL DEFAULT 1,
            independent_source_family_count integer NOT NULL DEFAULT 1,
            algorithm_version text NOT NULL,
            conflicts jsonb NOT NULL DEFAULT '[]'::jsonb,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX event_clusters_window_idx ON event_clusters (occurred_end DESC, id DESC)"
    )
    op.execute("CREATE INDEX event_clusters_actors_idx ON event_clusters USING gin (actors)")
    op.execute(
        "CREATE INDEX event_clusters_organizations_idx ON event_clusters USING gin (organizations)"
    )
    op.execute(
        "CREATE INDEX event_clusters_action_types_idx ON event_clusters USING gin (action_types)"
    )
    op.execute(
        """
        CREATE TABLE event_decisions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            candidate_id uuid NOT NULL REFERENCES event_candidates(id) ON DELETE CASCADE,
            compared_cluster_id uuid REFERENCES event_clusters(id),
            assigned_cluster_id uuid NOT NULL REFERENCES event_clusters(id),
            relation text NOT NULL CHECK (relation IN (
                'syndicated_copy', 'same_event', 'event_update', 'same_topic', 'unrelated'
            )),
            score double precision NOT NULL CHECK (score >= 0 AND score <= 1),
            features jsonb NOT NULL,
            threshold_version text NOT NULL,
            reason text NOT NULL,
            origin text NOT NULL CHECK (origin IN ('algorithm', 'human', 'migration')),
            status text NOT NULL CHECK (status IN ('accepted', 'rejected', 'suggested')),
            decided_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX event_decisions_candidate_idx ON event_decisions (candidate_id)")
    op.execute(
        """
        CREATE TABLE event_memberships (
            cluster_id uuid NOT NULL REFERENCES event_clusters(id) ON DELETE CASCADE,
            candidate_id uuid NOT NULL REFERENCES event_candidates(id) ON DELETE CASCADE,
            decision_id uuid NOT NULL REFERENCES event_decisions(id),
            relation text NOT NULL,
            added_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (cluster_id, candidate_id),
            UNIQUE (candidate_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE event_cluster_revisions (
            id bigserial PRIMARY KEY,
            cluster_id uuid NOT NULL REFERENCES event_clusters(id) ON DELETE CASCADE,
            version integer NOT NULL CHECK (version > 0),
            reason text NOT NULL,
            algorithm_version text NOT NULL,
            snapshot jsonb NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (cluster_id, version)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE event_lineage (
            id bigserial PRIMARY KEY,
            parent_cluster_id uuid NOT NULL REFERENCES event_clusters(id),
            child_cluster_id uuid NOT NULL REFERENCES event_clusters(id),
            operation text NOT NULL CHECK (operation IN ('merge', 'split', 'event_update')),
            reason text NOT NULL,
            origin text NOT NULL CHECK (origin IN ('algorithm', 'human')),
            created_at timestamptz NOT NULL DEFAULT now(),
            CHECK (parent_cluster_id <> child_cluster_id OR operation = 'event_update'),
            UNIQUE (parent_cluster_id, child_cluster_id, operation)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS event_lineage")
    op.execute("DROP TABLE IF EXISTS event_cluster_revisions")
    op.execute("DROP TABLE IF EXISTS event_memberships")
    op.execute("DROP TABLE IF EXISTS event_decisions")
    op.execute("DROP TABLE IF EXISTS event_clusters")
    op.execute("DROP TABLE IF EXISTS event_candidates")
    op.execute("DROP TABLE IF EXISTS article_revisions")
