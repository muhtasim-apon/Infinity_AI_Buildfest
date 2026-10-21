# Plan: Apon, Sat 17 Oct (day 1/13) — Phase 0 "Foundations, tooling, infrastructure" (M1)

## Context
The Gantt PDF (17–29 Oct) makes `CROP_GUARDIAN_BUILD_SPEC.md` the baseline (spec wins over `docs/`; n8n, Leaflet, Supabase-Auth-only and automatic un-reviewed alerts are dropped). Apon's track is P0 → P1 → P4 → P8 → P11 → P12. The user wants **only the 17 Oct task implemented now**, then 18 → 23 Oct one day at a time.
Today is 21 Oct, so this is catch-up. Do P0 first; later days only after P0's gate passes. All 17 Oct prompts (Apon, Taeen, Salwa, Raisa, Sara) are merged into the one master prompt below; only Apon's day-1 work is implemented here.

## Verified current state (read-only checks)
- Repo has docs, a static prototype and a 2-endpoint starter API (`cropguardian/services/api/app/main.py`: `/healthz`, `/readyz`). **No** PROGRESS.md, DECISIONS.md, Makefile, backend/, frontend/, infra/, `.claude/skills/`, `.github/workflows`, Alembic or tests.
- Live: Vercel prototype returns 200. Backend `https://cropgurdian-backend.onrender.com`: `/health` → **404** (spec gate requires `/health` 200; only `/healthz` and `/readyz` exist).
- `cropguardian/CLAUDE.md` says "no human-review features" — contradicts the spec. Must be replaced (≤ 60 lines).
- **Supabase MCP in this session points at a different project** (tables destinations/reviews/guest_visits). Do not write to it. Re-point before any MCP DB work.
- Render MCP needs a workspace chosen by the user; Vercel MCP shows no teams (personal account).
- An earlier `.env.example` once held a Supabase secret-key placeholder/weak DB password (per deploy notes): rotate DB password + secret key (Supabase dashboard → Render env) as step 0.

## Decisions to record in DECISIONS.md / ADR
1. Layout: build the spec §4 tree (`backend/`, `frontend/`, `infra/`, `kb/`, `e2e/`) under `cropguardian/` as repo root. Keep `services/api` + `apps/web` running untouched so Render/UptimeRobot stay green; cut Render over to `backend/` at the end of P0 once `/health` passes (spec §5.2 ADR: verify Render `/api/*` rewrite incl. SSE, else `SERVE_SPA=true`).
2. Judging-rubric version (6 × weighted vs 5 × 20) → record per spec §23.
3. Hosted DB uses Supabase transaction pooler (6543), `statement_cache_size=0`.

## Order of work (each step ends with a small commit; PR to main at end of day)
1. **Docs/skeleton:** `CLAUDE.md` (≤60 lines, from spec §0.2), `PROGRESS.md`, `DECISIONS.md`, `.editorconfig`, `.gitignore`, `.phase`, CODEOWNERS (spec §0.5), PR template, `docs/plans/phase-00.md` (copy of this plan), docs stubs.
2. **Skills:** `.claude/skills/` — install/review frontend-design, webapp-testing, skill-creator, pdf, pptx, threejs-skills (read every SKILL.md first, record commit hashes in DECISIONS.md + `.claude/skills/README.md`); author `cropguardian-safety` (spec §0.2, §16.22, §19.8).
3. **Backend core** (`backend/`): `pyproject.toml` (ruff, mypy strict for core/domain, pytest `--strict-markers`, coverage), hashed locks; `core/config.py` (all §6.1 vars, production refuses insecure combos), `logging.py` (structlog + redaction), `errors.py` (problem+json), `clock.py`, `http.py` (allow-list client + circuit breaker), `storage.py` (presigned POST/PUT/GET), `db/` (async engine, `SET LOCAL ROLE`, naming conventions), app factory with §16.9 middleware order, `/health`, `/health/ready`, `/metrics`, `jobs` (arq `ping`, `JOBS_MODE`, cron lock).
4. **Alembic + first migration:** extensions (`vector`), roles/grants (`infra/postgres/init` for compose; migration for Supabase), `platform_settings` (seeded + validated), `audit_log` (append-only trigger + hash chain), `jobs_log`, `idempotency_keys`, `client_errors`. Verify up/down/up.
5. **Infra:** Nginx (TLS via mkcert, 80→443, exact CSP in `security-headers.conf`, `limit_req`, body limits, timeouts, least_conn upstream, TRACE blocked, internal-only `/metrics` + `/health/ready`); compose dev/test/prod (non-root, read-only FS, `no-new-privileges`, cap drop, limits, healthchecks); MinIO private buckets.
6. **Scripts + gate:** `phase_gate.py` (runs steps on whatever exists, writes `runs/gates/phase-0.json`, appends PROGRESS.md), `check_forbidden.py`, `check_layers.py`, `check_rls.py`, `check_honesty.py`, `export_openapi.py`; `.pre-commit-config.yaml`; Makefile (§19.7); CI workflows `ci.yml`, `keepwarm.yml`, `deploy.yml`, `dependabot.yml`.
7. **Frontend skeleton** (`frontend/`): Vite + React + TS strict, Tailwind token placeholder, self-hosted fonts, ESLint/Prettier, Vitest/RTL/MSW, Playwright config + smoke test, CSP-compat test (no inline scripts/styles in `dist/index.html`).
8. **Hosted skeleton:** `infra/render.yaml` (static + Docker web, Key Value), Supabase project region recorded, `/api/*` rewrite verified (or `SERVE_SPA` ADR), keep-warm workflow, `docs/DEPLOYMENT.md` with observed free-tier limits. Cut over Render to `backend/`, confirm hosted `/health` 200.
9. **Security review + gate:** `/security-review` on the day's diff → `docs/security-reviews/phase-00.md`; run `make gate PHASE=0`.

