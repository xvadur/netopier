import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

from netopier_v1.text import normalize_title

EXTRACTOR_VERSION = "rule-atomizer-v1"
THRESHOLD_VERSION = "event-hybrid-v2"


class EventRelation(StrEnum):
    SYNDICATED_COPY = "syndicated_copy"
    SAME_EVENT = "same_event"
    EVENT_UPDATE = "event_update"
    SAME_TOPIC = "same_topic"
    UNRELATED = "unrelated"


class DecisionStatus(StrEnum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUGGESTED = "suggested"


@dataclass(frozen=True)
class ArticleRevision:
    id: object
    article_id: object
    title: str
    text: str
    published_at: datetime
    source_id: str
    source_family: str
    url: str
    content_hash: str


@dataclass(frozen=True)
class EventCandidate:
    ordinal: int
    title: str
    summary: str
    actors: tuple[str, ...]
    organizations: tuple[str, ...]
    location: str | None
    occurred_at: datetime
    action_type: str
    action_object: str | None
    institutional_status: str | None
    source_excerpt: str
    excerpt_start: int
    excerpt_end: int
    extractor_version: str = EXTRACTOR_VERSION


@dataclass(frozen=True)
class EventFeatures:
    canonical_url_match: bool = False
    content_hash_match: bool = False
    normalized_title_match: bool = False
    title_similarity: float = 0.0
    text_similarity: float = 0.0
    entity_overlap: float = 0.0
    location_match: bool = False
    time_proximity: float = 0.0
    lexical_similarity: float = 0.0
    embedding_similarity: float = 0.0
    action_type_match: bool = False
    update_signal: bool = False
    status_changed: bool = False

    def as_dict(self) -> dict[str, float | bool]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True)
class RelationshipDecision:
    relation: EventRelation
    status: DecisionStatus
    score: float
    reason: str
    threshold_version: str = THRESHOLD_VERSION
    features: dict[str, float | bool] = field(default_factory=dict)

    @property
    def should_merge(self) -> bool:
        return self.status is DecisionStatus.ACCEPTED and self.relation in {
            EventRelation.SYNDICATED_COPY,
            EventRelation.SAME_EVENT,
            EventRelation.EVENT_UPDATE,
        }


ACTION_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("approval", ("schválil", "schválila", "schválilo", "prijala", "prijalo")),
    ("acquittal", ("oslobodil", "oslobodila", "oslobodený", "oslobodeného")),
    ("charge", ("obvinil", "obvinila", "obžaloval", "obžalovala")),
    ("investigation", ("vyšetruje", "preveruje", "začala vyšetrovať")),
    ("statement", ("povedal", "povedala", "uviedol", "vyhlásil", "tvrdí")),
    ("attack", ("zaútočil", "útok", "napadol")),
    ("appointment", ("vymenoval", "vymenovala", "zvolil", "zvolila")),
    ("dismissal", ("odvolal", "odvolala", "stiahla", "zbavil")),
)
STATUS_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("acquitted", ("oslobodil", "oslobodila", "oslobodený", "oslobodeného")),
    ("charged", ("obvinený", "obžalovaný", "obžalovaného")),
    ("under_investigation", ("vyšetruje", "preveruje")),
    ("approved", ("schválil", "schválila", "schválilo", "prijala", "prijalo")),
)
LOCATION_TERMS = (
    "Bratislava",
    "Slovensko",
    "Brusel",
    "Malta",
    "Naháč",
    "Trnava",
    "Lipsko",
    "Ukrajina",
    "Rusko",
)


def _first_rule(text: str, rules: tuple[tuple[str, tuple[str, ...]], ...]) -> str | None:
    folded = normalize_title(text)
    for label, terms in rules:
        if any(normalize_title(term) in folded for term in terms):
            return label
    return None


def _named_phrases(text: str) -> tuple[str, ...]:
    phrases = re.findall(
        r"(?<![.!?])\b(?:[A-ZÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽ][\wÁ-ž-]+)(?:\s+[A-ZÁÄČĎÉÍĹĽŇÓÔŔŠŤÚÝŽ][\wÁ-ž-]+){0,2}",
        text,
    )
    return tuple(dict.fromkeys(phrase.strip() for phrase in phrases if len(phrase) > 2))


