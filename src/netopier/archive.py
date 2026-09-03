from uuid import UUID

from psycopg.types.json import Jsonb

from netopier.database import DbConnection
from netopier.domain import EntryBatch, IngestReceipt
from netopier.text import canonicalize_url, content_hash, html_to_text, normalize_title


class ArticleArchive:
    """Owns normalization, provenance and idempotent article persistence."""

    def __init__(self, conn: DbConnection) -> None:
        self._conn = conn

    def ingest(self, batch: EntryBatch) -> IngestReceipt:
        article_ids: list[UUID] = []
        created = updated = skipped = 0
        for entry in batch.entries:
            source = self._conn.execute(
                """
                SELECT id, text_scope
                FROM sources
                WHERE active = true
                  AND (miniflux_feed_id = %s OR feed_url = %s)
                ORDER BY (miniflux_feed_id = %s) DESC
                LIMIT 1
                """,
                (entry.feed_id, entry.feed_url, entry.feed_id),
            ).fetchone()
            if source is None or not entry.title or not entry.url:
                skipped += 1
                continue

            canonical_url = canonicalize_url(entry.url)
            normalized_title = normalize_title(entry.title)
            rss_text = html_to_text(entry.content_html)
            digest = content_hash(entry.title, rss_text)
            existing = self._conn.execute(
                """
                SELECT id, content_hash
                FROM articles
                WHERE miniflux_entry_id = %s OR canonical_url = %s
                LIMIT 1
                """,
                (entry.id, canonical_url),
            ).fetchone()

            if existing is None:
                row = self._conn.execute(
                    """
                    INSERT INTO articles (
                        source_id, miniflux_entry_id, canonical_url, original_url, title,
                        normalized_title, author, rss_content_text, text_scope,
                        miniflux_hash, content_hash, published_at, discovered_at,
                        changed_at, raw_payload
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    RETURNING id
                    """,
                    (
                        source["id"],
                        entry.id,
                        canonical_url,
                        entry.url,
                        entry.title,
                        normalized_title,
                        entry.author,
                        rss_text,
                        source["text_scope"],
                        entry.source_hash,
                        digest,
                        entry.published_at,
                        entry.discovered_at,
                        entry.changed_at,
                        Jsonb(entry.raw),
                    ),
                ).fetchone()
                assert row is not None
                self._append_revision(row["id"], entry.title, rss_text, digest, entry.raw)
                article_ids.append(row["id"])
                created += 1
                continue

            if existing["content_hash"] == digest:
                skipped += 1
                continue

            row = self._conn.execute(
                """
                UPDATE articles SET
                    source_id = %s,
                    miniflux_entry_id = %s,
                    canonical_url = %s,
                    original_url = %s,
                    title = %s,
                    normalized_title = %s,
                    author = %s,
                    rss_content_text = %s,
                    text_scope = %s,
                    miniflux_hash = %s,
                    content_hash = %s,
                    published_at = %s,
                    discovered_at = %s,
                    changed_at = %s,
                    raw_payload = %s,
                    updated_at = now()
                WHERE id = %s
                RETURNING id
                """,
                (
                    source["id"],
                    entry.id,
                    canonical_url,
                    entry.url,
                    entry.title,
                    normalized_title,
                    entry.author,
                    rss_text,
                    source["text_scope"],
                    entry.source_hash,
                    digest,
                    entry.published_at,
                    entry.discovered_at,
                    entry.changed_at,
                    Jsonb(entry.raw),
                    existing["id"],
                ),
            ).fetchone()
            assert row is not None
            self._append_revision(row["id"], entry.title, rss_text, digest, entry.raw)
            self._conn.execute("DELETE FROM article_embeddings WHERE article_id = %s", (row["id"],))
            article_ids.append(row["id"])
            updated += 1

        return IngestReceipt(
            article_ids=tuple(article_ids), created=created, updated=updated, skipped=skipped
        )

    def _append_revision(
        self,
        article_id: UUID,
        title: str,
        rss_text: str,
        digest: str,
        raw_payload: dict,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO article_revisions (
                article_id, revision_number, title, rss_content_text, content_hash, raw_payload
            )
            SELECT %s, coalesce(max(revision_number), 0) + 1, %s, %s, %s, %s
            FROM article_revisions
            WHERE article_id = %s
            ON CONFLICT (article_id, content_hash) DO NOTHING
            """,
            (article_id, title, rss_text, digest, Jsonb(raw_payload), article_id),
        )
