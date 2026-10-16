# Render guide — prototype, web app and API on the free tier

Owner: **Apon**. Order of work: [`00-zero-to-deploy.md`](00-zero-to-deploy.md) Phase 8. Everything that
can go wrong on the free tier and how to recover: [`04-free-tier-challenges.md`](04-free-tier-challenges.md).
Facts cite `docs/research/sources.md` ([R1] free tier, [R3] Docker, [R4] Blueprint spec, [R9] custom domains).

## 1. What the free tier gives us (and why the design looks like this)
| Fact | Consequence for Crop Guardian |
|---|---|
| Free **web services** spin down after 15 min without inbound traffic; spin-up ≈ 1 min [R1] | frontends are **static sites** (they never sleep); the web app shows "waking server"; keep-warm during demo windows |
| 750 free instance-hours per workspace per month; when used up **all free web services are suspended** until next month [R1] | exactly **one** free web service (the API); static sites use no instance hours |
| Filesystem is ephemeral; no persistent disk; single instance; may restart any time [R1] | API is stateless; data in Supabase; model downloaded at boot |
| Free Render Postgres expires after 30 days [R1] | we use Supabase instead (ADR 0003) |
| Bandwidth over the included amount with no payment method → **all free services suspended** for the month; build minutes over → **builds disabled** for the month [R1] | compress images client-side; cache static assets; avoid unnecessary redeploys |
| Render **may suspend a free web service for unusually high outbound traffic** (calls to external DBs/APIs/object storage) [R1] | cache advice; small DB pool; no load tests against production; moderate monitors |
| Outbound SMTP ports 25/465/587 blocked [R1] | email via provider HTTP APIs / Supabase Auth only |
| Docker env vars are passed to `docker build` as build args [R3] | no secrets read in the Dockerfile; model fetched at runtime |

## 2. Services we create
| Service | Type | Root directory | Build | Publish / start | Plan |
|---|---|---|---|---|---|
| `cropguardian-prototype` | Static site | `prototype` | `echo static` | publish `.` | free (no plan field) |
| `cropguardian-web` | Static site | `apps/web` | `npm ci && npm run build` | publish `dist` | free |
| `cropguardian-api` | Web service, Docker | `services/api` | Dockerfile | container CMD binds `$PORT` | **Free** |

## 3. Create the prototype site (day 1, no code needed)
1. dashboard.render.com → **New → Static Site** → connect GitHub → select the repo.
2. Name `cropguardian-prototype` · Branch `main` · Root Directory `prototype` · Build Command
   `echo static` · Publish Directory `.` → **Create Static Site**.
3. Open the service → **Redirects/Rewrites** → add rules in §4 → Save.
4. **Headers** → add the headers in §6 (path `/*`).
5. Copy the URL (e.g. `https://cropguardian-prototype.onrender.com`) into the URL plan.

## 4. Rewrite rules
**Prototype** (Congress-style routes → the static pages):

| Source | Destination | Action |
|---|---|---|
| `/app` | `/app.html` | Rewrite |
| `/demo-user` | `/demo-user.html` | Rewrite |
| `/demo-admin` | `/demo-admin.html` | Rewrite |
| `/admin` | `/admin.html` | Rewrite |
| `/data` | `/data.html` | Rewrite |
| `/security` | `/security.html` | Rewrite |
| `/architecture` | `/architecture.html` | Rewrite |
| `/presentation` | `/presentation.html` | Rewrite |
| `/pitchdeck` | `/pitchdeck.html` | Rewrite |
| `/audit` | `/audit.html` | Rewrite |

**Web app** (single-page app): `/*` → `/index.html` (Rewrite) so deep links like `/audit` load after a refresh.

## 5. Create the API service
1. **New → Web Service** → repo → Name `cropguardian-api` → Language **Docker** → Root Directory
   `services/api` → Dockerfile path `./Dockerfile` → Instance Type **Free** → region nearest the
   Supabase region (Singapore if available).
2. **Health Check Path** `/healthz` (fast, no DB — so a cold start passes quickly).
3. **Environment** → add variables. Secrets are typed here once and never committed:

| Variable | Secret? | Value / source |
|---|---|---|
| `ENVIRONMENT` | no | `production` (turns off `/docs` — debug off in prod) |
| `APP_BASE_URL` | no | web app URL (U2) — the **only** CORS origin |
| `WEB_CONCURRENCY` | no | `1` |
| `SUPABASE_URL` | no | project URL (U4) |
| `SUPABASE_SECRET_KEY` | **yes** | `sb_secret_…` |
| `SUPABASE_JWKS_URL` | no | `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json` |
| `DATABASE_URL` | **yes** | Supabase **pooler** string (IPv4) |
| `ANTHROPIC_API_KEY` | **yes** | from the Anthropic Console (spend cap set) |
| `TURNSTILE_SECRET_KEY` | **yes** | Cloudflare Turnstile secret |
| `N8N_WEBHOOK_SECRET` | **yes** | random 32+ bytes; same value in n8n and GitHub secrets |
| `N8N_ALERT_WEBHOOK_URL` | no | n8n webhook (U5) |
| `MODEL_NAME`, `MODEL_PATH` | no | `crop-disease-classifier`, `/tmp/models/classifier.int8.onnx` |
| other tunables | no | as in `.env.example` |

