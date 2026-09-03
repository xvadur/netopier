import json
from urllib.parse import quote
from urllib.request import urlopen

BASE_URL = "http://127.0.0.1:8090"


def get(path: str):
    with urlopen(f"{BASE_URL}{path}", timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"GET {path} returned {response.status}")
        return json.load(response)


def main() -> None:
    health = get("/health")
    if health["status"] != "ok" or health["counts"]["articles"] < 1:
        raise SystemExit(f"unhealthy archive: {health}")
    sources = get("/sources")
    if len(sources) < 2 or any(source["miniflux_feed_id"] is None for source in sources):
        raise SystemExit("source projection is incomplete")

    cursor = None
    story_ids: list[str] = []
    first_story = None
    for _ in range(100):
        suffix = "?limit=7"
        if cursor:
            suffix += f"&cursor={quote(cursor)}"
        page = get(f"/feed{suffix}")
        if first_story is None and page["items"]:
            first_story = page["items"][0]
        story_ids.extend(item["id"] for item in page["items"])
        cursor = page["next_cursor"]
        if not cursor:
            break
    else:
        raise SystemExit("pagination did not terminate")
    if len(story_ids) != len(set(story_ids)):
        raise SystemExit("feed pagination returned duplicate stories")
    if len(story_ids) != health["counts"]["stories"]:
        raise SystemExit("feed traversal did not return every story")
    if first_story is None:
        raise SystemExit("feed has no story")
    story = get(f"/stories/{first_story['id']}")
    if not story["articles"] or not story["revisions"]:
        raise SystemExit("story provenance is incomplete")
    events = get("/events?limit=2")
    if events["contract_version"] != "events-v1" or not events["items"]:
        raise SystemExit("event projection is incomplete")
    event = events["items"][0]
    if not event["evidence"] or not event["revisions"] or not event["timeline"]:
        raise SystemExit("event evidence or decision history is incomplete")
    independent = get("/events?min_independent_sources=2&coverage=independent&limit=2")
    if any(item["independent_source_family_count"] < 2 for item in independent["items"]):
        raise SystemExit("event independence filter is incorrect")

    print(
        json.dumps(
            {
                "status": "passed",
                "health": health,
                "sources": len(sources),
                "stories_traversed": len(story_ids),
                "unique_stories": len(set(story_ids)),
                "story_detail_checked": first_story["id"],
                "event_detail_checked": event["id"],
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
