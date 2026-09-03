import base64
import json
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from netopier_v1.database import DbConnection

SNAPSHOT_RETENTION_HOURS = 24


@dataclass(frozen=True)
class EventQuery:
    people: tuple[str, ...] = ()
    organizations: tuple[str, ...] = ()
    public_institutions: tuple[str, ...] = ()
    geography: str | None = None
    since: datetime | None = None
    until: datetime | None = None
    action_types: tuple[str, ...] = ()
    institutional_status: str | None = None
    min_independent_sources: int = 0
    novelty: str | None = None
    evidence_strength: str | None = None
    coverage: str | None = None
    min_articles: int = 0
    has_conflicts: bool | None = None
    limit: int = 50


def _encode_cursor(snapshot_id: UUID, position: int) -> str:
    payload = json.dumps(
        {"snapshot_id": str(snapshot_id), "position": position},
        separators=(",", ":"),
    ).encode()
    return base64.urlsafe_b64encode(payload).decode().rstrip("=")


def _decode_cursor(cursor: str) -> tuple[UUID, int]:
    padding = "=" * (-len(cursor) % 4)
    payload = json.loads(base64.urlsafe_b64decode(cursor + padding))
    position = int(payload["position"])
    if position < 0:
        raise ValueError("negative snapshot position")
    return UUID(payload["snapshot_id"]), position


