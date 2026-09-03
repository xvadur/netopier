from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class SourceSpec:
    id: str
    name: str
    site_url: str
    feed_url: str
    source_family: str
    resolved_feed_url: str | None = None
    language: str = "sk"
    country: str = "SK"
    text_scope: str = "rss"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MinifluxEntry:
    id: int
    feed_id: int
    feed_url: str
    title: str
    url: str
    author: str | None
    content_html: str
    source_hash: str | None
    published_at: datetime
    discovered_at: datetime
    changed_at: datetime | None
    raw: dict[str, Any]


@dataclass(frozen=True)
class EntryBatch:
    entries: tuple[MinifluxEntry, ...]
    next_cursor: int


@dataclass(frozen=True)
class IngestReceipt:
    article_ids: tuple[UUID, ...]
    created: int
    updated: int
    skipped: int


@dataclass(frozen=True)
class EmbeddingReceipt:
    article_ids: tuple[UUID, ...]
    model_version: str


@dataclass(frozen=True)
class StoryChanges:
    assigned: int
    stories_created: int
    stories_updated: int


@dataclass(frozen=True)
class EventChanges:
    candidates_created: int
    assigned: int
    events_created: int
    events_updated: int
    suggestions_created: int
