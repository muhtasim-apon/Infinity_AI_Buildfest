# Render guide — the API web service, exact settings

Owner: **Apon**. Used by [00](00-zero-to-deploy.md) Step 5. Free. Facts: [R1], [R3] in
[`sources.md`](../research/sources.md). **Only the API is on Render** — the prototype and the web app
are on Vercel ([05 Vercel guide](05-vercel-guide.md)).

**Repository layout:** our GitHub repo (`Infinity_AI_Buildfest`) has the project inside a
`cropguardian/` folder, so every Root Directory starts with `cropguardian/`. Setting just `api` gives
*"Root directory does not exist"*.

**Remember:** the free API **sleeps after 15 min** without traffic and takes about a minute to wake [R1]
— the UptimeRobot monitor (00 Step 8) prevents that. Only **one** free web service fits in the monthly
750 hours, so never create a second free web service.

Live: `https://cropgurdian-backend.onrender.com` (the name Render gave — keep using it).

## 1. API web service
Render → **New → Web Service** → repository → settings:

| Field | Value |
|---|---|
| Name | `cropguardian-api` |
| Language | **Docker** |
| Root Directory | `cropguardian/services/api` |
| Instance Type | **Free** |
| Region | Singapore (closest to the Supabase region) |
| Health Check Path | `/healthz` |

**Environment** tab — type these once (secrets never go in files or GitHub):

| Key | Value | Secret |
|---|---|---|
| `ENVIRONMENT` | `production` (turns off `/docs`) | |
| `APP_BASE_URL` | the Vercel web app URL, exact, no trailing slash (CORS) | |
| `WEB_CONCURRENCY` | `1` | |
| `SUPABASE_URL` | Supabase project URL | |
| `SUPABASE_JWKS_URL` | `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json` | |
| `SUPABASE_SECRET_KEY` | `sb_secret_…` | ✅ |
| `DATABASE_URL` | Supabase **pooler** connection string | ✅ |
| `ANTHROPIC_API_KEY` | from Anthropic Console | ✅ |
| `TURNSTILE_SECRET_KEY` | from Cloudflare Turnstile | ✅ |
| `MODEL_NAME` / `MODEL_PATH` | `crop-disease-classifier` / `/tmp/models/classifier.int8.onnx` | |

Other values use the defaults in [`.env.example`](../../.env.example).
The Dockerfile must not read any secret: Render passes environment variables into the Docker build [R3].

**Check:** `/healthz` → 200 · `/readyz` → 200 (after Step 7 it also shows the model) · `/docs` → 404 ·
`curl.exe -I .../readyz` → 200 (HEAD works, so UptimeRobot stays green).

## 2. Security headers
The API sets its own headers in code. The frontends' headers (HSTS, CSP, …) are in their `vercel.json`
files ([05](05-vercel-guide.md)). Check the grade on securityheaders.com.

## 3. Day-to-day
- Every push to `main` deploys automatically. Merge in small batches (free build minutes are limited [R1]).
- **Rollback:** service → Events → previous deploy → Rollback (no rebuild needed).
- **Restart** (Settings → Manual restart) after activating a new model.
- Read Render's usage-alert emails — they warn before a free limit is hit.

## 4. Done checklist
- [ ] API: `/healthz` 200, `/readyz` 200 (GET and HEAD), `/docs` 404.
- [ ] `APP_BASE_URL` = the Vercel web URL; no CORS errors in the web app.
- [ ] `http://` URLs end up on `https://`.
- [ ] No secret in GitHub or in build logs.
