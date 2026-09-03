# Netopier v1 night-build report

Observed 2026-09-03, Europe/Bratislava.

## Outcome

**Verified local vertical backend.** Netopier v1 is a clean sibling repository and
does not import or execute v0 code. Miniflux collects public feeds, PostgreSQL with
pgvector stores source-linked articles and derived state, FastEmbed generates local
vectors, the story engine groups conservatively, and FastAPI serves read-only JSON.

This is a usable v1 foundation, not a production release. The exact next product
decision is Adam's ratification of the 22-item Slovak benchmark packet. The next
engineering layer after ratification is a durable processing job/outbox model.

## Start and operate

```bash
cd /Users/xvadur_mac/netopier
bin/netopier-v1 up
bin/netopier-v1 bootstrap
bin/netopier-v1 once
```

The safe default leaves the continuous embedding worker stopped. `worker-on` enables
a 20-item, five-minute loop capped at one CPU and 1 GiB RAM; `worker-off` stops it.

- Miniflux: `http://127.0.0.1:8088`
- Health: `http://127.0.0.1:8090/health`
- Feed: `http://127.0.0.1:8090/feed`
- OpenAPI UI: `http://127.0.0.1:8090/docs`

## Observed runtime

| Layer | Verified state |
|---|---:|
| Feed definitions | 4 |
| Independent source families | 3 (`dennikn`, `aktuality`, `pravda`) |
| Archived articles | 56 |
| Local embeddings | 56 |
| Stories | 51 |
| Story memberships | 56 |
| Multi-source stories | 5 |
| Durable Miniflux checkpoint | 56 |

After a quiet sample the API used 44.72 MiB, Miniflux 21.68 MiB and PostgreSQL
62.63 MiB. The continuous worker was stopped after its restart probe.

## Clustering result

The provisional 22-title packet compares a word unigram/bigram TF-IDF DBSCAN
baseline with the live multilingual title-plus-RSS-text embeddings:

| Method | Pairwise precision | Recall | F1 | False merges | False splits |
|---|---:|---:|---:|---:|---:|
| TF-IDF DBSCAN @ 0.34 | 1.0000 | 0.5000 | 0.6667 | 0 | 3 |
| Temporal centroid @ 0.83 | 1.0000 | 0.8333 | 0.9091 | 0 | 1 |

Threshold 0.83 is selected because it matches the 0.79 result while remaining more
conservative. The one false split is the cross-publisher drought/farm-aid pair.
Labels remain provisional until Adam reviews them. Peak benchmark process RSS was
64.1 MiB. The cached model is pinned by a 19-file, 504,279,920-byte checksum
manifest with aggregate SHA-256
`0bd9bb070dc8a6094860fd5cfabf3da1c7b515c9b090d57bfd317f5ec4ae4ef0`.

## Proof completed

- Empty database migrated through `0004_feed_snapshots`: 11 public tables.
- Source import and stable Miniflux feed-ID binding: 4/4, no failure.
- Idempotent replay: 20 received, 20 skipped, 0 created.
- Concurrent reconcile: serialized safely; the second runner collected entry 56,
  with no duplicate article, embedding or membership.
- API and worker restarts preserved articles, stories, memberships and checkpoint.
- Snapshot pagination returned 51/51 unique stories while an existing story was
  rescored and a new story fixture was inserted concurrently; the fixture was then
  removed.
- `/health`, `/sources`, `/feed` and `/stories/{id}` passed the live smoke script.
- 13 unit tests passed; Ruff passed; mypy passed 16 source files.
- Secret scan passed 60 text files and confirmed `.env` is ignored.
- One deliberately invalid Miniflux credential produced a durable failed run with
  an error and finish timestamp. It is proof of failure recording, not a runtime
  incident.

## Open boundaries

- No webhook path is enabled; reconciliation is the only intake path.
- The benchmark lacks a verified article-update-over-time case.
- Processing is transactionally safe and serialized, but still synchronous; there
  is no durable per-stage job/outbox, lease, retry or dead-letter table yet.
- An SBOM still has to be generated before any release.
- v0 currently has 38 dirty worktree entries. No v1 build command wrote into v0,
  but a clean before/after v0 baseline was not captured, so the pre-existing dirt
  is reported instead of being misrepresented as clean.
- No commit, push, deployment or publication was performed.

Machine-readable proof is in `artifacts/verification-2026-09-03.json`; API examples
and OpenAPI are in `contracts/`; benchmark inputs and results are in `benchmarks/`.
