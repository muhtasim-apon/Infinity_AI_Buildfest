# DECISIONS

Format: ID · date · decision · reason · alternatives.

- **D-001 · 2026-10-21 · Build Spec is the baseline.** `CROP_GUARDIAN_BUILD_SPEC.md` supersedes `docs/` where they
  differ (human review loop, own sessions + RLS, arq not n8n, d3-geo not Leaflet). Reason: Gantt PDF §1 verdict.
  Alternatives: keep docs/ design (smaller but lacks reviewer queue and safety rubric coverage).
- **D-002 · 2026-10-21 · Layout.** Spec §4 tree (`backend/`, `frontend/`, `infra/`) is built under `cropguardian/`
  as repo root. Legacy `services/api` + `apps/web` stay until Render is cut over to `backend/` once `/health` is
  200 on the hosted stack. Alternatives: rename in place (risks breaking the live Render + UptimeRobot setup).
- **D-003 · 2026-10-21 · Hosted DB connection.** Supabase transaction pooler (port 6543), asyncpg
  `statement_cache_size=0` (spec §5.2).
- **D-004 · OPEN · Judging rubric version** (6 weighted criteria vs 5 × 20): confirm from the Participants Guide
  (`../AI Builders Congress 2026 - Participants Guide.pdf`) and record here (spec §23).
- **D-005 · 2026-10-21 · Python.** Runtime 3.12 (Docker). Local dev machine has 3.13; tests must pass on both.
- **D-006 · 2026-10-21 · Skills reviewed and pinned.** anthropics/skills @ dbd4588f9e1033efb41dad4bef2f7947c8993d44 (frontend-design, webapp-testing, skill-creator: Apache-2.0; skill-creator installed minus eval-viewer + eval scripts); CloudAI-X/threejs-skills @ 0e181866f095b5f06d005133876e926515390d95 (MIT, 7 docs-only skills). pdf and pptx are proprietary (no copying/redistribution) and are NOT committed: use the Claude-provided copies. Details: .claude/skills/README.md.
- **D-007 · 2026-10-21 · Design-token deviations (verified by `frontend/src/design/contrast.test.ts`).**
  (a) Spec 15.1 `--text-subtle` `#66766B` measures 4.496:1 on `--bg` `#F6F8F3` (WCAG AA needs 4.5:1), so it is
  `#657569` (4.565:1). Captions in `--text-subtle` must not be placed on `--surface-2` (4.33:1).
  (b) Dark-theme status colours are not given hex values in the spec ("lightened to keep >= 4.5:1"); the values
  in `tokens.ts` are our derivation, verified by the same test. Alternatives: relax the test (rejected, 19.11).
- **D-008 · 2026-10-21 · Local object store.** The spec names MinIO, but `minio/minio` (Docker Hub) and
  `quay.io/minio/minio` both refused anonymous pulls on 2026-10-21. Local dev/test uses RustFS (S3-compatible)
  pinned by image digest in `docker-compose.yml`, with `amazon/aws-cli` creating private buckets. The API code
  path is unchanged (`core/storage.py`, boto3 path-style). Hosted uses Supabase Storage. Revisit if MinIO
  publishes an official image again. Lifecycle rules are best-effort locally and authoritative on the hosted store.
- **D-009 · 2026-10-21 · Frontend toolchain majors.** Spec 3 names Vite 5; its dev-server advisories (path traversal,
  esbuild dev-server request exposure) and Vitest 2's critical advisories (tinypool, vitest UI) have no fix inside
  those majors, so dev tooling is upgraded to vite 8.3.4, vitest 5.0.5, @vitejs/plugin-react 6.1.2, @types/node 24.
  React 18, TypeScript 5 and Tailwind 3 are unchanged. Remaining `npm audit` highs (braces chain via Tailwind 3) are
  build-time only, listed with an expiry (2026-11-30) in `frontend/scripts/audit-gate.mjs`; runtime deps: 0 findings.
  Alternative considered: Tailwind 4 migration (config format change) - deferred until Phase 2 has components.
- **D-010 · 2026-10-21 · Playwright lives in `e2e/` with its own package.json** (spec layout), not in `frontend/`.
- **D-011 · 2026-10-21 · Gate semantics.** `phase_gate.py` records N/A (nothing to run yet), SKIP (tool missing or
  `--offline`) and FAIL separately; a SKIP fails the gate unless `--offline` is given, and an offline PASS must not
  be reported as a full PASS. `security review` fails only on an `UNRESOLVED-HIGH` table row.
- **D-012 · Phase 0 sign-off blockers (owner actions).** Status 2026-10-21: (a) DB password and secret key rotated,
  R7 and R11 RESOLVED (owner-attested); (b) Render cut over, hosted `/health` and `/health/ready` OK; (c) built-in
  `/security-review` still to run and append; (d) gitleaks and pip-audit pass locally, CI run still pending (nothing pushed).
