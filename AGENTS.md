# Netopier Agent Rules

## Purpose

Netopier v2 is a clean, local-first Slovak public-source news intelligence backend.
The previous v0 implementation is retired and must not be reintroduced.

## Hard boundaries

- Never restore or import retired v0 pipeline code, runtime state, generated bundles,
  schedulers, or clusters into the canonical implementation.
- Public sources only. Preserve source URL, publication time, collection time, source ID,
  raw payload hash, and algorithm/model version.
- Keep raw evidence separate from derived stories, scores, and synthesis.
- LLM output is optional derived data and can never block collection or story formation.
- Runtime data and credentials stay under ignored paths or Docker volumes.
- No deploy, push, publication, production credentials, or external mutation without
  explicit current-conversation authorization.

## Engineering contract

- Prefer maintained OSS for commodity mechanics; own Slovak source semantics, story
  assignment, ranking, provenance, and feed contracts.
- Keep four deep modules: `MinifluxGateway`, `ArticleArchive`, `StoryEngine`, and
  `FeedProjector`. Tests and callers use the same interfaces.
- Miniflux owns feed polling. PostgreSQL/pgvector owns Netopier persistence and exact
  vector search. FastAPI is a thin transport adapter.
- One authoritative story-assignment writer during alpha.
- A false merge is costlier than a false split.
- New behaviour needs an interface-level test and proportional integration proof.

## Proof states

Distinguish implemented, unit-tested, integration-tested, runtime-observed, persisted,
and destination-verified. A container starting is not a successful RSS-to-feed loop.
