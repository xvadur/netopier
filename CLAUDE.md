# netopier — monitoring, zdroje, Event Intelligence Core, dôkazové balíky

@AGENTS.md
@PRODUCT.md
@STATUS.md
@STACK.md

Príkazy: runtime `docker compose up` (compose.yaml; Docker na mini nie je) · testy `pytest` · migrácie `alembic` · writing engine `bin/netopier-write`.
Kde čo je: `src/` FastAPI + ingest + event core + person resolution · `frontend/` „Vydanie“ (DESIGN.md) · `sources/` registre zdrojov · `contracts/` schémy · `docs/` (DISCOVERY, LINEAR_PLAN, research) · `private/research/` fact-check CSV, case ingest · `benchmarks/`.
Front: `work/`. Spustenie trvalého workera = externá mutácia.
