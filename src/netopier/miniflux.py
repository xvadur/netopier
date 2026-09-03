from datetime import datetime

import httpx

from netopier.config import Settings
from netopier.domain import EntryBatch, MinifluxEntry


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class MinifluxGateway:
    """The only seam where Miniflux HTTP details enter Netopier."""

    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=settings.miniflux_base_url,
            auth=(settings.miniflux_admin_username, settings.miniflux_admin_password),
            timeout=30,
        )
        self._limit = settings.reconciliation_batch_size

    def reconcile(self, checkpoint: int) -> EntryBatch:
        response = self._client.get(
            "/v1/entries",
            params={
                "after_entry_id": checkpoint,
                "order": "id",
                "direction": "asc",
                "limit": self._limit,
            },
        )
        response.raise_for_status()
        entries: list[MinifluxEntry] = []
        for raw in response.json().get("entries", []):
            published_at = _parse_datetime(raw.get("published_at"))
            discovered_at = _parse_datetime(raw.get("created_at"))
            if published_at is None or discovered_at is None:
                continue
            feed = raw.get("feed") or {}
            entries.append(
                MinifluxEntry(
                    id=int(raw["id"]),
                    feed_id=int(feed["id"]),
                    feed_url=feed.get("feed_url", ""),
                    title=raw.get("title", "").strip(),
                    url=raw.get("url", "").strip(),
                    author=(raw.get("author") or "").strip() or None,
                    content_html=raw.get("content") or "",
                    source_hash=raw.get("hash"),
                    published_at=published_at,
                    discovered_at=discovered_at,
                    changed_at=_parse_datetime(raw.get("changed_at")),
                    raw=raw,
                )
            )
        next_cursor = max((entry.id for entry in entries), default=checkpoint)
        return EntryBatch(entries=tuple(entries), next_cursor=next_cursor)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()
