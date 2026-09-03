# Event relationship benchmark

Dataset: `netopier-event-relations-2026-09-03` (5 source-linked pairs)
Review status: **provisional**

| Method | Accuracy | Merge precision | Merge recall | Merge F1 | False merges | False splits |
|---|---:|---:|---:|---:|---:|---:|
| lexical-baseline | 0.4000 | 1.0000 | 0.3333 | 0.5000 | 0 | 2 |
| embedding-baseline | 0.8000 | 1.0000 | 0.6667 | 0.8000 | 0 | 1 |
| hybrid-event-v2 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 | 0 |

False merge means the method would automatically combine a same-topic or unrelated pair. 
False split means it would separate a syndicated copy, same event, or event update.

## Evidence boundary

Every pair points to public articles present in the bounded local archive. The exact-copy case intentionally replays one canonical article because ingestion removed duplicate rows. The event-update label is a provisional editorial judgment and requires Adam's ratification.

Peak process RSS observed: 63.1 MiB.