class FeedProjector:
    """Owns stable public JSON projections over persisted story state."""

    def __init__(self, conn: DbConnection) -> None:
        self._conn = conn

    def health(self) -> dict:
        counts = self._conn.execute(
            """
            SELECT
              (SELECT count(*) FROM sources WHERE active) AS sources,
              (SELECT count(*) FROM articles) AS articles,
              (SELECT count(*) FROM stories) AS stories,
              (SELECT count(*) FROM article_embeddings) AS embeddings,
              (SELECT count(*) FROM event_candidates) AS event_candidates,
              (SELECT count(*) FROM event_clusters WHERE lifecycle_state = 'active') AS events,
              (SELECT count(*) FROM event_decisions WHERE status = 'suggested') AS event_suggestions
            """
        ).fetchone()
        checkpoint = self._conn.execute(
            "SELECT cursor, updated_at FROM pipeline_checkpoints WHERE stream = 'miniflux_entries'"
        ).fetchone()
        return {
            "status": "ok",
            "counts": counts,
            "reconciliation": checkpoint,
        }

    def snapshot(self, limit: int = 50, cursor: str | None = None) -> dict:
        limit = max(1, min(limit, 200))
        if cursor:
            snapshot_id, position = _decode_cursor(cursor)
            snapshot = self._conn.execute(
                """
                SELECT id, ranking_version, story_count
                FROM feed_snapshots
                WHERE id = %s AND expires_at > now()
                """,
                (snapshot_id,),
            ).fetchone()
            if snapshot is None:
                raise ValueError("feed snapshot is missing or expired")
        else:
            snapshot_id = self._create_snapshot()
            position = 0
            snapshot = self._conn.execute(
                "SELECT id, ranking_version, story_count FROM feed_snapshots WHERE id = %s",
                (snapshot_id,),
            ).fetchone()
            assert snapshot is not None
        stories = self._conn.execute(
            """
            SELECT
                s.id, s.title, s.first_published_at, s.last_published_at,
                s.article_count, s.source_family_count, i.score, i.score_factors,
                s.algorithm_version, snap.ranking_version
            FROM feed_snapshot_items i
            JOIN feed_snapshots snap ON snap.id = i.snapshot_id
            JOIN stories s ON s.id = i.story_id
            WHERE i.snapshot_id = %s AND i.position >= %s
            ORDER BY i.position
            LIMIT %s
            """,
            (snapshot_id, position, limit + 1),
        ).fetchall()
        has_more = len(stories) > limit
        stories = stories[:limit]
        items: list[dict] = []
        for story in stories:
            articles = self._conn.execute(
                """
                SELECT
                    a.id, a.title, a.canonical_url AS url, a.author,
                    a.published_at, a.discovered_at, a.text_scope,
                    src.id AS source_id, src.name AS source_name,
                    src.source_family, sm.similarity
                FROM story_memberships sm
                JOIN articles a ON a.id = sm.article_id
                JOIN sources src ON src.id = a.source_id
                WHERE sm.story_id = %s
                ORDER BY a.published_at DESC, a.id DESC
                """,
                (story["id"],),
            ).fetchall()
            items.append({**story, "articles": articles})
        next_cursor = None
        if has_more:
            next_cursor = _encode_cursor(snapshot_id, position + limit)
        return {
            "snapshot_id": snapshot_id,
            "story_count": snapshot["story_count"],
            "items": items,
            "next_cursor": next_cursor,
        }

    def _create_snapshot(self) -> UUID:
        self._conn.execute("DELETE FROM feed_snapshots WHERE expires_at <= now()")
        snapshot = self._conn.execute(
            """
            INSERT INTO feed_snapshots (ranking_version)
            VALUES ('source-family-v1')
            RETURNING id
            """
        ).fetchone()
        assert snapshot is not None
        snapshot_id = snapshot["id"]
        self._conn.execute(
            """
            INSERT INTO feed_snapshot_items (
                snapshot_id, position, story_id, score, score_factors,
                score_explanation_hash, last_published_at
            )
            SELECT
                %s,
                row_number() OVER (
                    ORDER BY score DESC, last_published_at DESC, id DESC
                )::integer - 1,
                id,
                score,
                score_factors,
                encode(digest(score_factors::text, 'sha256'), 'hex'),
                last_published_at
            FROM stories
            """,
            (snapshot_id,),
        )
        self._conn.execute(
            """
            UPDATE feed_snapshots
            SET story_count = (
                SELECT count(*) FROM feed_snapshot_items WHERE snapshot_id = %s
            )
            WHERE id = %s
            """,
            (snapshot_id, snapshot_id),
        )
        return snapshot_id

    def story(self, story_id: UUID) -> dict | None:
        story = self._conn.execute(
            """
            SELECT id, title, first_published_at, last_published_at, article_count,
                   source_family_count, score, score_factors, algorithm_version,
                   ranking_version, created_at, updated_at
            FROM stories WHERE id = %s
            """,
            (story_id,),
        ).fetchone()
        if story is None:
            return None
        articles = self._conn.execute(
            """
            SELECT a.id, a.title, a.canonical_url AS url, a.author, a.published_at,
                   a.discovered_at, a.text_scope, src.id AS source_id,
                   src.name AS source_name, src.source_family, sm.similarity,
                   sm.algorithm_version, sm.assigned_at
            FROM story_memberships sm
            JOIN articles a ON a.id = sm.article_id
            JOIN sources src ON src.id = a.source_id
            WHERE sm.story_id = %s
            ORDER BY a.published_at, a.id
            """,
            (story_id,),
        ).fetchall()
        revisions = self._conn.execute(
            """
            SELECT id, reason, algorithm_version, snapshot, created_at
            FROM story_revisions WHERE story_id = %s ORDER BY id
            """,
            (story_id,),
        ).fetchall()
        return {**story, "articles": articles, "revisions": revisions}

    def sources(self) -> list[dict]:
        return self._conn.execute(
            """
            SELECT s.id, s.name, s.site_url, s.feed_url, s.miniflux_feed_id, s.source_family,
                   s.language, s.country, s.text_scope, s.active,
                   count(a.id)::integer AS article_count,
                   max(a.discovered_at) AS latest_discovered_at
            FROM sources s
            LEFT JOIN articles a ON a.source_id = s.id
            GROUP BY s.id
            ORDER BY s.id
            """
        ).fetchall()

    def events(self, query: EventQuery) -> dict:
        """Return source-bounded event cards independent of publisher categories."""
        conditions: list[str] = ["ev.lifecycle_state = 'active'"]
        params: list[object] = []
        if query.people:
            conditions.append("ev.actors && %s::text[]")
            params.append(list(query.people))
        organization_filters = query.organizations + query.public_institutions
        if organization_filters:
            conditions.append("ev.organizations && %s::text[]")
            params.append(list(organization_filters))
        if query.geography:
            conditions.append("ev.location = %s")
            params.append(query.geography)
        if query.since:
            conditions.append("ev.occurred_end >= %s")
            params.append(query.since)
        if query.until:
            conditions.append("ev.occurred_start <= %s")
            params.append(query.until)
        if query.action_types:
            conditions.append("ev.action_types && %s::text[]")
            params.append(list(query.action_types))
        if query.institutional_status:
            conditions.append("ev.institutional_status = %s")
            params.append(query.institutional_status)
        if query.min_independent_sources:
            conditions.append("ev.independent_source_family_count >= %s")
            params.append(query.min_independent_sources)
        if query.novelty:
            conditions.append("ev.novelty = %s")
            params.append(query.novelty)
        if query.evidence_strength:
            conditions.append("ev.evidence_strength = %s")
            params.append(query.evidence_strength)
        if query.min_articles:
            conditions.append("ev.article_count >= %s")
            params.append(query.min_articles)
        if query.has_conflicts is not None:
            conditions.append(
                "jsonb_array_length(ev.conflicts) > 0"
                if query.has_conflicts
                else "ev.conflicts = '[]'::jsonb"
            )
        if query.coverage == "syndicated":
            conditions.append(
                "EXISTS (SELECT 1 FROM event_memberships em "
                "WHERE em.cluster_id = ev.id AND em.relation = 'syndicated_copy')"
            )
        elif query.coverage == "independent":
            conditions.append("ev.independent_source_family_count >= 2")
        elif query.coverage not in (None, "all"):
            raise ValueError("coverage must be all, independent, or syndicated")
        where = "WHERE " + " AND ".join(conditions) if conditions else ""
        limit = max(1, min(query.limit, 200))
        params.append(limit)
        rows = self._conn.execute(
            f"""
            SELECT ev.*,
                   count(*) OVER()::integer AS filtered_count,
                   EXISTS (
                       SELECT 1 FROM event_decisions d
                       WHERE d.compared_cluster_id = ev.id AND d.status = 'suggested'
                   ) AS has_suggestions,
                   (SELECT count(DISTINCT ar.article_id)::integer
                    FROM event_memberships em
                    JOIN event_candidates ec ON ec.id = em.candidate_id
                    JOIN article_revisions ar ON ar.id = ec.article_revision_id
                    WHERE em.cluster_id = ev.id AND em.relation = 'syndicated_copy'
                   ) AS syndicated_article_count
            FROM event_clusters ev
            {where}
            ORDER BY ev.occurred_end DESC, ev.confidence DESC, ev.id DESC
            LIMIT %s
            """,
            params,
        ).fetchall()
        items = [self._event_card(row) for row in rows]
        return {
            "contract_version": "events-v1",
            "filtered_count": rows[0]["filtered_count"] if rows else 0,
            "items": items,
            "filters": {
                "people": query.people,
                "organizations": query.organizations,
                "public_institutions": query.public_institutions,
                "geography": query.geography,
                "since": query.since,
                "until": query.until,
                "action_types": query.action_types,
                "institutional_status": query.institutional_status,
                "min_independent_sources": query.min_independent_sources,
                "novelty": query.novelty,
                "evidence_strength": query.evidence_strength,
                "coverage": query.coverage,
                "min_articles": query.min_articles,
                "has_conflicts": query.has_conflicts,
            },
        }

    def _event_card(self, event: dict) -> dict:
        evidence = self._conn.execute(
            """
            SELECT ec.id AS candidate_id, ec.source_excerpt AS exact_excerpt,
                   ec.excerpt_start, ec.excerpt_end, ec.action_type,
                   ec.institutional_status, ec.occurred_at,
                   a.id AS article_id, a.title AS article_title,
                   a.canonical_url AS url, a.published_at, a.discovered_at,
                   ar.revision_number, ar.content_hash, s.id AS source_id,
                   s.name AS source_name, s.source_family, em.relation,
                   d.id AS decision_id, d.score AS decision_score,
                   d.status AS decision_status, d.reason AS decision_reason,
                   d.features AS decision_features, d.threshold_version,
                   d.origin AS decision_origin, d.decided_at
            FROM event_memberships em
            JOIN event_candidates ec ON ec.id = em.candidate_id
            JOIN article_revisions ar ON ar.id = ec.article_revision_id
            JOIN articles a ON a.id = ar.article_id
            JOIN sources s ON s.id = a.source_id
            JOIN event_decisions d ON d.id = em.decision_id
            WHERE em.cluster_id = %s
            ORDER BY ec.occurred_at, ec.id
            """,
            (event["id"],),
        ).fetchall()
        revisions = self._conn.execute(
            """
            SELECT version, reason, algorithm_version, snapshot, created_at
            FROM event_cluster_revisions WHERE cluster_id = %s ORDER BY version
            """,
            (event["id"],),
        ).fetchall()
        suggestions = self._conn.execute(
            """
            SELECT id, candidate_id, assigned_cluster_id, relation, score, features,
                   threshold_version, reason, origin, status, decided_at
            FROM event_decisions
            WHERE compared_cluster_id = %s AND status = 'suggested'
            ORDER BY decided_at, id
            """,
            (event["id"],),
        ).fetchall()
        excluded = {"filtered_count", "centroid"}
        core = {key: value for key, value in event.items() if key not in excluded}
        return {
            **core,
            "timeline": [
                {
                    "occurred_at": item["occurred_at"],
                    "action_type": item["action_type"],
                    "institutional_status": item["institutional_status"],
                    "relation": item["relation"],
                    "candidate_id": item["candidate_id"],
                }
                for item in evidence
            ],
            "evidence": evidence,
            "revisions": revisions,
            "suggested_decisions": suggestions,
        }