- **D-013 · 2026-10-21 · CI location.** The git root is `C:\Hackathon\BracU Hackathon` (parent of `cropguardian/`).
  GitHub reads workflows, dependabot and PR templates only from the repository root, so they live in the root
  `.github/` (`cropguardian-ci.yml`, `-deploy.yml`, `-keepwarm.yml`, `dependabot.yml`, `PULL_REQUEST_TEMPLATE.md`) and run
  with `working-directory: cropguardian`. `cropguardian/.github/CODEOWNERS` is inert there; real GitHub handles are
  needed before a root-level CODEOWNERS is useful. Render uses `rootDir: cropguardian/backend`. Alternative: make
  `cropguardian/` its own repository (cleaner, but a history change the owner must decide).
- **D-014 · 2026-10-21 · Dependency security bumps.** FastAPI 0.115.6 -> 0.156.4 and Starlette pinned 1.9.0 (7 advisories);
  Pillow 11.1.0 -> 13.0.0 in `ml/` (25 advisories). `pip-audit` now runs in the gate through `scripts/run_pip_audit.py`,
  which uses the OS trust store when `truststore` is installed (TLS verification stays on).
- **D-015 · 2026-10-21 · Local image builds behind TLS interception.** `make wheelhouse` downloads Linux cp312 wheels on
  the host; the Dockerfile installs from `backend/wheelhouse/` with `--no-index` when it exists, else the normal
  hash-locked/pinned online install. The wheelhouse is gitignored and never exists on Render/CI.
- **D-016 · 2026-10-21 · Render health checks and fail-closed environment.** Found live: a deploy never went live because
  the host allow-list rejected Render's health checks. `/health` and `/healthz` (constant body, no data) are exempt from the
  host check; all other paths stay checked. `RENDER=true` (set by the platform) makes an unset `CG_ENV` default to
  `production` so strict validation runs. Added `RequestLogMiddleware` (method, path without query, status, duration,
  request id; liveness at debug level) because uvicorn's access log is disabled for privacy and rejections were invisible.
- **D-017 · 2026-10-21 · Phase 1 dependency choices.** React Router **7.18.4** instead of 6 (spec 3): 6.30.6 has an open-redirect
  advisory (GHSA-wrjc-x8rr-h8h6, backslash in `<Link>`/`useNavigate`) fixed only in >= 7.18; the data-router API
  (`createBrowserRouter`, lazy routes) is the same. `@hookform/resolvers` pinned to 5.x (6.x has unresolved optional peers).
  Backend test tooling bumped (pytest 9, pytest-asyncio 1.4, hypothesis 6.170) because `schemathesis` 4.x requires pytest 9.
  Dev/test Redis runs with persistence off (read-only root FS made it refuse writes: MISCONF).

- **D-018 - 2026-10-21 - Phase 1 identity choices.** Postgres is the session record and Redis a 60 s read cache (Redis outage = slower, not logged out; auth limits fail closed). Pre-login lookups use a server-only SYSTEM database context that request data cannot produce. Demo users are shared, so demo "sign out everywhere" and the device list touch only the caller's own session. `create_admin.py` does not print a TOTP URI: two-factor enrolment is forced at first sign-in instead (smaller secret exposure). Common-password check = small bundled list plus zxcvbn dictionaries, not a breach corpus. `seed.py` seeds demo users only; the base catalogue needs Phase 4 tables. `idempotency.py` is deferred to Phase 4 (first resource-creating endpoints); `idempotency_keys` only gained a `route` column. Migration 0002 also fixes the Phase 0 audit chain (it restarted at genesis for non-admin writers under RLS; ids now assigned under the chain lock). `p1_smoke.py --insecure-loopback` skips certificate verification for localhost only (same trade-off as `curl -k` in `verify.sh`; this machine's antivirus re-signs local TLS).

- **D-019 - 2026-10-21 - Gate and secret-scan fixes found while closing Phase 0/1.** (1) gitleaks flagged 9 fake test fixtures (generic-api-key) in commit `5f30c79`; they are pinned by exact fingerprint in `.gitleaksignore` (repo root for history, `cropguardian/` for the working tree), never by path glob, so any new finding still fails the gate. The gate now scans `.` from `cropguardian/` so fingerprints are machine-independent. (2) Gate step 9 ran unit tests only against an 85% floor, which Phase 1 code (covered by real-Postgres tests) could no longer meet; it now runs the whole suite when the test Postgres+Redis are up and keeps the same floor for the unit-only fallback. (3) Migration 0003 revokes `anon`/`authenticated` access again and sets default privileges: 0002 revoked function access before creating `audit_tail_hash()`, and Supabase grants new functions to those roles directly, so the function was callable at `/rest/v1/rpc/` (found by the Supabase advisor on the hosted DB). (4) `test_explicit_cg_env_wins_over_render` asserted the pre-Phase-1 behaviour; `CG_ENV=test|development` on Render is now refused and the test says so. (5) `vector` stays in `public` (advisor WARN accepted, see phase-01 review R14).
