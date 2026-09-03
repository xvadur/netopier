# Build 2A — Event Intelligence Core

Observed 2026-09-03, Europe/Bratislava.

## Result

Build 2A adds a local-first, versioned event layer above preserved article evidence.
The event cluster is now available through `/events`; legacy `/feed` and stories remain
compatible. Processing stays opt-in and bounded to 20 items per call. No feed, worker,
deployment, push or external service was changed.

## Implemented

- Immutable `article_revisions` with URL, source identity, publication/collection time,
  content hash and raw payload inherited from the canonical article.
- Deterministic `EventCandidateExtractor.atomize(article_revision)` with multiple
  candidates per article and exact source excerpts plus character offsets.
- Five relationship classes: `syndicated_copy`, `same_event`, `event_update`,
  `same_topic`, and `unrelated`.
- Bounded candidate generation: 72-hour window, vector/actor/organization/location/action
  prefilter, maximum 20 cluster comparisons, and exclusion of candidates from the same
  article revision.
- Conservative `event-hybrid-v2` decisions with persisted features, score, threshold
  version, reason, time, origin and accepted/suggested status. Suggested decisions create
  a separate event and never merge automatically.
- Versioned event revisions, human merge/split correction interfaces and lineage. Old
  clusters and old decisions are retained rather than overwritten.
- Independent-source counts exclude `syndicated_copy` memberships.
- `/events` JSON cards with title, source-bounded summary, time/place, actors,
  organizations, status, article/source-family counts, timeline, exact evidence,
  confidence, conflicts, revisions and suggested decisions.
- Filters for people, organizations, public institutions, geography, time, action type,
  institutional status, independent-source count, novelty, evidence strength, coverage,
  article count and conflicts.
- Reproducible five-pair event relationship benchmark comparing lexical, embedding and
  hybrid methods. LlamaIndex was not added.
- Dockerfile stage order now lets a runtime target stop before installing test tooling.

## Tested

- 18 tests passed.
- Ruff passed.
- mypy passed 17 source files.
- Fresh temporary database migrated from empty state through `0006_event_lifecycle`;
  a second `upgrade head` was a no-op and all seven event tables existed.
- Secret scan passed 73 text files and confirmed `.env` remains ignored.
- Benchmark fixture URLs all resolved to articles and embeddings in the local archive.

Benchmark (five provisional, source-linked pairs):

| Method | Merge precision | Merge recall | Merge F1 | False merges | False splits |
|---|---:|---:|---:|---:|---:|
| lexical baseline | 1.0000 | 0.3333 | 0.5000 | 0 | 2 |
| embedding baseline | 1.0000 | 0.6667 | 0.8000 | 0 | 1 |
| hybrid-event-v2 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 |

This tiny fixture is an engineering check, not a general quality claim. The exact-copy
case is an idempotent replay of one canonical article because duplicate ingestion had
already removed duplicate rows. The event-update label is provisional and needs Adam's
editorial ratification.

## Runtime observed

- Alembic is at `0006_event_lifecycle` in the local v1 database.
- 56 articles, 56 immutable initial revisions, 57 event candidates and 54 active events.
- One article produced two candidates.
- Three accepted cross-publisher `same_event` merges, all manually read back as correct:
  the Naháč fire, the Bratislava fatal fall and the Malta acquittal.
- All three merged events have two independent source families.
- The EU sanctions pair remains a `suggested` decision and stayed split.
- Zero same-article candidates were classified as syndicated copies after the guard fix.
- A final bounded process replay created and assigned zero records.
- `/events`, `/health`, `/sources`, `/feed` and story detail passed live smoke; event
  evidence, decision history, timeline and independence filtering were present.
- API, PostgreSQL and Miniflux are healthy; the continuous worker remains stopped.

## Still open

- The rule atomizer is deliberately small and has limited Slovak entity, action, place
  and institutional-status extraction. Many short RSS summaries use the fallback
  `reported_development` action.
- No real changed article revision, cross-publisher syndicated copy or accepted
  `event_update` was observed in this 56-article runtime corpus. Their code paths and
  fixture behavior are tested, but they are not runtime-proven.
- Human merge/split methods and lineage are implemented but were not invoked against the
  live corpus because no editorial correction was authorized or required.
- Conflict extraction is represented in the contract but not yet populated by a
  contradiction detector.
- Docker Desktop's 30 GiB internal disk was full during migration. Reproducible dangling
  Netopier v1 build images were removed; no volumes or unrelated tagged images were
  deleted.

## Next smallest step

Adam should ratify the five benchmark pairs and the EU-sanctions suggested decision.
Then add those decisions as fixed regression evidence and improve the deterministic
Slovak entity/action extractor against this same corpus before collecting more feeds.
