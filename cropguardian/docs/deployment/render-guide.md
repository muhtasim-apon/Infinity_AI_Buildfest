# Render deployment guide

Owner: **Apon**. Blueprint: [`../../render.yaml`](../../render.yaml). Limits: [R1] in `docs/research/sources.md`.
Status: **not yet deployed** — this is the procedure.

## 0. Prerequisites
- GitHub repo (private until submission, then public as required).
- Supabase project created and migrated (`db/README.md`), buckets `scans` + `models` created.
- ONNX model uploaded to `models/` bucket (or baked into the image — see §3).
- LLM API key with a spending cap set in the provider console.

## 1. Backend — `cropguardian-api` (Docker, free)
1. Render → New → Blueprint → select repo → it reads `render.yaml`.
2. Fill env group `cropguardian-secrets` (never paste secrets into `render.yaml`).
3. Health check path `/healthz` (fast, no DB). `/readyz` checks DB + model for monitors.
4. Dockerfile essentials (`services/api/Dockerfile`):
   - `python:3.12-slim`, `pip install --no-cache-dir`, non-root user;
   - `CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1` — **bind to `$PORT`**;
   - model downloaded at build time (`ARG MODEL_URL`) **or** at startup to `/tmp` (ephemeral is fine — it is re-downloaded after every restart).
5. Deploy → watch logs for `model loaded sha256=…` and `ready`.

## 2. Frontend — `cropguardian-web` (static, free)
1. Build `npm ci && npm run build`, publish `dist/`.
2. Rewrite `/* → /index.html` so `/admin`, `/audit`, etc. work on refresh.
3. Env `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` (anon only).
4. Security headers from `render.yaml`.

## 3. Where the model lives
| Option | Pros | Cons | Use |
|---|---|---|---|
| Baked into Docker image | no startup download; deterministic | rebuild to change model | **default** if ≤ 30 MB |
| Download from Supabase Storage at boot | swap model without rebuild | adds seconds to cold start; Storage egress | when iterating models |
Never rely on files written at runtime surviving (ephemeral FS [R1]).

## 4. CORS
API allows exactly the static site origin (and `http://localhost:5173` in development).

## 5. Custom domain (optional)
Render free supports custom domains with managed TLS; otherwise use `*.onrender.com`.

## 6. Smoke test after each deploy
`GET /healthz` 200 → `GET /readyz` 200 → demo session → scan a fixture image → advice returned
with ≥ 1 citation → `/audit` renders. Automated as n8n workflow `05-synthetic-monitor`.

## 7. Rollback
Render dashboard → service → Events → previous successful deploy → Rollback. Model rollback:
`/admin` → model versions → activate previous (no deploy needed if download-at-boot; otherwise rollback deploy).
