# PROGRESS

Phase status, gate tables, known issues. One line per member per day (DONE / PARTIAL / BLOCKED + reason).
Nothing in this repository has been committed or pushed by the assistant (owner's instruction).

## Phase status
| Phase | Owner | Status | Gate |
|---|---|---|---|
| P0 Foundations | Apon | **GATE PASS** 2026-10-21 (full run, not `--offline`); R7/R11 closed by the owner (attested); CI run and built-in `/security-review` still pending | `make gate PHASE=0` → `PHASE 0 GATE: PASS` |
| P1 Identity, sessions, tenancy | Apon + team | **GATE FAIL at one step** — 20 of 21 steps pass; only R12 (rotate `SECRET_KEY`) is open | `make gate PHASE=1` → FAIL (step 6 security review: R12 UNRESOLVED-HIGH) |
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
| gitleaks 8.30.1 (git history 30 commits + working tree) | PASS — 9 fake test fixtures pinned by exact fingerprint (D-019); 0 other findings |
| project checks (forbidden, layers, honesty), check_rls | PASS |
| pip-audit (backend + ml) | PASS — after upgrading FastAPI/Starlette and Pillow (D-014) |
| npm audit gate | PASS — runtime deps clean; 2 dev-only advisories accepted until 2026-11-30 |
| migrations (up, down, up on real pgvector Postgres) | PASS |
| backend tests (full suite on real Postgres + Redis), security suite, frontend tests | PASS |
| compose stack: build, up, healthy, migrate, Nginx edge checks | PASS |
| security review | PASS — R7 and R11 RESOLVED 2026-10-21 (owner-attested: the assistant cannot verify a rotation) |
| hosted `/health` | PASS — `/health` 200; `/health/ready` `{"db":"ok","redis":"ok"}` after the credential rotation |

Also verified (2026-10-21): Supabase `elkhvfcawllyoearrxop` is at migration 0002 with forced RLS on all 16 tables, 34 policies, 13 seeded settings, `cg_*` roles, no `anon`/`authenticated` table grants; the advisor lists only `vector` in `public` (accepted, R14).
**Not verified:** GitHub Actions run (nothing pushed; workflows validated as YAML only), the built-in `/security-review` command.

## What is still open (owner)
1. Confirm `SECRET_KEY` was rotated on Render and redeployed (R12), so I can flip it to RESOLVED and re-run `make gate PHASE=1`.
2. Run the 0003 revokes on Supabase (migration `0003_revoke_api_roles.py`; the live DB already has the same revokes applied by hand, but `alembic_version` still says 0002) and restart the Render service so the demo-user seed runs.
3. `git push` a branch when ready: Render root directory `cropguardian/backend`, health check `/health`, auto-deploy "After CI checks pass".
4. Run the built-in `/security-review` and append its output.

## Known issues
- Render health check path is still `/healthz` (works); set it to `/health` in the dashboard. Auto-deploy is on every commit and should be "After CI checks pass". Both are dashboard-only.
- The Supabase MCP is connected to the right project but read-only by design, so the owner applies DDL (SQL Editor or `make migrate`). The Render MCP needs re-authentication. The Vercel MCP lists only project `abhijatri` (wrong account for the prototype); the prototype root URL returns 404 (not investigated).
- The git root is the parent folder; CI lives in the root `.github/` (D-013).
- D2 archive holds 3,150 images but its page/README state 2,545 (unexplained); D1 has 22 cross-class duplicate groups.
- `webapp-testing` skill uses `shell=True` by design (local use only).
- Rubric version (D-004) not yet confirmed from the Participants Guide.

## Next (18 Oct row of each member)
Apon P1 models/RLS/core security · Taeen pHash groups + split v1 · Salwa extraction/OCR + chunking · Raisa advisory prompt v0 + 20 golden Q&A · Sara primitives + i18n lint.

## Phase 1 - Identity, sessions, tenancy, security core (work done 2026-10-21; gate run 2026-10-21: 20 of 21 steps PASS)
Gate run (full, `--keep-going`): everything passes (identity suite 133 s on real Postgres+Redis with coverage floors met, compose smoke 15 end-to-end checks, hosted readiness db+redis ok) except **step 6 security review**: R12 (`SECRET_KEY` passed through chat) is UNRESOLVED-HIGH until the owner confirms rotation.
| Role | Done |
|---|---|
| Apon | migration 0002 (11 tables, FORCE RLS, up/down/up on real Postgres), security core, endpoints, scripts, authz matrix (204 cases), schemathesis zero 5xx |
| Salwa | review pass in `docs/security-reviews/phase-01.md` |
| Sara | fetch wrapper, guards, auth pages, demo picker, role homes, 403/404, DEMO ribbon; 129 tests; 7 Chromium journeys |
| Raisa | bn/en auth copy, consent texts v1, SMS/email templates (team-authored, not expert-reviewed) |
| Taeen | none in Phase 1 |
Verified: backend 576 tests, six security modules 100% line+branch, total 92.8%; compose smoke 15/15; frontend lint/typecheck/build/audit pass.
Applied to Supabase by the owner on 2026-10-21 (0001+0002 via the SQL Editor); verified read-only afterwards. Migration 0003 (revoke API roles) added after the advisor found `audit_tail_hash()` callable by `anon` (R13).
**Blockers (owner):** rotate and redeploy `SECRET_KEY` (R12); record 0003 on Supabase; restart Render so demo users are seeded (the `users` table is empty until then).
- gate phase 0: FAIL (step 5 gitleaks) at 2026-10-21T16:04:27.176261+00:00
- gate phase 0: FAIL (step 5 gitleaks) at 2026-10-21T16:08:35.818367+00:00
- gate phase 0: FAIL (step 5 gitleaks) at 2026-10-21T16:10:23.324560+00:00
- gate phase 0: FAIL (step 9 backend tests) at 2026-10-21T16:12:28.735782+00:00
- gate phase 0: FAIL (step 9 backend tests) at 2026-10-21T16:14:30.221396+00:00
- gate phase 0: FAIL (step 9 backend tests) at 2026-10-21T16:16:10.239429+00:00
- gate phase 0: PASS at 2026-10-21T16:21:22.597299+00:00
- gate phase 1: FAIL (step 6 security review) at 2026-10-21T16:30:24.506982+00:00
