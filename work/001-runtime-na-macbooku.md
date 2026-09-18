---
id: NET-001
status: blocked
lane: ty
proof: na MacBooku beží docker compose up a curl /health vracia 200; z mini cez SSH readback
blocked_on: MacBook príprava (Docker/OpenClaw/Hermes handoff nedokončený, 11. 9.)
created: 2026-09-17
---
## Cieľ
Rozbehnúť Netopier v1 runtime na MacBooku (worker), aby existoval dôkaz behu.

## Scope
Áno: compose na MacBooku, SSH overenie z mini.
Nie: Docker na mini, nové funkcie.

## Podmienka dôkazu
`/health` 200 na MacBooku, readback z mini.

## Receipt
