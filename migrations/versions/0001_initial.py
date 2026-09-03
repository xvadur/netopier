"""Create the clean Netopier v2 schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-03
"""

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute(
        """
        CREATE TABLE sources (
            id text PRIMARY KEY,
            name text NOT NULL,
            site_url text NOT NULL,
            feed_url text NOT NULL UNIQUE,
            source_family text NOT NULL,
            language text NOT NULL DEFAULT 'sk',
            country text NOT NULL DEFAULT 'SK',
            text_scope text NOT NULL DEFAULT 'rss',
            active boolean NOT NULL DEFAULT true,
            metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE pipeline_checkpoints (
            stream text PRIMARY KEY,
            cursor bigint NOT NULL DEFAULT 0,
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE processing_runs (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            kind text NOT NULL,
            status text NOT NULL,
            started_at timestamptz NOT NULL DEFAULT now(),
            finished_at timestamptz,
            counts jsonb NOT NULL DEFAULT '{}'::jsonb,
            error text
        )
        """
    )
    op.execute(
        """
        CREATE TABLE articles (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            source_id text NOT NULL REFERENCES sources(id),
            miniflux_entry_id bigint NOT NULL UNIQUE,
            canonical_url text NOT NULL UNIQUE,
            original_url text NOT NULL,
            title text NOT NULL,
            normalized_title text NOT NULL,
            author text,
            rss_content_text text NOT NULL DEFAULT '',
            text_scope text NOT NULL DEFAULT 'rss',
            miniflux_hash text,
            content_hash char(64) NOT NULL,
            published_at timestamptz NOT NULL,
            discovered_at timestamptz NOT NULL,
            changed_at timestamptz,
            ingested_at timestamptz NOT NULL DEFAULT now(),
            raw_payload jsonb NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute("CREATE INDEX articles_published_idx ON articles (published_at DESC, id)")
    op.execute("CREATE INDEX articles_title_trgm_idx ON articles USING gin (normalized_title gin_trgm_ops)")
    op.execute(
        """
        CREATE TABLE article_embeddings (
            article_id uuid NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
            model_version text NOT NULL,
            dimensions integer NOT NULL CHECK (dimensions = 384),
            embedding vector(384) NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (article_id, model_version)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE stories (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            representative_article_id uuid REFERENCES articles(id),
            title text NOT NULL,
            centroid vector(384) NOT NULL,
            first_published_at timestamptz NOT NULL,
            last_published_at timestamptz NOT NULL,
            article_count integer NOT NULL DEFAULT 1,
            source_family_count integer NOT NULL DEFAULT 1,
            score double precision NOT NULL DEFAULT 0,
            score_factors jsonb NOT NULL DEFAULT '{}'::jsonb,
            algorithm_version text NOT NULL,
            ranking_version text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX stories_feed_idx ON stories (score DESC, last_published_at DESC, id DESC)"
    )
    op.execute(
        """
        CREATE TABLE story_memberships (
            story_id uuid NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
            article_id uuid NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
            similarity double precision NOT NULL,
            algorithm_version text NOT NULL,
            assigned_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (story_id, article_id),
            UNIQUE (article_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE story_revisions (
            id bigserial PRIMARY KEY,
            story_id uuid NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
            reason text NOT NULL,
            algorithm_version text NOT NULL,
            snapshot jsonb NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS story_revisions")
    op.execute("DROP TABLE IF EXISTS story_memberships")
    op.execute("DROP TABLE IF EXISTS stories")
    op.execute("DROP TABLE IF EXISTS article_embeddings")
    op.execute("DROP TABLE IF EXISTS articles")
    op.execute("DROP TABLE IF EXISTS processing_runs")
    op.execute("DROP TABLE IF EXISTS pipeline_checkpoints")
    op.execute("DROP TABLE IF EXISTS sources")

