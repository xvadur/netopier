import httpx

from netopier_v1.config import Settings
from netopier_v1.domain import SourceSpec
from netopier_v1.sources import bootstrap_miniflux


def test_bootstrap_is_idempotent() -> None:
    posts: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET":
            return httpx.Response(
                200,
                json=[{"id": 7, "feed_url": "https://existing.sk/rss"}],
            )
        posts.append(request.read().decode())
        return httpx.Response(201, json={"feed_id": 8})

    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="http://miniflux.test"
    )
    specs = [
        SourceSpec(
            id="existing",
            name="Existing",
            site_url="https://existing.sk",
            feed_url="https://old.existing.sk/rss",
            source_family="existing",
            resolved_feed_url="https://existing.sk/rss",
        ),
        SourceSpec(
            id="new",
            name="New",
            site_url="https://new.sk",
            feed_url="https://new.sk/rss",
            source_family="new",
        ),
    ]
    result = bootstrap_miniflux(specs, Settings(), client=client)
    assert result["retained"] == [{"source_id": "existing", "feed_id": 7}]
    assert result["created"] == [{"source_id": "new", "feed_id": 8}]
    assert len(posts) == 1
