# Deployment (hosted public demo + local stacks)

Status 2026-10-21: **hosted skeleton is the OLD starter** (`services/api`), not yet the new `backend/`.
Nothing below claims a measurement that was not taken; observed vs. unverified is marked.

## Live endpoints (user-supplied)
| What | URL | Observed 2026-10-21 |
|---|---|---|
| Prototype (static, Vercel) | https://infinityaibuildfest-prototype-five.vercel.app/ | HTTP 200 |
| API (Render, Docker, free) | https://cropgurdian-backend.onrender.com | `/health` → **404** (starter exposes `/healthz` and `/readyz`); response in ~0.44 s (warm) |

Note the spelling `cropgurdian` (sic) in the Render hostname; keep it consistent in CORS/TRUSTED_HOSTS.

## Topology (spec 5.2)
Vercel/Render static (SPA) → rewrite `/api/*` → Render Docker API (1 free instance, `JOBS_MODE=inprocess`) →
Supabase Postgres (transaction pooler 6543, `statement_cache_size=0`) + Supabase Storage (S3 endpoint, private
buckets) + Render Key Value (Redis). Keep-warm: GitHub Actions `keepwarm.yml` and/or UptimeRobot on `/health/ready`.

## Cut-over of the API from `services/api` to `backend/` (P0 step 8) — NOT yet done
1. Rotate secrets first (an earlier `.env.example` carried a weak DB password and a Supabase secret key): Supabase
   → reset DB password and create a new secret key, delete the old; update Render env vars; verify `/readyz`.
2. Render service → Settings: **Root Directory** `cropguardian/backend` (the git root is the *parent* folder of `cropguardian/`), Dockerfile `./Dockerfile`, health check path `/health`, **Branch** = the branch you pushed. Render builds with Docker, so `backend/wheelhouse/` (gitignored) is absent there and the normal online install runs.
3. Environment (Render dashboard, never in git): `CG_ENV=production`, `SECRET_KEY` (≥ 32 random chars),
   `DATABASE_URL` (Supabase **transaction pooler** string; write `$` as `%24`), `APP_BASE_URL` (https), `TRUSTED_HOSTS`
   (JSON list including the onrender hostname), `CORS_ORIGINS` (JSON list; only while SPA and API differ in origin),
   `JOBS_MODE=inprocess`, `METRICS_TOKEN`, S3 vars, `REDIS_URL` (Key Value internal URL).
   Production startup **refuses** insecure combinations (see `backend/app/core/config.py` and its tests).
4. Run migrations once with the *migrator* connection: `MIGRATION_DATABASE_URL=... make migrate`
   (Supabase: the connecting user must be able to `GRANT` membership of `cg_app/cg_worker/cg_readonly`; the
   migration logs a NOTICE and continues if it cannot — then grant manually and re-check `check_rls.py`).
5. Deploy, then `curl -i https://cropgurdian-backend.onrender.com/health` → 200 with the security headers.
   Update UptimeRobot from `/readyz` to `/health/ready` (the legacy `/healthz`, `/readyz` aliases remain for now).
6. **Verify the `/api/*` rewrite to an external origin works, including SSE** (Render static or Vercel). If the platform
   buffers or refuses it, set `SERVE_SPA=true` and serve the SPA from the API container; record an ADR in DECISIONS.md.
   (Not yet verified — the SPA is a placeholder and no SSE endpoint exists before Phase 4.)


## Render service `cropgurdian_backend` — inspected via MCP on 2026-10-21 (read-only)
Service `srv-db933ae7bikc73bplnng`, workspace "My Workspace" (also holds unrelated services Abhijatri, EduHub, SHETU — never touch them).
Observed: Docker, free plan, Singapore, 1 instance, branch `main`, Root Directory `cropguardian/backend`, Dockerfile `./Dockerfile`,
auto-deploy on every commit, health check path `/healthz`. No Key Value instance exists. Memory of the new instance ~97 MB of 512 MB.

**Incident found:** after the Root Directory change the new deploy built successfully and the instance started, but the deploy stayed
`update_in_progress` and traffic kept going to the old starter (`/health` 404). The new instance logged **no** health-check requests:
the host-header allow-list (localhost only, because `CG_ENV` was unset and the app defaulted to `development`) rejected the platform's
health checks with 400. Fixed in code (DECISIONS D-016): liveness paths are exempt from the host check, and on Render an unset
`CG_ENV` now means production (the service refuses to start without a real `SECRET_KEY`, https `APP_BASE_URL` and `DATABASE_URL`).

