# PROGRESS

Phase status, gate tables, known issues. One line per member per day (DONE / PARTIAL / BLOCKED + reason).
Nothing in this repository has been committed or pushed by the assistant (owner's instruction).

## Phase status
| Phase | Owner | Status | Gate |
|---|---|---|---|
| P0 Foundations | Apon | **PARTIAL** — 17 of 18 gate steps pass on a full run, hosted API live; 1 owner-only blocker | `make gate PHASE=0` → FAIL only at security review (R7, R11: rotate credentials) |
| P2 Design system (17 Oct part) | Sara + Raisa | day-1 scope DONE | gate not run (P2 not complete) |
| P3 ML data (17 Oct part) | Taeen | day-1 scope DONE | gate not run |
| P5 KB (17 Oct part) | Salwa | day-1 scope DONE | gate not run |
| P1, P4, P6–P12 | — | not started | — |

## Daily log
- 17 Oct (catch-up, executed 21 Oct) Apon: **PARTIAL** — P0 foundations built and verified locally (see gate table); blocked on owner actions (rotate Supabase credentials; Render cut-over to `backend/`).
- 17 Oct Taeen: **DONE** — `cg_ml` data pipeline, D1/D2 downloaded + checksums verified, EDA figures, datasheets. Findings: D2 count mismatch, D1 cross-class duplicates, resolution confound.
- 17 Oct Salwa: **DONE** — `kb/sources.yaml` with 15 real documents + validator; OCR needed for all BRRI PDFs; banned-pesticide list still a GAP.
- 17 Oct Raisa: **DONE** — Bangla style guide, `bn.json`/`en.json` first strings, personas review (team-authored, not expert-reviewed).
- 17 Oct Sara: **DONE** — `cropguardian-ui` skill, tokens, contrast + drift tests, motion tokens.

## Phase 0 gate table (full run, NOT `--offline`: 2026-10-21, real Postgres, real compose stack, hosted URL set)
| Step | Result |
|---|---|
| environment, openapi contract, frontend build, format+lint, frontend lint, mypy, Bandit | PASS |
| gitleaks 8.30.1 (git history 7 commits + working tree) | PASS — 0 leaks |
| project checks (forbidden, layers, honesty), check_rls | PASS |
| pip-audit (backend + ml) | PASS — after upgrading FastAPI/Starlette and Pillow (D-014) |
| npm audit gate | PASS — runtime deps clean; 2 dev-only advisories accepted until 2026-11-30 |
| migrations (up, down, up on real pgvector Postgres) | PASS |
| backend tests (141 + 1 skipped on Windows), security suite, frontend tests (63) | PASS |
| compose stack: build, up, healthy, migrate, 16 Nginx edge checks | PASS |
| **security review** | **FAIL** — R7 and R11 UNRESOLVED-HIGH (owner: rotate Supabase DB password + secret key; revoke the Render API key pasted in chat) |
| hosted `/health` | PASS — live deploy `dep-dbc6nq8n74is73fiqin0` (commit `29596a9`): `/health` 200, `/health/ready` `{"db":"ok"}`, docs/openapi/metrics hidden, one copy of each security header, CORS only for the prototype origin, TRACE 405, 2 MB body 413, structured request logs in Render |

Also verified: Chromium smoke through the real Nginx stack, production-mode rehearsal of the API image (see
`docs/DEPLOYMENT.md`), anonymous access to the object-store buckets returns 403, ML tests 49 (94% branch coverage).
**Not verified:** the hosted deployment itself, Supabase (MCP session still stale: restart Claude Code), the built-in
`/security-review` command, GitHub Actions run (workflows validated as YAML only).

## What closes Phase 0 (only you can)
1. Restart Claude Code, `/mcp`, authenticate supabase (`elkhvfcawllyoearrxop`); rotate the DB password + secret key; revoke the Render key pasted in chat.
2. `git push` a branch; in Render set Root Directory `cropguardian/backend`, branch, health check `/health`, env vars (`docs/DEPLOYMENT.md`).
3. Run `/security-review`; then I flip R7/R11 to RESOLVED and re-run the gate expecting `PHASE 0 GATE: PASS`.

## Known issues
- Render health check path is still `/healthz` (works); set it to `/health` in the dashboard. Auto-deploy is on every commit and should be "After CI checks pass". Both are dashboard-only.
- The Supabase MCP session is stale: it loads project ref `sgoxsghtkmcikzyxoqgj` (not `elkhvfcawllyoearrxop`) and fails OAuth discovery. Restart Claude Code. The Vercel MCP lists only project `abhijatri` (wrong account for the prototype). Render MCP works (one workspace) but I wait for your confirmation before using it.
- The git root is the parent folder; CI lives in the root `.github/` (D-013).
- D2 archive holds 3,150 images but its page/README state 2,545 (unexplained); D1 has 22 cross-class duplicate groups.
- `webapp-testing` skill uses `shell=True` by design (local use only).
- Rubric version (D-004) not yet confirmed from the Participants Guide.

## Next (18 Oct row of each member)
Apon P1 models/RLS/core security · Taeen pHash groups + split v1 · Salwa extraction/OCR + chunking · Raisa advisory prompt v0 + 20 golden Q&A · Sara primitives + i18n lint.