## Security controls (spec §16.21 row 0)
Config validation + prod refusal; secrets via env only; gitleaks/Bandit/Semgrep/pip-audit/npm audit/Trivy wired in; Dependabot; non-root read-only containers; Nginx TLS, redirect, exact CSP, body limits, TRACE blocked; forbidden/layer/honesty scanners; audit hash chain. Corner cases: none for P0.

## Tests (by layer; all include invalid input / failure paths)
Config defaults/overrides/insecure-prod refusal · log redaction (token/password/otp/phone/lat) · error handler hides traces · health endpoints · audit append-only + hash chain · settings validation (min_reports ≤ high_reports, bounds) · Nginx: redirect, exact headers, TRACE blocked, oversize 413, `/metrics` unreachable externally · storage anonymous access denied · frontend smoke + token contrast.

## Exit check / acceptance
`make gate PHASE=0` → `PHASE 0 GATE: PASS`; `curl -k https://localhost/health` → 200 with headers; hosted `/health` → 200; M1 reached. If Docker/mkcert unavailable on this machine, report PARTIAL honestly, never fake a pass. Then append one line to PROGRESS.md (DONE/PARTIAL/BLOCKED + reason), commit `phase-0: …`, tag `phase-0`, stop and wait for "continue".

## Master Plan Prompt (the merged 17 Oct prompt; paste into Claude Code after `/clear` + Shift+Tab)
> I am Apon (lead / backend / DB / deploy). Today is Sat 17 Oct 2026 (day 1 of 13). Read CROP_GUARDIAN_BUILD_SPEC.md §0 and Phase 0 of §20, then only §0, §3–§6, §16.3, §16.14, §16.18, §17.3–17.6, §19. Load skill-creator. Scope: Finish P0 foundations (M1) as in the "Order of work" above. Produce a written plan, save to docs/plans/phase-00.md, show ≤15 lines and WAIT. After approval implement exactly (deviations → DECISIONS.md). Honesty rules §0.2.6 and fail-closed apply. End of day: run phase checks, /security-review, small PR to main, one line in PROGRESS.md. Exit check: make gate PHASE=0 → PASS; hosted /health 200; M1 reached.

Team parallel starts the same day (inputs, not implemented here): Taeen P3 datasets+EDA (`cg_ml` skeleton); Salwa P5 `kb/sources.yaml` + licences; Raisa P2 `docs/BANGLA_STYLE.md` + bn.json keys; Sara P2 cropguardian-ui skill + tokens.

## Sequence after today (one day each, same prompt pattern from the PDF)
18 Oct P1 models + RLS + core security → 19 Oct P1 auth endpoints, start P4 → 20 Oct P4 scan API + inference service → 21 Oct P4 vertical slice (M2) → 22 Oct P8 review loop/outbreak rules → 23 Oct P8 engine/weather/alert approval. Given today's date these slip ≥ 4 days; apply the spec cut order and re-baseline then.

## MCP server suggestions (Claude Code CLI; run in your terminal, not via me)
- **Already connected in this session:** Render, Supabase, Vercel, Railway, Chrome. Check with `/mcp`.
- **Supabase (fix scope):** `claude mcp add --transport http supabase "https://mcp.supabase.com/mcp?project_ref=<CG_PROJECT_REF>&read_only=true"`, then `/mcp` → authenticate. Start read-only; use `get_advisors` after every migration.
- **Render:** `claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer <RENDER_API_KEY>"`; tell me the workspace to select. Use for logs, deploys, env vars.
- **Vercel:** `claude mcp add --transport http vercel https://mcp.vercel.com` then `/mcp` login. Use for deployments/runtime logs of `infinityaibuildfest-prototype-five.vercel.app`.
- **GitHub (CI/PRs):** `claude mcp add --transport http github https://api.githubcopilot.com/mcp/ --header "Authorization: Bearer <PAT>"` or just use `gh`.
- **Playwright (E2E/screenshots):** `claude mcp add playwright -- npx @playwright/mcp@latest`.
- Use `--scope project` (writes `.mcp.json`) only for servers without secrets; keep tokens in user scope or env vars, never committed. Review every server's tool list; prefer read-only.

## Verification (end-to-end)
`make env certs up` → `https://localhost` loads, Noto Sans Bengali + Inter, no console errors, no external requests; `make gate PHASE=0`; `curl https://cropgurdian-backend.onrender.com/health` → 200 after cutover; `curl -I` on hosted URL shows security headers; Vercel prototype still 200; UptimeRobot monitor green.

---
## Execution record — 17 Oct work, executed 2026-10-21 (appended)
Built exactly the nine ordered steps except where noted. Deviations are in DECISIONS.md (D-007 … D-012).
- Done and verified locally: docs skeleton, skills (reviewed, hashes pinned), backend core + tests, Alembic 0001 on real
  Postgres (RLS, append-only, hash chain, seed), Nginx edge (16/16 checks), compose dev/test/prod files, scripts + gate,
  CI workflows, frontend skeleton (build, CSP check, 63 tests, Chromium smoke).
- Not done / blocked: hosted cut-over and hosted `/health` (needs deploy; no push by instruction), full API image build
  on this machine (TLS interception), gitleaks and pip-audit (tool/network), `/security-review` command, Supabase
  credential rotation (owner).
- Corrections to this plan found during execution: object store changed from MinIO to RustFS (D-008); Playwright moved to
  `e2e/` (D-010); dev toolchain majors upgraded for security (D-009).
