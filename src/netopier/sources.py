from pathlib import Path
from typing import Any

import httpx
import yaml
from psycopg.types.json import Jsonb

from netopier.config import Settings
from netopier.database import DbConnection
from netopier.domain import SourceSpec


def load_source_manifest(path: str | Path) -> list[SourceSpec]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("unsupported source manifest schema")
    return [SourceSpec(**item) for item in payload.get("sources", [])]


class SourceRegistry:
    def __init__(self, conn: DbConnection) -> None:
        self._conn = conn

    def import_specs(self, specs: list[SourceSpec]) -> dict[str, int]:
        created = 0
        updated = 0
        for spec in specs:
            metadata = dict(spec.metadata)
            if spec.resolved_feed_url:
                metadata["resolved_feed_url"] = spec.resolved_feed_url
            existing = self._conn.execute(
                "SELECT 1 FROM sources WHERE id = %s", (spec.id,)
            ).fetchone()
            self._conn.execute(
                """
                INSERT INTO sources (
                    id, name, site_url, feed_url, source_family, language, country,
                    text_scope, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    site_url = EXCLUDED.site_url,
                    feed_url = EXCLUDED.feed_url,
                    source_family = EXCLUDED.source_family,
                    language = EXCLUDED.language,
                    country = EXCLUDED.country,
                    text_scope = EXCLUDED.text_scope,
                    metadata = EXCLUDED.metadata,
                    updated_at = now()
                """,
                (
                    spec.id,
                    spec.name,
                    spec.site_url,
                    spec.feed_url,
                    spec.source_family,
                    spec.language,
                    spec.country,
                    spec.text_scope,
                    Jsonb(metadata),
                ),
            )
            if existing:
                updated += 1
            else:
                created += 1
        return {"created": created, "updated": updated, "total": len(specs)}

    def bind_miniflux(self, bootstrap_result: dict[str, Any]) -> int:
        bound = 0
        bindings = bootstrap_result.get("created", []) + bootstrap_result.get("retained", [])
        for binding in bindings:
            result = self._conn.execute(
                """
                UPDATE sources
                SET miniflux_feed_id = %s, updated_at = now()
                WHERE id = %s
                """,
                (binding["feed_id"], binding["source_id"]),
            )
            bound += result.rowcount
        return bound


def bootstrap_miniflux(
    specs: list[SourceSpec], settings: Settings, client: httpx.Client | None = None
) -> dict[str, Any]:
    own_client = client is None
    if client is None:
        client = httpx.Client(
            base_url=settings.miniflux_base_url,
            auth=(settings.miniflux_admin_username, settings.miniflux_admin_password),
            timeout=30,
        )
    try:
        response = client.get("/v1/feeds")
        response.raise_for_status()
        existing = {feed["feed_url"]: feed["id"] for feed in response.json()}
        created: list[dict[str, Any]] = []
        retained: list[dict[str, Any]] = []
        failed: list[dict[str, Any]] = []
        for spec in specs:
            known_urls = [spec.feed_url]
            if spec.resolved_feed_url:
                known_urls.append(spec.resolved_feed_url)
            matched_url = next((url for url in known_urls if url in existing), None)
            if matched_url:
                retained.append({"source_id": spec.id, "feed_id": existing[matched_url]})
                continue
            try:
                result = client.post("/v1/feeds", json={"feed_url": spec.feed_url})
                result.raise_for_status()
                created.append({"source_id": spec.id, "feed_id": result.json()["feed_id"]})
            except httpx.HTTPError as exc:
                failed.append({"source_id": spec.id, "error": str(exc)})
        return {"created": created, "retained": retained, "failed": failed}
    finally:
        if own_client:
            client.close()
