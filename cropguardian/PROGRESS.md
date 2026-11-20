# PROGRESS

Phase status, gate tables, known issues. One line per member per day (DONE / PARTIAL / BLOCKED + reason).
Nothing in this repository has been committed or pushed by the assistant (owner's instruction).

## Phase status
| Phase | Owner | Status | Gate |
|---|---|---|---|
| P0 Foundations | Apon | **GATE PASS** 2026-10-21 (full run, not `--offline`); R7/R11 closed by the owner (attested); CI run and built-in `/security-review` still pending | `make gate PHASE=0` → `PHASE 0 GATE: PASS` |
| P1 Identity, sessions, tenancy | Apon + team | **GATE PASS** 2026-10-21 (full run, not `--offline`); R12 closed by the owner (attested); one flaky failure seen earlier, see below; `/security-review` and CI run still pending | `make gate PHASE=1` → `PHASE 1 GATE: PASS` |
| P2 Design system, shells, landing | Sara + Raisa (solo build) | **IN PROGRESS** — Block 1 of 4 DONE 2026-10-21 (primitives, tooling, gate scaffolding, 3 defects fixed); Blocks 2-3 (shells, landing, 3D) not started; target gate Fri 23 Oct (D-024) | `make gate PHASE=2` → FAIL only on not-yet-built items (see Phase 2 section) |
| P3 ML data (17 Oct part) | Taeen | day-1 scope DONE | gate not run |
| P5 KB (17 Oct part) | Salwa | day-1 scope DONE | gate not run |
| P4, P6–P12 | — | not started | — |

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
1. (done 2026-10-21, owner-attested) `SECRET_KEY` rotated on Render: R12 RESOLVED.
2. Run the 0003 revokes on Supabase (migration `0003_revoke_api_roles.py`; the live DB already has the same revokes applied by hand, but `alembic_version` still says 0002) and restart the Render service so the demo-user seed runs.
3. `git push` a branch when ready: Render root directory `cropguardian/backend`, health check `/health`, auto-deploy "After CI checks pass".
4. Run the built-in `/security-review` and append its output.

## Known issues
- Render health check path is still `/healthz` (works); set it to `/health` in the dashboard. Auto-deploy is on every commit and should be "After CI checks pass". Both are dashboard-only.
- The Supabase MCP is connected to the right project but read-only by design, so the owner applies DDL (SQL Editor or `make migrate`). The Render MCP needs re-authentication. The Vercel MCP lists only project `abhijatri` (wrong account for the prototype); the prototype root URL returns 404 with `X-Vercel-Error: NOT_FOUND` on every path (probed 2026-10-21): that is Vercel's "no deployment at this alias" response, not an application 404, so the alias or deployment must be fixed in the Vercel dashboard (owner).
- The git root is the parent folder; CI lives in the root `.github/` (D-013).
- D2 archive holds 3,150 images but its page/README state 2,545 (unexplained); D1 has 22 cross-class duplicate groups.
- `webapp-testing` skill uses `shell=True` by design (local use only).
- Rubric version (D-004) not yet confirmed from the Participants Guide.

## Next (18 Oct row of each member)
Apon P1 models/RLS/core security · Taeen pHash groups + split v1 · Salwa extraction/OCR + chunking · Raisa advisory prompt v0 + 20 golden Q&A · Sara primitives + i18n lint.

## Phase 1 - Identity, sessions, tenancy, security core (work done 2026-10-21; gate PASS 2026-10-21)
Gate history (full runs): R12 open -> only step 6 failed; after R12 closed, one run failed at step 21 (1 failed, 579 passed; the failing test's name was not captured), the next run passed all 21 steps (identity suite on real Postgres+Redis with coverage floors met, compose smoke 15 end-to-end checks, hosted readiness db+redis ok). A standalone full-suite rerun passed 580/580 and six runs of `tests/security/test_identity_security.py` all passed, so the flake is **unidentified**. `phase_gate.py` now prints the `FAILED ...` test names in step 21's note so the next occurrence can be diagnosed. Suspect, unproven: the 50 ms login-timing test (`test_login_timing_does_not_reveal_whether_the_account_exists`).
| Role | Done |
|---|---|
| Apon | migration 0002 (11 tables, FORCE RLS, up/down/up on real Postgres), security core, endpoints, scripts, authz matrix (204 cases), schemathesis zero 5xx |
| Salwa | review pass in `docs/security-reviews/phase-01.md` |
| Sara | fetch wrapper, guards, auth pages, demo picker, role homes, 403/404, DEMO ribbon; 129 tests; 7 Chromium journeys |
| Raisa | bn/en auth copy, consent texts v1, SMS/email templates (team-authored, not expert-reviewed) |
| Taeen | none in Phase 1 |
Verified: backend 576 tests, six security modules 100% line+branch, total 92.8%; compose smoke 15/15; frontend lint/typecheck/build/audit pass.
Applied to Supabase by the owner on 2026-10-21 (0001+0002 via the SQL Editor); verified read-only afterwards. Migration 0003 (revoke API roles) added after the advisor found `audit_tail_hash()` callable by `anon` (R13).
**Remaining (owner):** record 0003 on Supabase; restart Render so demo users are seeded (the `users` table is empty until then); run the built-in `/security-review`; push a branch so GitHub Actions runs once.
- gate phase 0: FAIL (step 5 gitleaks) at 2026-10-21T16:04:27.176261+00:00
- gate phase 0: FAIL (step 5 gitleaks) at 2026-10-21T16:08:35.818367+00:00
- gate phase 0: FAIL (step 5 gitleaks) at 2026-10-21T16:10:23.324560+00:00
- gate phase 0: FAIL (step 9 backend tests) at 2026-10-21T16:12:28.735782+00:00
- gate phase 0: FAIL (step 9 backend tests) at 2026-10-21T16:14:30.221396+00:00
- gate phase 0: FAIL (step 9 backend tests) at 2026-10-21T16:16:10.239429+00:00
- gate phase 0: PASS at 2026-10-21T16:21:22.597299+00:00
- gate phase 1: FAIL (step 6 security review) at 2026-10-21T16:30:24.506982+00:00
- gate phase 1: FAIL (step 21 P1 identity suite) at 2026-10-21T16:42:22.982260+00:00
- gate phase 1: PASS at 2026-10-21T16:54:15.483911+00:00
- gate phase 2: FAIL (step 6 security review) at 2026-10-21T17:52:19.816138+00:00

## Phase 2 - Design system, shells, landing page (solo; plan: `docs/plans/phase-02.md`; decisions D-020..D-028)
**Block 1 DONE 2026-10-21:** ~25 token-styled primitives (native `<dialog>` modals, D-025), motion/format/prefs libraries, ESLint design-token rules, `check_i18n.py`, bundle-budget gate, Playwright 360/768/1366/slow-3G projects + axe spec, P2 gate steps that FAIL when unbuilt. Verified: frontend 262 tests (stable over 3 runs), backend unit 265, lint/tsc/build/budgets/CSP pass, **axe E2E 84/84** (7 screens x light/dark x bn/en x 3 widths, zero CSP violations).
**Defects found by the new gates and fixed:** Bangla fonts 192.7 KB vs 120 KB budget (D-026); Zod probing eval under the strict CSP (D-027); Phase 1 register page had unnamed consent checkboxes while loading, now fail-closed (D-028).
`make gate PHASE=2` (keep-going) fails only on: security review file (Block 4), layout/shells E2E spec (Block 2), visual spec, Lighthouse script, stills manifest (Block 3).
**Next:** Block 2 - `/app` route rename (D-020), public/farmer/staff shells, offline page, `/dev/ui-kit`, layout (CC-40) + shells E2E.
**Open questions for the owner:** confirm D-020 (`/home` -> `/app`); which Vercel account owns the prototype; accept poster-only hero if Block 3 slips.

## 20 Nov 2026 - Gantt 10-13 Nov plan, P2-P4 slice (deadline day; decisions D-031..D-035)
Built: scan upload (hardened: size, magic bytes, decode, bomb guard, EXIF/GPS strip, SHA-256, Idempotency-Key) -> Llama 4 vision -> abstain logic -> BRRI KB retrieval (39 AI-transcribed chunks, no chemicals) -> Bangla advice validated (citations, verbatim numbers, no chemicals, Bangla, injection) with verbatim static-card fallback -> outbreak drafts -> reviewer approve/decline (+ audit; step-up for real staff) -> farmer sees approved "possible outbreak, unverified". Farmer app `/app` (home, scan with camera/gallery + division, result / not-sure + office card + read-aloud, history, alerts, more, offline IndexedDB outbox with the same Idempotency-Key), reviewer `/review`, public Trust Centre `/trust`.
Verified locally (2026-11-20): backend 778 passed incl. 10 new end-to-end API tests, 9 new RLS tests on real Postgres, 101 new unit tests, authz matrix incl. the 6 new routes; migration 0004 up/down/up; `infra/supabase/0004_scans_alerts.sql` applied to a fresh 0003 DB; frontend 265/265 (twice), lint, tsc, CSP check, budgets (initial 138/170 KB); Chrome walkthrough on localhost: demo farmer -> scan -> honest "not sure" (no key locally), demo reviewer -> approve -> audit row.
NOT verified yet: a real Llama call (key only on Render), the hosted deploy, a phone over mobile data. No accuracy, latency or eval number exists; none is claimed.
Owner actions: run the SQL file in Supabase; set LLAMA_API_KEY, DEMO_ENABLED=true, DEMO_SEED_ON_START=true on Render; push.
