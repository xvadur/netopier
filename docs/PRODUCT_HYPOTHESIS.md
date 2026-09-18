# Netopier product hypothesis

Netopier is a small, public, AI-assisted newsroom for Slovak political,
institutional, media, and geopolitical events. In 2026, one human operator can
use Codex and a source-linked event system to perform work that previously
required a larger editorial and software team: monitor public sources, merge
coverage into events, rank significance, prepare research, and publish a fast
public wire.

The system does not need to turn every captured item into a human-style article.
Its primary public unit is a concise, source-bounded event report that answers:

- what happened and what changed;
- who acted or spoke;
- why the event entered Netopier's editorial attention;
- which independent sources support it;
- what remains uncertain or disputed.

## Daily public output target

- 20–30 concise feed reports distributed through the day;
- at least 3 curated articles selected from the strongest events and supported
  by a bounded research pack and human ratification.

This is a product target. It becomes an operating claim only after a sustained
multi-day newsroom trial verifies source volume, relevance, evidence quality,
cost, and operator workload.

## Editorial relevance

Collection and publication are separate decisions. A routine local incident,
such as a fire in Gelnica, remains preserved in the archive but does not occupy
the public or operator priority feed by default. It can be escalated when new
evidence connects it to at least one editorially relevant mechanism:

- action or a statement by a minister, government body, police, prosecution,
  municipality, or another watched public institution;
- public money, regulation, institutional failure, or a recurring systemic
  pattern;
- political or media use of the incident as support for a broader claim;
- a material contradiction between sources about cause, consequence, legal
  status, responsibility, or affected people;
- an explicit operator watch rule or repeated ratified interest.

Every surfaced event should retain a machine-readable and human-readable
`why_surfaced` reason. Editorial relevance must not be hidden inside an opaque
model score.

## Separate judgments

Netopier keeps at least three decisions separate:

1. `event_confidence`: whether the evidence describes the same real-world event
   and how strongly it is supported;
2. `public_consequence`: the event's institutional, legal, financial, social,
   or political consequence;
3. `operator_relevance`: whether the event belongs in the newsroom's current
   attention and research agenda.

Popularity or coverage momentum may inform ordering, but it cannot replace any
of these judgments. Factual summaries, attributed claims, operator commentary,
research synthesis, and published revisions remain distinct artifacts.

## Human responsibility

Automation may collect, cluster, score, summarize, and prepare bounded research.
The operator owns the editorial policy, ratifies its changes, selects the three
curated daily pieces, and explicitly authorizes publication. Every public output
must remain traceable to its evidence and revision history.

## Public-state sensing

Publisher coverage is not the only event source. Netopier should also detect
public acts directly from official records such as contracts, registries,
procurement, corporate filings, and justice datasets. This is a proposed product
extension, not an implemented capability or a claim that every source exposes a
stable public API.

Official records enter as immutable, source-linked revisions. Entity matches,
diffs, anomaly scores, and alerts remain derived research leads until a human
checks the source and context. They never become allegations or public stories
automatically. The bounded source plan and founding editorial case are recorded
in `/Users/xvadur_mac/hriech/research/editorial/STATE_READING_EDITORIAL_BRIEF_2026-09-03.md`.
Hriech owns the media-criticism case and its public presentation; Netopier owns
the public-source collection and event-intelligence machinery that can supply it.
