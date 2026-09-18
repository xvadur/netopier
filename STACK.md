# STACK — netopier
prefix: NET

## Zámok
Backend: Python 3 + FastAPI · DB: Postgres + pgvector (Alembic) · Feed: Miniflux · Embeddingy: lokálne (FastEmbed/ONNX) · Runtime: Docker compose (`compose.yaml`) · Frontend: „Vydanie“ — čiernobiela novinová typografia s červenými akcentmi (DESIGN.md, schválené 9. 9.)
Dizajnový smer: „Vydanie“ zamknutý. Ďalšie „50 smerov“ sa nerobia; robí sa napojenie Vydania na backend.

## Príkazy
dev: `docker compose up` (na mini bez Dockera: len testy a statické časti)
build: —
test: `pytest`
deploy: — (žiadny cieľ; runtime = MacBook worker, nerozhodnutý dátum)
proof: `pytest` + pre runtime: `curl -s http://127.0.0.1:8000/health`

## Hranice
Cloudové spracovanie textov (OpenRouter, embedding API) zakázané — súkromie. `private/research/` sa nepublikuje. Docker na mini sa neinštaluje (RAM); runtime dôkaz čaká na MacBook.
