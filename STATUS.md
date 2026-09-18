# STATUS — netopier

## Živé
- v1 postavený od nuly (2.–3. 9.): Miniflux + Postgres/pgvector + FastAPI + lokálne embeddingy; kanonický repo `xvadur/netopier` (posledný commit 11. 9., 27 dirty)
- Build 2A Event Intelligence Core: atomizácia článkov na udalosti, päťtriedny vzťahový model, TDD
- Writing Engine v1: CLI `netopier-write`, zdrojovo uzamknutý kompilátor s hard gates
- Person resolution modul (RPO/ORSR, Meta Business Discovery konektor) — technicky hotový, bez živého tokenu
- Frontend „Vydanie“ vybraný (9. 9., DESIGN.md) — mock dáta, nenapojený na backend
- Datasety: SK Instagram Top 200; fact-check SMER/TA3 (187 tvrdení); Sulík vs. Barami proof-case + 7 363-slovný článok; mapa 10 redakcií (558 osôb) → Hriech

## Rozhodnutia
- 2026-08-30 — teardown „Minút po minúte“ a HotInfo; v1 na OSS komponentoch [A]
- 2026-09-01 — AI autorstvo sa nemaskuje, robí sa kvalitným [A]
- 2026-09-07 — Netopier = „redakcia riadená jedným kurátorom“; Hriech = autorstvo a publikácia, Netopier = monitoring a dôkazy [A]
- 2026-09-11 — Docker/OpenClaw/Hermes bežia na MacBooku, mini je pracovisko [A]

## Ďalší krok
- nič ready — napíš /issue

## Blokované
- NET-001 Rozbehnúť Netopier v1 runtime na MacBooku (worker), aby existoval dôkaz behu. — na: MacBook príprava (Docker/OpenClaw/Hermes handoff nedokončený, 11. 9.)

## Posledný receipt
- zatiaľ žiadny

## Inbox
- XDR-142 Martin Slíž: 30 príspevkov, register zdrojov, 3 reprodukcie — nedokončené
- Denný publikačný kontrakt (20–30 feed správ + 3 kurátorské články) — hypotéza, worker väčšinou vypnutý
- YouTube → prepis → porovnanie s mediálnou interpretáciou — navrhnuté v DISCOVERY.md, v kóde nie
