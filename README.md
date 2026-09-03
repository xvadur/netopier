# Netopier

Clean, local-first Slovak public-source news-intelligence backend. This codebase
replaced the retired v0 implementation and is the canonical Netopier repository.

The public newsroom direction, editorial relevance boundary, and daily output
target are defined in [`PRODUCT_HYPOTHESIS.md`](PRODUCT_HYPOTHESIS.md).
The supporting product and open-source precedent is captured in
[`docs/research/AI_NEWSROOM_AND_NATURAL20_TEARDOWN_2026-09-03.md`](docs/research/AI_NEWSROOM_AND_NATURAL20_TEARDOWN_2026-09-03.md).

## Runtime

- Miniflux 2.3.3 collects RSS/Atom/JSON Feed.
- PostgreSQL 17 + pgvector 0.8.6 stores provenance, embeddings, stories and revisions.
- FastEmbed produces local multilingual embeddings.
- FastAPI exposes read-only JSON interfaces.
- One worker reconciles Miniflux, archives articles and assigns stories.

## Start

```bash
cp .env.example .env
# Replace every change-me value in .env.
docker compose up -d postgres miniflux
docker compose run --rm api alembic upgrade head
docker compose run --rm api netopier-v1 sources import sources/slovak-core.yaml
docker compose run --rm api netopier-v1 sources bootstrap-miniflux sources/slovak-core.yaml
docker compose up -d api
```

This safe default leaves the embedding worker off. Run one bounded batch with
`bin/netopier-v1 once`. Enable continuous reconciliation explicitly with
`bin/netopier-v1 worker-on`; stop it with `bin/netopier-v1 worker-off`. Continuous
mode processes at most 20 entries every five minutes and the worker container is
limited to one CPU and 1 GiB RAM.

The local interfaces are:

- Miniflux: `http://127.0.0.1:8088`
- Netopier API health: `http://127.0.0.1:8090/health`
- Feed: `http://127.0.0.1:8090/feed`
- Events: `http://127.0.0.1:8090/events`

## Verify

```bash
docker compose run --rm api netopier-v1 reconcile
docker compose run --rm api netopier-v1 process
bin/netopier-v1 test
bin/netopier-v1 smoke
bin/netopier-v1 snapshot-smoke
bin/netopier-v1 contracts
bin/netopier-v1 secret-scan
bin/netopier-v1 model-manifest
docker compose run --rm api python benchmarks/run_benchmark.py
docker compose run --rm api python benchmarks/run_event_benchmark.py
```

See [ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md), and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Benchmark inputs and the latest
measured report live under [`benchmarks/`](benchmarks/).
