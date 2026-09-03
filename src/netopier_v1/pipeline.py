import time
from typing import Any

import structlog
from psycopg.types.json import Jsonb

from netopier_v1.archive import ArticleArchive
from netopier_v1.config import Settings
from netopier_v1.database import connection
from netopier_v1.embeddings import EmbeddingIndex
from netopier_v1.miniflux import MinifluxGateway
from netopier_v1.stories import StoryEngine

log = structlog.get_logger()
RECONCILIATION_LOCK_ID = 741852964


def reconcile_once(settings: Settings, gateway: MinifluxGateway | None = None) -> dict[str, Any]:
    own_gateway = gateway is None
    gateway = gateway or MinifluxGateway(settings)
    with connection() as conn:
        run = conn.execute(
            """
            INSERT INTO processing_runs (kind, status)
            VALUES ('reconcile', 'running')
            RETURNING id
            """
        ).fetchone()
        assert run is not None
    try:
        with connection() as conn:
            conn.execute("SELECT pg_advisory_xact_lock(%s)", (RECONCILIATION_LOCK_ID,))
            checkpoint_row = conn.execute(
                """
                INSERT INTO pipeline_checkpoints (stream, cursor)
                VALUES ('miniflux_entries', 0)
                ON CONFLICT (stream) DO UPDATE SET stream = EXCLUDED.stream
                RETURNING cursor
                """
            ).fetchone()
            assert checkpoint_row is not None
            checkpoint = checkpoint_row["cursor"]
            batch = gateway.reconcile(checkpoint)
            receipt = ArticleArchive(conn).ingest(batch)
            embedding = EmbeddingIndex(conn, settings).embed(receipt.article_ids)
            engine = StoryEngine(conn, settings)
            stories = engine.assign(embedding.article_ids)
            candidates_created = engine.atomize(receipt.article_ids)
            events = engine.assign_events(limit=settings.reconciliation_batch_size)
            conn.execute(
                """
                UPDATE pipeline_checkpoints
                SET cursor = %s, updated_at = now()
                WHERE stream = 'miniflux_entries'
                """,
                (batch.next_cursor,),
            )
            counts = {
                "received": len(batch.entries),
                "created": receipt.created,
                "updated": receipt.updated,
                "skipped": receipt.skipped,
                "embedded": len(embedding.article_ids),
                "assigned": stories.assigned,
                "stories_created": stories.stories_created,
                "stories_updated": stories.stories_updated,
                "event_candidates_created": candidates_created,
                "events_assigned": events.assigned,
                "events_created": events.events_created,
                "events_updated": events.events_updated,
                "event_suggestions_created": events.suggestions_created,
                "checkpoint": batch.next_cursor,
            }
            conn.execute(
                """
                UPDATE processing_runs
                SET status = 'completed', finished_at = now(), counts = %s
                WHERE id = %s
                """,
                (Jsonb(counts), run["id"]),
            )
            log.info("reconcile_completed", run_id=str(run["id"]), **counts)
            return counts
    except Exception as exc:
        with connection() as conn:
            conn.execute(
                """
                UPDATE processing_runs
                SET status = 'failed', finished_at = now(), error = %s
                WHERE id = %s
                """,
                (str(exc), run["id"]),
            )
        raise
    finally:
        if own_gateway:
            gateway.close()


def process_pending(settings: Settings) -> dict[str, int]:
    with connection() as conn:
        embedding = EmbeddingIndex(conn, settings).embed_pending()
        engine = StoryEngine(conn, settings)
        stories = engine.assign(embedding.article_ids)
        candidates_created = engine.atomize(limit=settings.reconciliation_batch_size)
        events = engine.assign_events(limit=settings.reconciliation_batch_size)
        return {
            "embedded": len(embedding.article_ids),
            "assigned": stories.assigned,
            "stories_created": stories.stories_created,
            "stories_updated": stories.stories_updated,
            "event_candidates_created": candidates_created,
            "events_assigned": events.assigned,
            "events_created": events.events_created,
            "events_updated": events.events_updated,
            "event_suggestions_created": events.suggestions_created,
        }


def run_forever(settings: Settings) -> None:
    gateway = MinifluxGateway(settings)
    try:
        while True:
            try:
                reconcile_once(settings, gateway)
            except Exception:
                log.exception("reconcile_failed")
            time.sleep(settings.worker_interval_seconds)
    finally:
        gateway.close()
