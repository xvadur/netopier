import json
import math
from datetime import timedelta
from difflib import SequenceMatcher
from uuid import UUID

from psycopg.types.json import Jsonb

from netopier_v1.config import Settings
from netopier_v1.database import DbConnection
from netopier_v1.domain import EventChanges, StoryChanges
from netopier_v1.events import (
    EXTRACTOR_VERSION,
    ArticleRevision,
    DecisionStatus,
    EventCandidateExtractor,
    EventFeatures,
    EventRelation,
    RelationshipDecider,
    RelationshipDecision,
)
from netopier_v1.text import normalize_title

ALGORITHM_FAMILY = "temporal-centroid-v1"
RANKING_VERSION = "source-family-v1"


def explainable_score(article_count: int, source_family_count: int) -> tuple[float, dict]:
    family_score = source_family_count * 10.0
    coverage_score = round(math.log2(article_count + 1) * 2.0, 6)
    factors = {
        "source_family_count": source_family_count,
        "source_family_score": family_score,
        "article_count": article_count,
        "coverage_score": coverage_score,
        "ranking_version": RANKING_VERSION,
    }
    return round(family_score + coverage_score, 6), factors


class StoryEngine:
    """Owns exact candidate search, assignment locking and story revisions."""

    def __init__(self, conn: DbConnection, settings: Settings) -> None:
        self._conn = conn
        self._settings = settings

    @property
    def algorithm_version(self) -> str:
        return f"{ALGORITHM_FAMILY}:threshold={self._settings.story_similarity_threshold:.2f}"

    def assign(self, article_ids: tuple[UUID, ...] | None = None, limit: int = 500) -> StoryChanges:
        self._conn.execute("SELECT pg_advisory_xact_lock(741852963)")
        params: list[object] = [self._settings.embedding_model]
        where = "sm.article_id IS NULL AND e.model_version = %s"
        if article_ids is not None:
            where += " AND a.id = ANY(%s)"
            params.append(list(article_ids))
        params.append(limit)
        rows = self._conn.execute(
            f"""
            SELECT a.id, a.title, a.published_at, e.embedding::text AS embedding
            FROM articles a
            JOIN article_embeddings e ON e.article_id = a.id
            LEFT JOIN story_memberships sm ON sm.article_id = a.id
            WHERE {where}
            ORDER BY a.published_at, a.id
            LIMIT %s
            """,
            params,
        ).fetchall()

        assigned = created = updated = 0
        window = timedelta(hours=self._settings.story_window_hours)
        for article in rows:
            candidate = self._conn.execute(
                """
                SELECT id, 1 - (centroid <=> %s::vector) AS similarity
                FROM stories
                WHERE last_published_at >= %s
                  AND first_published_at <= %s
                ORDER BY centroid <=> %s::vector, id
                LIMIT 1
                """,
                (
                    article["embedding"],
                    article["published_at"] - window,
                    article["published_at"] + window,
                    article["embedding"],
                ),
            ).fetchone()
            below_threshold = (
                candidate is not None
                and candidate["similarity"] < self._settings.story_similarity_threshold
            )
            if candidate is None or below_threshold:
                score, factors = explainable_score(1, 1)
                story = self._conn.execute(
                    """
                    INSERT INTO stories (
                        representative_article_id, title, centroid, first_published_at,
                        last_published_at, score, score_factors, algorithm_version,
                        ranking_version
                    ) VALUES (%s, %s, %s::vector, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        article["id"],
                        article["title"],
                        article["embedding"],
                        article["published_at"],
                        article["published_at"],
                        score,
                        Jsonb(factors),
                        self.algorithm_version,
                        RANKING_VERSION,
                    ),
                ).fetchone()
                assert story is not None
                story_id = story["id"]
                similarity = 1.0
                created += 1
            else:
                story_id = candidate["id"]
                similarity = float(candidate["similarity"])
                updated += 1

            self._conn.execute(
                """
                INSERT INTO story_memberships (
                    story_id, article_id, similarity, algorithm_version
                ) VALUES (%s, %s, %s, %s)
                ON CONFLICT (article_id) DO NOTHING
                """,
                (story_id, article["id"], similarity, self.algorithm_version),
            )
            self._refresh_story(story_id)
            assigned += 1
        return StoryChanges(assigned=assigned, stories_created=created, stories_updated=updated)

    def atomize(self, article_ids: tuple[UUID, ...] | None = None, limit: int = 500) -> int:
        """Persist deterministic candidates from immutable article revisions."""
        params: list[object] = [EXTRACTOR_VERSION]
        article_filter = ""
        if article_ids is not None:
            article_filter = "AND a.id = ANY(%s)"
            params.append(list(article_ids))
        params.append(limit)
        rows = self._conn.execute(
            f"""
            SELECT ar.id, ar.article_id, ar.title, ar.rss_content_text, ar.content_hash,
                   a.published_at, a.canonical_url, a.source_id, s.source_family
            FROM article_revisions ar
            JOIN articles a ON a.id = ar.article_id
            JOIN sources s ON s.id = a.source_id
            LEFT JOIN event_candidates ec
              ON ec.article_revision_id = ar.id AND ec.extractor_version = %s
            WHERE ec.id IS NULL {article_filter}
            ORDER BY a.published_at, ar.revision_number, ar.id
            LIMIT %s
            """,
            params,
        ).fetchall()
        extractor = EventCandidateExtractor()
        created = 0
        for row in rows:
            revision = ArticleRevision(
                id=row["id"],
                article_id=row["article_id"],
                title=row["title"],
                text=row["rss_content_text"],
                published_at=row["published_at"],
                source_id=row["source_id"],
                source_family=row["source_family"],
                url=row["canonical_url"],
                content_hash=row["content_hash"],
            )
            for candidate in extractor.atomize(revision):
                result = self._conn.execute(
                    """
                    INSERT INTO event_candidates (
                        article_revision_id, ordinal, title, summary, actors, organizations,
                        location, occurred_at, action_type, action_object, institutional_status,
                        source_excerpt, excerpt_start, excerpt_end, extractor_version
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (article_revision_id, ordinal, extractor_version) DO NOTHING
                    RETURNING id
                    """,
                    (
                        row["id"], candidate.ordinal, candidate.title, candidate.summary,
                        list(candidate.actors), list(candidate.organizations), candidate.location,
                        candidate.occurred_at, candidate.action_type, candidate.action_object,
                        candidate.institutional_status, candidate.source_excerpt,
                        candidate.excerpt_start, candidate.excerpt_end, candidate.extractor_version,
                    ),
                ).fetchone()
                created += int(result is not None)
        return created

    def assign_events(
        self, candidate_ids: tuple[UUID, ...] | None = None, limit: int = 500
    ) -> EventChanges:
        """Assign candidates through a bounded, explainable, conservative comparison."""
        self._conn.execute("SELECT pg_advisory_xact_lock(741852965)")
        params: list[object] = [self._settings.embedding_model]
        candidate_filter = ""
        if candidate_ids is not None:
            candidate_filter = "AND ec.id = ANY(%s)"
            params.append(list(candidate_ids))
        params.append(limit)
        rows = self._conn.execute(
            f"""
            SELECT ec.*, ar.content_hash, ar.rss_content_text, ar.article_id,
                   a.canonical_url, a.normalized_title, a.published_at,
                   s.source_family, emb.embedding::text AS embedding
            FROM event_candidates ec
            JOIN article_revisions ar ON ar.id = ec.article_revision_id
            JOIN articles a ON a.id = ar.article_id
            JOIN sources s ON s.id = a.source_id
            JOIN article_embeddings emb
              ON emb.article_id = a.id AND emb.model_version = %s
            LEFT JOIN event_memberships em ON em.candidate_id = ec.id
            WHERE em.candidate_id IS NULL {candidate_filter}
            ORDER BY ec.occurred_at, ec.id
            LIMIT %s
            """,
            params,
        ).fetchall()
        decider = RelationshipDecider()
        created = updated = suggestions = assigned = 0
        window = timedelta(hours=self._settings.story_window_hours)
        for candidate in rows:
            comparisons = self._candidate_clusters(candidate, window, decider)
            accepted = [item for item in comparisons if item[1].should_merge]
            suggested = [item for item in comparisons if item[1].status is DecisionStatus.SUGGESTED]
            if accepted:
                compared_cluster, decision = max(accepted, key=lambda item: item[1].score)
                cluster_id = compared_cluster["id"]
                updated += 1
            else:
                cluster_id = self._create_event(candidate)
                created += 1
                if suggested:
                    compared_cluster, decision = max(suggested, key=lambda item: item[1].score)
                    suggestions += 1
                elif comparisons:
                    compared_cluster, decision = max(comparisons, key=lambda item: item[1].score)
                else:
                    compared_cluster = None
                    decision = decider.decide(EventFeatures())
            decision_row = self._conn.execute(
                """
                INSERT INTO event_decisions (
                    candidate_id, compared_cluster_id, assigned_cluster_id, relation, score,
                    features, threshold_version, reason, origin, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'algorithm', %s)
                RETURNING id
                """,
                (
                    candidate["id"], compared_cluster["id"] if compared_cluster else None,
                    cluster_id, decision.relation.value, decision.score, Jsonb(decision.features),
                    decision.threshold_version, decision.reason, decision.status.value,
                ),
            ).fetchone()
            assert decision_row is not None
            membership_relation = (
                decision.relation.value if accepted else EventRelation.UNRELATED.value
            )
            self._conn.execute(
                """
                INSERT INTO event_memberships (cluster_id, candidate_id, decision_id, relation)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (candidate_id) DO NOTHING
                """,
                (cluster_id, candidate["id"], decision_row["id"], membership_relation),
            )
            if decision.relation is EventRelation.EVENT_UPDATE and accepted:
                self._conn.execute(
                    """
                    INSERT INTO event_lineage (
                        parent_cluster_id, child_cluster_id, operation, reason, origin
                    ) VALUES (%s, %s, 'event_update', %s, 'algorithm')
                    ON CONFLICT DO NOTHING
                    """,
                    (cluster_id, cluster_id, decision.reason),
                )
            self._refresh_event(cluster_id, decision.relation.value)
            assigned += 1
        return EventChanges(0, assigned, created, updated, suggestions)

    def _candidate_clusters(
        self, candidate: dict, window: timedelta, decider: RelationshipDecider
    ) -> list[tuple[dict, RelationshipDecision]]:
        rows = self._conn.execute(
            """
            SELECT ev.*, 1 - (ev.centroid <=> %s::vector) AS embedding_similarity,
                   peer.content_hash AS peer_content_hash,
                   peer.rss_content_text AS peer_text,
                   peer_article.canonical_url AS peer_url,
                   peer_article.normalized_title AS peer_title
            FROM event_clusters ev
            JOIN LATERAL (
                SELECT ec.article_revision_id
                FROM event_memberships em
                JOIN event_candidates ec ON ec.id = em.candidate_id
                WHERE em.cluster_id = ev.id
                ORDER BY ec.occurred_at DESC, ec.id DESC LIMIT 1
            ) member ON true
            JOIN article_revisions peer ON peer.id = member.article_revision_id
            JOIN articles peer_article ON peer_article.id = peer.article_id
            WHERE ev.occurred_end >= %s AND ev.occurred_start <= %s
              AND NOT EXISTS (
                SELECT 1
                FROM event_memberships same_membership
                JOIN event_candidates same_candidate
                  ON same_candidate.id = same_membership.candidate_id
                JOIN article_revisions same_revision
                  ON same_revision.id = same_candidate.article_revision_id
                WHERE same_membership.cluster_id = ev.id
                  AND same_revision.article_id = %s
              )
              AND (
                ev.actors && %s::text[] OR ev.organizations && %s::text[] OR
                ev.location = %s OR ev.action_types @> ARRAY[%s]::text[] OR
                1 - (ev.centroid <=> %s::vector) >= 0.60
              )
            ORDER BY ev.centroid <=> %s::vector, ev.occurred_end DESC
            LIMIT 20
            """,
            (
                candidate["embedding"], candidate["occurred_at"] - window,
                candidate["occurred_at"] + window, candidate["article_id"], candidate["actors"],
                candidate["organizations"], candidate["location"], candidate["action_type"],
                candidate["embedding"], candidate["embedding"],
            ),
        ).fetchall()
        output = []
        for event in rows:
            candidate_entities = set(candidate["actors"]) | set(candidate["organizations"])
            event_entities = set(event["actors"]) | set(event["organizations"])
            union = candidate_entities | event_entities
            entity_overlap = len(candidate_entities & event_entities) / len(union) if union else 0.0
            hours = abs((candidate["occurred_at"] - event["occurred_end"]).total_seconds()) / 3600
            lexical = self._lexical_similarity(candidate["summary"], event["summary"])
            features = EventFeatures(
                canonical_url_match=candidate["canonical_url"] == event["peer_url"],
                content_hash_match=candidate["content_hash"] == event["peer_content_hash"],
                normalized_title_match=candidate["normalized_title"] == event["peer_title"],
                title_similarity=SequenceMatcher(
                    None, candidate["normalized_title"], event["peer_title"]
                ).ratio(),
                text_similarity=SequenceMatcher(
                    None, candidate["rss_content_text"][:4000], event["peer_text"][:4000]
                ).ratio(),
                entity_overlap=entity_overlap,
                location_match=bool(
                    candidate["location"] and candidate["location"] == event["location"]
                ),
                time_proximity=max(0.0, 1.0 - hours / self._settings.story_window_hours),
                lexical_similarity=lexical,
                embedding_similarity=float(event["embedding_similarity"]),
                action_type_match=candidate["action_type"] in event["action_types"],
                update_signal=candidate["occurred_at"] > event["occurred_end"],
                status_changed=bool(
                    candidate["institutional_status"]
                    and event["institutional_status"]
                    and candidate["institutional_status"] != event["institutional_status"]
                ),
            )
            output.append((event, decider.decide(features)))
        return output

    @staticmethod
    def _lexical_similarity(left: str, right: str) -> float:
        left_tokens = set(normalize_title(left).split())
        right_tokens = set(normalize_title(right).split())
        union = left_tokens | right_tokens
        return len(left_tokens & right_tokens) / len(union) if union else 0.0

    def _create_event(self, candidate: dict) -> UUID:
        row = self._conn.execute(
            """
            INSERT INTO event_clusters (
                title, summary, actors, organizations, location, occurred_start, occurred_end,
                action_types, institutional_status, centroid, confidence, algorithm_version
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, ARRAY[%s], %s, %s::vector, 1, %s)
            RETURNING id
            """,
            (
                candidate["title"], candidate["summary"], candidate["actors"],
                candidate["organizations"], candidate["location"], candidate["occurred_at"],
                candidate["occurred_at"], candidate["action_type"],
                candidate["institutional_status"], candidate["embedding"], self.algorithm_version,
            ),
        ).fetchone()
        assert row is not None
        return row["id"]

    def _refresh_event(self, cluster_id: UUID, reason: str) -> None:
        aggregate = self._conn.execute(
            """
            SELECT min(ec.occurred_at) AS first_at, max(ec.occurred_at) AS last_at,
                   count(DISTINCT ar.article_id)::integer AS article_count,
                   count(DISTINCT s.source_family)::integer AS source_family_count,
                   count(DISTINCT s.source_family) FILTER (
                       WHERE em.relation <> 'syndicated_copy'
                   )::integer AS independent_count,
                   array_agg(DISTINCT actor) FILTER (WHERE actor IS NOT NULL) AS actors,
                   array_agg(DISTINCT org) FILTER (WHERE org IS NOT NULL) AS organizations,
                   array_agg(DISTINCT ec.action_type) AS action_types,
                   avg(emb.embedding)::text AS centroid
            FROM event_memberships em
            JOIN event_candidates ec ON ec.id = em.candidate_id
            JOIN article_revisions ar ON ar.id = ec.article_revision_id
            JOIN articles a ON a.id = ar.article_id
            JOIN sources s ON s.id = a.source_id
            JOIN article_embeddings emb
              ON emb.article_id = a.id AND emb.model_version = %s
            LEFT JOIN LATERAL unnest(ec.actors) actor ON true
            LEFT JOIN LATERAL unnest(ec.organizations) org ON true
            WHERE em.cluster_id = %s
            """,
            (self._settings.embedding_model, cluster_id),
        ).fetchone()
        assert aggregate is not None
        latest = self._conn.execute(
            """
            SELECT ec.title, ec.summary, ec.location, ec.institutional_status
            FROM event_memberships em JOIN event_candidates ec ON ec.id = em.candidate_id
            WHERE em.cluster_id = %s ORDER BY ec.occurred_at DESC, ec.id DESC LIMIT 1
            """,
            (cluster_id,),
        ).fetchone()
        assert latest is not None
        independent = aggregate["independent_count"]
        strength = "corroborated" if independent >= 2 else "single_source"
        novelty = "update" if reason == EventRelation.EVENT_UPDATE.value else "new"
        row = self._conn.execute(
            """
            UPDATE event_clusters SET version = version + 1, title = %s, summary = %s,
                actors = %s, organizations = %s, location = coalesce(%s, location),
                occurred_start = %s, occurred_end = %s, action_types = %s,
                institutional_status = coalesce(%s, institutional_status), centroid = %s::vector,
                article_count = %s, source_family_count = %s,
                independent_source_family_count = %s, novelty = %s,
                evidence_strength = %s, updated_at = now()
            WHERE id = %s RETURNING version, confidence, algorithm_version
            """,
            (
                latest["title"], latest["summary"], aggregate["actors"] or [],
                aggregate["organizations"] or [], latest["location"], aggregate["first_at"],
                aggregate["last_at"], aggregate["action_types"], latest["institutional_status"],
                aggregate["centroid"], aggregate["article_count"], aggregate["source_family_count"],
                independent, novelty, strength, cluster_id,
            ),
        ).fetchone()
        assert row is not None
        snapshot = {
            "title": latest["title"], "summary": latest["summary"],
            "occurred_start": aggregate["first_at"].isoformat(),
            "occurred_end": aggregate["last_at"].isoformat(),
            "article_count": aggregate["article_count"],
            "source_family_count": aggregate["source_family_count"],
            "independent_source_family_count": independent,
            "novelty": novelty, "evidence_strength": strength,
        }
        self._conn.execute(
            """
            INSERT INTO event_cluster_revisions (
                cluster_id, version, reason, algorithm_version, snapshot
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (cluster_id, version) DO NOTHING
            """,
            (cluster_id, row["version"], reason, row["algorithm_version"], Jsonb(snapshot)),
        )

    def merge_events(self, target_id: UUID, source_id: UUID, reason: str) -> None:
        """Human correction: preserve the source event and move its evidence to target."""
        if target_id == source_id:
            raise ValueError("merge requires two different events")
        self._conn.execute("SELECT pg_advisory_xact_lock(741852965)")
        candidates = self._conn.execute(
            """
            SELECT candidate_id FROM event_memberships
            WHERE cluster_id = %s ORDER BY candidate_id
            """,
            (source_id,),
        ).fetchall()
        if not candidates:
            raise ValueError("source event has no active evidence")
        for candidate in candidates:
            decision = self._conn.execute(
                """
                INSERT INTO event_decisions (
                    candidate_id, compared_cluster_id, assigned_cluster_id, relation, score,
                    features, threshold_version, reason, origin, status
                ) VALUES (%s, %s, %s, 'same_event', 1, '{}'::jsonb,
                          'human-correction-v1', %s, 'human', 'accepted')
                RETURNING id
                """,
                (candidate["candidate_id"], target_id, target_id, reason),
            ).fetchone()
            assert decision is not None
            self._conn.execute(
                """
                UPDATE event_memberships
                SET cluster_id = %s, decision_id = %s, relation = 'same_event', added_at = now()
                WHERE cluster_id = %s AND candidate_id = %s
                """,
                (target_id, decision["id"], source_id, candidate["candidate_id"]),
            )
        self._conn.execute(
            """
            UPDATE event_clusters SET lifecycle_state = 'superseded', updated_at = now()
            WHERE id = %s
            """,
            (source_id,),
        )
        self._conn.execute(
            """
            INSERT INTO event_lineage (
                parent_cluster_id, child_cluster_id, operation, reason, origin
            ) VALUES (%s, %s, 'merge', %s, 'human')
            ON CONFLICT DO NOTHING
            """,
            (source_id, target_id, reason),
        )
        self._refresh_event(target_id, "merge")

    def split_event(
        self, source_id: UUID, candidate_ids: tuple[UUID, ...], reason: str
    ) -> UUID:
        """Human correction: move selected evidence to a new event and record lineage."""
        if not candidate_ids:
            raise ValueError("split requires at least one candidate")
        self._conn.execute("SELECT pg_advisory_xact_lock(741852965)")
        source_count = self._conn.execute(
            "SELECT count(*)::integer AS count FROM event_memberships WHERE cluster_id = %s",
            (source_id,),
        ).fetchone()
        if source_count is None or source_count["count"] <= len(set(candidate_ids)):
            raise ValueError("split must leave at least one candidate in the source event")
        seed = self._conn.execute(
            """
            SELECT ec.*, ar.article_id, emb.embedding::text AS embedding
            FROM event_memberships em
            JOIN event_candidates ec ON ec.id = em.candidate_id
            JOIN article_revisions ar ON ar.id = ec.article_revision_id
            JOIN article_embeddings emb
              ON emb.article_id = ar.article_id AND emb.model_version = %s
            WHERE em.cluster_id = %s AND ec.id = ANY(%s)
            ORDER BY ec.occurred_at, ec.id LIMIT 1
            """,
            (self._settings.embedding_model, source_id, list(candidate_ids)),
        ).fetchone()
        if seed is None:
            raise ValueError("split candidates are not members of the source event")
        new_id = self._create_event(seed)
        for candidate_id in candidate_ids:
            decision = self._conn.execute(
                """
                INSERT INTO event_decisions (
                    candidate_id, compared_cluster_id, assigned_cluster_id, relation, score,
                    features, threshold_version, reason, origin, status
                ) VALUES (%s, %s, %s, 'unrelated', 1, '{}'::jsonb,
                          'human-correction-v1', %s, 'human', 'accepted')
                RETURNING id
                """,
                (candidate_id, source_id, new_id, reason),
            ).fetchone()
            assert decision is not None
            moved = self._conn.execute(
                """
                UPDATE event_memberships
                SET cluster_id = %s, decision_id = %s, relation = 'unrelated', added_at = now()
                WHERE cluster_id = %s AND candidate_id = %s RETURNING candidate_id
                """,
                (new_id, decision["id"], source_id, candidate_id),
            ).fetchone()
            if moved is None:
                raise ValueError("split candidate is not a member of the source event")
        self._conn.execute(
            """
            INSERT INTO event_lineage (
                parent_cluster_id, child_cluster_id, operation, reason, origin
            ) VALUES (%s, %s, 'split', %s, 'human')
            """,
            (source_id, new_id, reason),
        )
        self._refresh_event(source_id, "split_source")
        self._refresh_event(new_id, "split")
        return new_id

    def _refresh_story(self, story_id: UUID) -> None:
        aggregate = self._conn.execute(
            """
            SELECT
                avg(e.embedding)::text AS centroid,
                min(a.published_at) AS first_published_at,
                max(a.published_at) AS last_published_at,
                count(*)::integer AS article_count,
                count(DISTINCT s.source_family)::integer AS source_family_count
            FROM story_memberships sm
            JOIN articles a ON a.id = sm.article_id
            JOIN sources s ON s.id = a.source_id
            JOIN article_embeddings e
              ON e.article_id = a.id AND e.model_version = %s
            WHERE sm.story_id = %s
            """,
            (self._settings.embedding_model, story_id),
        ).fetchone()
        assert aggregate is not None
        representative = self._conn.execute(
            """
            SELECT a.id, a.title
            FROM story_memberships sm
            JOIN articles a ON a.id = sm.article_id
            WHERE sm.story_id = %s
            ORDER BY a.published_at DESC, a.id DESC
            LIMIT 1
            """,
            (story_id,),
        ).fetchone()
        assert representative is not None
        score, factors = explainable_score(
            aggregate["article_count"], aggregate["source_family_count"]
        )
        self._conn.execute(
            """
            UPDATE stories SET
                representative_article_id = %s,
                title = %s,
                centroid = %s::vector,
                first_published_at = %s,
                last_published_at = %s,
                article_count = %s,
                source_family_count = %s,
                score = %s,
                score_factors = %s,
                algorithm_version = %s,
                ranking_version = %s,
                updated_at = now()
            WHERE id = %s
            """,
            (
                representative["id"],
                representative["title"],
                aggregate["centroid"],
                aggregate["first_published_at"],
                aggregate["last_published_at"],
                aggregate["article_count"],
                aggregate["source_family_count"],
                score,
                Jsonb(factors),
                self.algorithm_version,
                RANKING_VERSION,
                story_id,
            ),
        )
        snapshot = {
            "title": representative["title"],
            "article_count": aggregate["article_count"],
            "source_family_count": aggregate["source_family_count"],
            "score": score,
            "score_factors": factors,
        }
        self._conn.execute(
            """
            INSERT INTO story_revisions (story_id, reason, algorithm_version, snapshot)
            VALUES (%s, 'assignment', %s, %s)
            """,
            (story_id, self.algorithm_version, Jsonb(json.loads(json.dumps(snapshot)))),
        )
