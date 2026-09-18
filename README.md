# Netopier v2

Clean, local-first Slovak public-source news-intelligence backend. Netopier v2
replaced the retired v0 implementation and lives in the canonical `netopier`
folder and GitHub repository.

## Schválený smer frontendu — Vydanie

Ďalší vývoj frontendu vychádza z prvého schváleného návrhu **Vydanie**:
veľký názov NETOPIER, serifová typografia, čiernobiela fotografia, červené
akcenty a novinové stĺpce. Výber návrhu je z 9. septembra 2026; rozhodnutie
zaznamenať ho v GitHube bolo potvrdené 11. septembra 2026.

**[Schválený obrázok, dizajnový smer a rozsah ďalšieho vývoja → DESIGN.md](DESIGN.md)**

Ide o schválený základ na rozvíjanie; webová implementácia ešte nie je dokončená.

## Local state — 2026-09-07

This is the retained, usable v2 foundation. The retired v0 was deleted separately;
its code and runtime must not be restored into this project.

The Mac cleanup intentionally removed Colima and stopped the local container
runtime. The addresses below describe the configured services; they are not
currently running. The private database recovery export is preserved in
`/Users/xvadur_mac/Archive/mac-cleanup-2026-09-07/docker-recovery/`.
Starting the stack again requires an explicit decision to provision a container
engine. Previous integration results in `docs/reports/` remain dated evidence.

`bin/netopier` now resolves the project directory when called from another folder.
The local CLI routing and secret scan were checked on 2026-09-07; a new live
RSS-to-feed verification awaits the container runtime. The Python package requires
Python 3.12; the system Python 3.9 is insufficient for the application tests.

Current exploration of public sources, monitoring and research lives in
[`docs/DISCOVERY.md`](docs/DISCOVERY.md). The public-newsroom output hypothesis
is documented separately in
[`docs/PRODUCT_HYPOTHESIS.md`](docs/PRODUCT_HYPOTHESIS.md); its targets are a
proposal, not proof of implemented output. See the [documentation index](docs/README.md).

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
docker compose run --rm api netopier sources import sources/slovak-core.yaml
docker compose run --rm api netopier sources bootstrap-miniflux sources/slovak-core.yaml
docker compose up -d api
```

This safe default leaves the embedding worker off. Run one bounded batch with
`bin/netopier once`. Enable continuous reconciliation explicitly with
`bin/netopier worker-on`; stop it with `bin/netopier worker-off`. Continuous
mode processes at most 20 entries every five minutes and the worker container is
limited to one CPU and 1 GiB RAM.

The local interfaces are:

- Miniflux: `http://127.0.0.1:8088`
- Netopier API health: `http://127.0.0.1:8090/health`
- Feed: `http://127.0.0.1:8090/feed`
- Events: `http://127.0.0.1:8090/events`

## Verify

```bash
docker compose run --rm api netopier reconcile
docker compose run --rm api netopier process
bin/netopier test
bin/netopier smoke
bin/netopier snapshot-smoke
bin/netopier contracts
bin/netopier secret-scan
bin/netopier model-manifest
docker compose run --rm api python benchmarks/run_benchmark.py
docker compose run --rm api python benchmarks/run_event_benchmark.py
```

See [architecture](docs/ARCHITECTURE.md), [decisions](docs/DECISIONS.md), and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Benchmark inputs and the latest
measured report live under [`benchmarks/`](benchmarks/).