4. **Create Web Service** → watch **Logs**: image build → "model loaded sha256=…" → health check passes.
5. Test: `curl https://<api>/healthz` and `https://<api>/readyz`; `https://<api>/docs` must be **404** in production.

## 6. Security headers (static sites → Headers tab, path `/*`)
| Header | Value |
|---|---|
| `Content-Security-Policy` (web app) | `default-src 'self'; img-src 'self' data: blob: https://*.supabase.co https://*.tile.openstreetmap.org; connect-src 'self' <API URL> https://*.supabase.co https://challenges.cloudflare.com; script-src 'self' https://challenges.cloudflare.com; frame-src https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; frame-ancestors 'none'` |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `X-Frame-Options` | `DENY` |
| `Permissions-Policy` | `camera=(self), geolocation=(self), microphone=()` |

The API sets its own headers in code (spec: `security/headers.py`). Verify with securityheaders.com.

## 7. Create the web app site
Static Site → Root Directory `apps/web` → Build `npm ci && npm run build` → Publish `dist` →
Environment: `VITE_API_BASE_URL` (U3), `VITE_SUPABASE_URL` (U4), `VITE_SUPABASE_PUBLISHABLE_KEY`,
`VITE_TURNSTILE_SITE_KEY` — all **public** (compiled into the bundle; never put a secret in `VITE_*`) →
rewrite `/*` → `/index.html` → headers from §6. Changing a `VITE_*` value needs a **redeploy**.

## 8. Blueprint template (`render.yaml`, optional — write it after the services work)
Reference shape (fill in when creating the file at the repository root):
```yaml
services:
  - type: web            # prototype
    name: cropguardian-prototype
    runtime: static
    rootDir: prototype
    buildCommand: echo static
    staticPublishPath: .
    routes:
      - { type: rewrite, source: /app, destination: /app.html }   # …one per route in §4
  - type: web            # web app
    name: cropguardian-web
    runtime: static
    rootDir: apps/web
    buildCommand: npm ci && npm run build
    staticPublishPath: dist
    routes: [ { type: rewrite, source: /*, destination: /index.html } ]
    envVars:
      - { key: VITE_SUPABASE_PUBLISHABLE_KEY, sync: false }
  - type: web            # API
    name: cropguardian-api
    runtime: docker
    plan: free
    rootDir: services/api
    healthCheckPath: /healthz
    envVars:
      - fromGroup: cropguardian-config
      - { key: SUPABASE_SECRET_KEY, sync: false }   # secrets: sync:false on the SERVICE
envVarGroups:
  - name: cropguardian-config                       # non-secret values only
    envVars:
      - { key: ENVIRONMENT, value: production }
```
Rules [R4]: static sites take no `plan`; **environment groups cannot contain `sync: false` values**
(put secrets on the service); the file must be at the repository root.

## 9. Deploys, rollback, logs
- Auto-deploy on push to `main`. Each deploy is listed under **Events**; **Rollback** redeploys a previous
  build without rebuilding (useful when build minutes are exhausted).
- **Deploy hook** (Settings) gives a URL to trigger a deploy from CI or n8n — keep it secret.
- **Logs** tab: live logs; **Metrics**: CPU, memory, bandwidth — check memory after each model change.
- **Manual restart** (Settings) re-downloads the model after activating a new version.
- Render emails **usage alerts** when you approach a free-tier limit — route those emails to the team.

## 10. Custom domain (recommended)
Service → Settings → **Custom Domains** → add `app.<domain>` (web), `api.<domain>` (API),
`demo.<domain>` (prototype) → add the CNAME records Render shows at your DNS provider → TLS is issued and
renewed automatically. The Hobby workspace includes 2 custom domains; more are billed per month.
Once a custom domain works you may disable the `onrender.com` subdomain (requests to it then return
404) [R9]. After switching, update every place in the URL plan (CORS, Supabase redirects, Turnstile
hostnames, CSP, monitors, submission).

## 11. Checklist before calling Render "done"
- [ ] U1 routes all load on a phone, logged out.
- [ ] U3 `/healthz` 200; `/readyz` 200; `/docs` 404.
- [ ] U2 loads, deep link `/audit` works after refresh, CAPTCHA widget appears on `/demo-user`.
- [ ] CORS: a request from another origin gets no `Access-Control-Allow-Origin`.
- [ ] Headers grade checked; HTTPS only — open `http://` versions of U1–U3 and confirm they end on `https://`
      (HSTS header then keeps browsers on HTTPS).
- [ ] No secret in the repository, the web bundle, or build logs.
- [ ] Usage alert emails reach the team; keep-warm only during demo windows.
