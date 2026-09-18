# Architecture

```text
public publisher feeds
        |
        v
Miniflux 2.3.3 ---- MinifluxGateway.reconcile(checkpoint)
                              |
                              v
              ArticleArchive.ingest(entry_batch)
                              |
                    PostgreSQL + pgvector
                              |
                              v
                 StoryEngine.assign(article_ids)
                              |
                              v
                 FeedProjector.snapshot(cursor)
                 FeedProjector.events(filters)
                              |
                         FastAPI JSON
```

The four named interfaces are the test surface. HTTP payload handling is local to
`MinifluxGateway`; SQL and story locking are local to `ArticleArchive` and
`StoryEngine`; HTTP route handlers do not reproduce domain logic.

Raw entries remain source-linked records. Story memberships and scores are derived,
versioned state. No generated synthesis is primary evidence.

Build 2A adds immutable article revisions and atomized event candidates behind the
existing `StoryEngine` interface. Bounded hybrid decisions create versioned event
clusters; suggested decisions never merge automatically. Event revisions and lineage
retain merge, split and update history. `/events` projects exact excerpts, URLs,
source IDs, timestamps, content hashes, decision features and Netopier-native filters.

`/feed` pagination creates an immutable PostgreSQL snapshot. Its opaque cursor binds
subsequent pages to a snapshot ID and position for 24 hours, so live score changes
cannot duplicate or hide a story during traversal.