### Environment variables to set on the service (names; values in the Render dashboard)
| Name | Value | Secret? |
|---|---|---|
| `CG_ENV` | `production` | no |
| `SECRET_KEY` | 64 random hex chars (`python -c "import secrets;print(secrets.token_hex(32))"`) | **yes** |
| `DATABASE_URL` | Supabase **transaction pooler** URI (port 6543), `$` written as `%24` | **yes** |
| `APP_BASE_URL` | `https://infinityaibuildfest-prototype-five.vercel.app` | no |
| `TRUSTED_HOSTS` | `["cropgurdian-backend.onrender.com"]` | no |
| `CORS_ORIGINS` | `["https://infinityaibuildfest-prototype-five.vercel.app"]` (only while the SPA is on another origin) | no |
| `JOBS_MODE` | `off` until a Redis exists, then `inprocess` | no |
| `LOG_LEVEL` | `info` | no |
| `METRICS_TOKEN` | random 24+ chars (only if you want `/metrics` externally; otherwise leave unset = hidden) | **yes** |
Remove obsolete starter variables that the new app ignores (`ENVIRONMENT`, `SUPABASE_*`) once nothing else uses them.

### Dashboard settings (the MCP cannot change these)
- Health Check Path: `/health` (the legacy `/healthz` alias still works).
- Auto-Deploy: change from "On commit" to **"After CI checks pass"** so a red build never deploys.
- Build Filters: only `cropguardian/backend/**` (so a docs-only push does not redeploy).
- Pre-Deploy Command (paid plans only): not available on free; run migrations from your machine with `make migrate`.

## Local stacks
- Dev: `make env certs up` → `https://localhost` (Nginx TLS, API, Postgres+pgvector, Redis, RustFS S3). `make down`.
- Test DB for gates: `make test-db` (Postgres + Redis on localhost ports 55432/56379, tmpfs).
- Production reference: `make up-prod` (api ×3 behind Nginx `least_conn`, worker ×2).
- Edge checks: `bash infra/nginx/verify.sh [https_base] [http_base]` (16 assertions; run against any Nginx front).
- **Behind TLS interception** (this laptop re-signs HTTPS, so pip inside Docker and Python `requests` fail verification):
  run `make wheelhouse` once (downloads Linux wheels on the host), then `make up`; for `pip-audit` install `truststore`
  (the gate's wrapper uses the OS certificate store). Never disable verification.
- **Recreating the API**: `make up` / `docker compose up -d` (all services) or `docker compose restart api` restart Nginx
  too (`depends_on.restart`). `docker compose up -d --force-recreate api` alone does **not**, and Nginx would keep the
  old address (504).
- Local object store is RustFS (DECISIONS D-008); buckets `scans`, `models`, `exports`, `backups` are private (anonymous
  requests get 403, verified).
- Windows Git Bash rewrites `/tmp` in `docker run` flags; use `MSYS_NO_PATHCONV=1`.

## Production-mode rehearsal (done locally, 2026-10-21)
The built API image was started with Render-style settings (`CG_ENV=production`, `PORT=10000`, Render hostname in
`TRUSTED_HOSTS`, prototype origin in `CORS_ORIGINS`, read-only root FS, all capabilities dropped, non-root user):
`/health` 200 with the four checked security headers; `/health/ready` `{"db":"ok"}` against Postgres; `/docs` and
`/openapi.json` 404; unknown Host 400; CORS header only for the prototype origin; **insecure settings
(`SECRET_KEY=change-me`, http base URL) make the container exit with code 3**. This is a rehearsal, not the hosted result.

## Free-tier limits
Do not trust numbers from memory. The team's sourced claims live in `docs/research/sources.md` (R1, R2: 15-minute
spin-down, instance hours, ephemeral disk, Supabase one-week pause, 500 MB). Anything **observed** on our own
instances (cold-start seconds, memory at startup, Key Value limits) must be recorded here with date and method:

| Observation | Value | Date | How measured |
|---|---|---|---|
| API warm `/health` latency (old starter, 404) | ~0.44 s | 2026-10-21 | single `curl` from the dev laptop |
| New API image, local production-mode start to healthy | ~7 s | 2026-10-21 | `docker run` + polling, no model loaded yet (not a Render number) |
| API cold start | _not measured_ | | |
| API RSS at startup | _not measured_ (Phase 4, with the ONNX models) | | |
| Render Key Value free limits | _not verified_ | | |
| Supabase region | _not recorded_ — owner to add | | |

## Backups and restore (spec 22.3)
`make backup` / `make restore-drill` are Phase 12 targets and currently stubs. Before demo day: `pg_dump` of the
Supabase DB with the migrator connection, encrypted, and a restore into a scratch project.
