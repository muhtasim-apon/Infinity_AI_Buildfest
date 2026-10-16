# Render guide — 3 services, exact settings

Owner: **Apon**. Used by [00](00-zero-to-deploy.md) Steps 3, 5 and 6. All free. Facts: [R1], [R3] in
[`sources.md`](../research/sources.md).

**Remember:** the free API **sleeps after 15 min** without traffic and takes about a minute to wake [R1]
— the UptimeRobot monitor (00 Step 8) prevents that. Only **one** free web service fits in the monthly
750 hours, so never create a second free web service. Static sites don't sleep and don't use hours.

## 1. Prototype static site
Render → **New → Static Site** → repository → settings:

| Field | Value |
|---|---|
| Name | `cropguardian-prototype` |
| Branch | `main` |
| Root Directory | `prototype` |
| Build Command | `echo static` |
| Publish Directory | `.` |

Then **Redirects/Rewrites** → add each as **Rewrite**:
`/app → /app.html` · `/demo-user → /demo-user.html` · `/demo-admin → /demo-admin.html` ·
`/admin → /admin.html` · `/data → /data.html` · `/security → /security.html` ·
`/architecture → /architecture.html` · `/presentation → /presentation.html` ·
`/pitchdeck → /pitchdeck.html` · `/audit → /audit.html`.

## 2. API web service
Render → **New → Web Service** → repository → settings:

| Field | Value |
|---|---|
| Name | `cropguardian-api` |
| Language | **Docker** |
| Root Directory | `services/api` |
| Instance Type | **Free** |
| Region | Singapore (closest to the Supabase region) |
| Health Check Path | `/healthz` |

**Environment** tab — type these once (secrets never go in files or GitHub):

| Key | Value | Secret |
|---|---|---|
| `ENVIRONMENT` | `production` (turns off `/docs`) | |
| `APP_BASE_URL` | the web app URL | |
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

**Check:** `/healthz` → 200 · `/readyz` → 200 (after Step 7 it also shows the model) · `/docs` → 404.

## 3. Web app static site
Render → **New → Static Site** → settings:

| Field | Value |
|---|---|
| Name | `cropguardian-web` |
| Root Directory | `apps/web` |
| Build Command | `npm ci && npm run build` |
| Publish Directory | `dist` |
| Rewrite | `/*` → `/index.html` (so page refreshes work) |

**Environment** (all public — they end up in the browser, so never a secret here):
`VITE_API_BASE_URL` = API URL · `VITE_SUPABASE_URL` · `VITE_SUPABASE_PUBLISHABLE_KEY` ·
`VITE_TURNSTILE_SITE_KEY`. After changing any of them, click **Manual Deploy** (they are baked in at build).

## 4. Security headers (both static sites → Headers tab, path `/*`)
| Header | Value |
|---|---|
| `Strict-Transport-Security` | `max-age=31536000` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Content-Security-Policy` (web app only) | `default-src 'self'; img-src 'self' data: blob: https://*.supabase.co https://*.tile.openstreetmap.org; connect-src 'self' <API URL> https://*.supabase.co https://challenges.cloudflare.com; script-src 'self' https://challenges.cloudflare.com; frame-src https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; frame-ancestors 'none'` |

The API sets its own headers in code. Check the grade on securityheaders.com.

## 5. Day-to-day
- Every push to `main` deploys automatically. Merge in small batches (free build minutes are limited [R1]).
- **Rollback:** service → Events → previous deploy → Rollback (no rebuild needed).
- **Restart** (Settings → Manual restart) after activating a new model.
- Read Render's usage-alert emails — they warn before a free limit is hit.

## 6. Done checklist
- [ ] Prototype: all 10 routes open on a phone.
- [ ] API: `/healthz` 200, `/readyz` 200, `/docs` 404.
- [ ] Web: loads; refreshing `/audit` works; CAPTCHA shows on `/demo-user`; no CORS errors.
- [ ] `http://` URLs end up on `https://`.
- [ ] No secret in GitHub, in the web bundle, or in build logs.
