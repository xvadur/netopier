from datetime import UTC, datetime

from netopier.events import (
    ArticleRevision,
    DecisionStatus,
    EventCandidateExtractor,
    EventFeatures,
    EventRelation,
    RelationshipDecider,
)


def revision(text: str) -> ArticleRevision:
    return ArticleRevision(
        id="revision-1",
        article_id="article-1",
        title="Vláda rokovala a súd rozhodol",
        text=text,
        published_at=datetime(2026, 9, 2, 12, tzinfo=UTC),
        source_id="source-a",
        source_family="family-a",
        url="https://example.test/evidence",
        content_hash="a" * 64,
    )


def test_atomize_preserves_exact_evidence_for_multiple_events() -> None:
    text = (
        "Vláda v Bratislave schválila pomoc farmárom. "
        "Najvyšší súd neskôr oslobodil obžalovaného podnikateľa."
    )

    candidates = EventCandidateExtractor().atomize(revision(text))

    assert len(candidates) == 2
    assert [candidate.source_excerpt for candidate in candidates] == [
        "Vláda v Bratislave schválila pomoc farmárom.",
        "Najvyšší súd neskôr oslobodil obžalovaného podnikateľa.",
    ]
    assert text[candidates[1].excerpt_start : candidates[1].excerpt_end] == (
        candidates[1].source_excerpt
    )
    assert candidates[0].action_type == "approval"
    assert candidates[1].institutional_status == "acquitted"


def test_relationship_decisions_cover_five_classes_conservatively() -> None:
    decider = RelationshipDecider()

    exact_copy = decider.decide(
        EventFeatures(
            canonical_url_match=True,
            content_hash_match=True,
            title_similarity=1.0,
            text_similarity=1.0,
        )
    )
    same_event = decider.decide(
        EventFeatures(
            entity_overlap=0.9,
            location_match=True,
            time_proximity=0.95,
            action_type_match=True,
            lexical_similarity=0.78,
            embedding_similarity=0.91,
        )
    )
    update = decider.decide(
        EventFeatures(
            entity_overlap=0.9,
            location_match=True,
            time_proximity=0.7,
            action_type_match=True,
            lexical_similarity=0.63,
            embedding_similarity=0.86,
            update_signal=True,
            status_changed=True,
        )
    )
    same_topic = decider.decide(
        EventFeatures(
            entity_overlap=0.7,
            time_proximity=0.3,
            lexical_similarity=0.45,
            embedding_similarity=0.72,
        )
    )
    unrelated = decider.decide(
        EventFeatures(lexical_similarity=0.05, embedding_similarity=0.12)
    )

    assert exact_copy.relation is EventRelation.SYNDICATED_COPY
    assert same_event.relation is EventRelation.SAME_EVENT
    assert update.relation is EventRelation.EVENT_UPDATE
    assert same_topic.relation is EventRelation.SAME_TOPIC
    assert unrelated.relation is EventRelation.UNRELATED
    assert all(
        result.status is DecisionStatus.ACCEPTED
        for result in (exact_copy, same_event, update, same_topic, unrelated)
    )


def test_gray_zone_is_suggested_and_does_not_merge() -> None:
    result = RelationshipDecider().decide(
        EventFeatures(
            entity_overlap=0.65,
            time_proximity=0.8,
            action_type_match=True,
            lexical_similarity=0.55,
            embedding_similarity=0.79,
        )
    )

    assert result.relation is EventRelation.SAME_EVENT
    assert result.status is DecisionStatus.SUGGESTED
    assert result.should_merge is False
    assert result.threshold_version == "event-hybrid-v2"


def test_embedding_threshold_still_requires_an_event_anchor() -> None:
    result = RelationshipDecider().decide(
        EventFeatures(
            time_proximity=0.9,
            lexical_similarity=0.6,
            embedding_similarity=0.9,
        )
    )

    assert result.should_merge is False