class EventCandidateExtractor:
    """Deterministically turns a preserved article revision into source-linked events."""

    def atomize(self, article_revision: ArticleRevision) -> tuple[EventCandidate, ...]:
        text = article_revision.text.strip()
        spans = [match.span() for match in re.finditer(r"[^.!?]+(?:[.!?]+|$)", text)]
        candidates: list[EventCandidate] = []
        for start, end in spans:
            while start < end and text[start].isspace():
                start += 1
            excerpt = text[start:end].strip()
            if not excerpt:
                continue
            action_type = _first_rule(excerpt, ACTION_RULES)
            if action_type is None:
                continue
            names = _named_phrases(excerpt)
            organizations = tuple(
                name
                for name in names
                if any(token in name for token in ("súd", "Súd", "Vláda", "Ministerstvo", "EÚ"))
            )
            actors = tuple(name for name in names if name not in organizations)
            location = next((place for place in LOCATION_TERMS if place in excerpt), None)
            candidates.append(
                EventCandidate(
                    ordinal=len(candidates),
                    title=excerpt[:240],
                    summary=excerpt,
                    actors=actors,
                    organizations=organizations,
                    location=location,
                    occurred_at=article_revision.published_at,
                    action_type=action_type,
                    action_object=None,
                    institutional_status=_first_rule(excerpt, STATUS_RULES),
                    source_excerpt=excerpt,
                    excerpt_start=start,
                    excerpt_end=start + len(excerpt),
                )
            )
        if candidates:
            return tuple(candidates)
        fallback = article_revision.title.strip() or text[:240]
        excerpt = text or fallback
        return (
            EventCandidate(
                ordinal=0,
                title=fallback[:240],
                summary=excerpt[:1000],
                actors=_named_phrases(fallback),
                organizations=(),
                location=next((place for place in LOCATION_TERMS if place in excerpt), None),
                occurred_at=article_revision.published_at,
                action_type="reported_development",
                action_object=None,
                institutional_status=_first_rule(excerpt, STATUS_RULES),
                source_excerpt=excerpt,
                excerpt_start=0,
                excerpt_end=len(excerpt),
            ),
        )


class RelationshipDecider:
    """Conservative, versioned five-class decision interface."""

    def decide(self, features: EventFeatures) -> RelationshipDecision:
        raw = features.as_dict()
        if features.canonical_url_match or features.content_hash_match or (
            features.normalized_title_match
            and features.title_similarity >= 0.97
            and features.text_similarity >= 0.94
        ):
            return RelationshipDecision(
                EventRelation.SYNDICATED_COPY,
                DecisionStatus.ACCEPTED,
                1.0,
                "canonical URL, content hash, or near-exact title and text match",
                features=raw,
            )

        score = round(
            0.30 * features.embedding_similarity
            + 0.20 * features.lexical_similarity
            + 0.20 * features.entity_overlap
            + 0.10 * features.time_proximity
            + 0.10 * float(features.action_type_match)
            + 0.05 * float(features.location_match)
            + 0.05 * features.title_similarity,
            6,
        )
        if (
            features.update_signal
            and features.status_changed
            and features.entity_overlap >= 0.6
            and features.embedding_similarity >= 0.6
            and score >= 0.55
        ):
            return RelationshipDecision(
                EventRelation.EVENT_UPDATE,
                DecisionStatus.ACCEPTED,
                score,
                "shared event anchors with an explicit later status change",
                features=raw,
            )
        high_confidence_event = score >= 0.82 or (
            score >= 0.45
            and features.embedding_similarity >= 0.86
            and features.time_proximity >= 0.5
            and (
                features.entity_overlap >= 0.2
                or features.location_match
                or features.action_type_match
            )
        )
        if high_confidence_event:
            return RelationshipDecision(
                EventRelation.SAME_EVENT,
                DecisionStatus.ACCEPTED,
                score,
                "high-confidence agreement across event anchors",
                features=raw,
            )
        if score >= 0.62:
            return RelationshipDecision(
                EventRelation.SAME_EVENT,
                DecisionStatus.SUGGESTED,
                score,
                "gray-zone event similarity requires human review",
                features=raw,
            )
        topic_score = max(features.embedding_similarity, features.lexical_similarity)
        if topic_score >= 0.42 or features.entity_overlap >= 0.5:
            return RelationshipDecision(
                EventRelation.SAME_TOPIC,
                DecisionStatus.ACCEPTED,
                round(topic_score, 6),
                "topic or entity overlap without enough event anchors",
                features=raw,
            )
        return RelationshipDecision(
            EventRelation.UNRELATED,
            DecisionStatus.ACCEPTED,
            round(max(topic_score, features.entity_overlap), 6),
            "no material event or topic overlap",
            features=raw,
        )
