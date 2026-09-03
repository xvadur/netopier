import json
import os
from pathlib import Path
from urllib.request import urlopen

from netopier_v1.api import app

BASE_URL = os.getenv("NETOPIER_API_BASE_URL", "http://127.0.0.1:8090")
OUTPUT = Path("contracts")


def get(path: str):
    with urlopen(f"{BASE_URL}{path}", timeout=10) as response:
        return json.load(response)


def write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT / "openapi.json", app.openapi())
    health = get("/health")
    sources = get("/sources")
    feed = get("/feed?limit=2")
    if not feed["items"]:
        raise SystemExit("cannot export story example from an empty feed")
    story = get(f"/stories/{feed['items'][0]['id']}")
    events = get("/events?limit=2")
    write_json(OUTPUT / "health.example.json", health)
    write_json(OUTPUT / "sources.example.json", sources)
    write_json(OUTPUT / "feed.example.json", feed)
    write_json(OUTPUT / "story.example.json", story)
    write_json(OUTPUT / "events.example.json", events)
    print(json.dumps({"status": "written", "directory": str(OUTPUT), "files": 6}))


if __name__ == "__main__":
    main()
