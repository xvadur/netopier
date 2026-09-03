import httpx

from netopier.config import Settings
from netopier.miniflux import MinifluxGateway


def test_reconcile_maps_documented_miniflux_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["after_entry_id"] == "41"
        assert request.url.params["order"] == "id"
        return httpx.Response(
            200,
            json={
                "total": 1,
                "entries": [
                    {
                        "id": 42,
                        "title": "Nová správa",
                        "url": "https://example.sk/sprava",
                        "author": "Redakcia",
                        "content": "<p>Obsah</p>",
                        "hash": "abc",
                        "published_at": "2026-09-03T10:00:00Z",
                        "created_at": "2026-09-03T10:01:00Z",
                        "changed_at": "2026-09-03T10:02:00Z",
                        "feed": {"id": 9, "feed_url": "https://example.sk/rss"},
                    }
                ],
            },
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url="http://miniflux.test"
    )
    gateway = MinifluxGateway(Settings(), client=client)
    batch = gateway.reconcile(41)

    assert batch.next_cursor == 42
    assert len(batch.entries) == 1
    assert batch.entries[0].feed_id == 9
    assert batch.entries[0].feed_url == "https://example.sk/rss"
    assert batch.entries[0].published_at.isoformat() == "2026-09-03T10:00:00+00:00"


def test_reconcile_keeps_checkpoint_when_empty() -> None:
    client = httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"entries": []})),
        base_url="http://miniflux.test",
    )
    batch = MinifluxGateway(Settings(), client=client).reconcile(99)
    assert batch.entries == ()
    assert batch.next_cursor == 99
