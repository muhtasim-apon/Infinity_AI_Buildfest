# Zero to deployment — the complete order of work

From an empty laptop to every public URL live. Follow the phases in order; each phase lists the
**owner**, the **Gantt day**, the **steps**, the **expected result** and **if it fails**.
Platform details: [Render](01-render-guide.md) · [Supabase](02-supabase-guide.md) ·
[other platforms](03-other-platforms-guide.md) · [free-tier challenges & recovery](04-free-tier-challenges.md) ·
security: [checklist](../security/security-checklist.md) · [security testing](../testing/security-testing-guide.md).

> This repository is a **template** — specs, not code. Phases 4–8 assume the team has written the code
> from [`services/api/SPEC.md`](../../services/api/SPEC.md), [`apps/web/SPEC.md`](../../apps/web/SPEC.md)
> and [`db/SCHEMA-SPEC.md`](../../db/SCHEMA-SPEC.md). Phase 8.1 (prototype) works **today**.

---

## The URL plan (decide once, paste everywhere)

| # | What | URL (default free subdomains) | Created in | Pasted into |
|---|---|---|---|---|
| U1 | Clickable prototype (judges, day 1) | `https://cropguardian-prototype.onrender.com` + `/app` `/demo-user` `/demo-admin` `/admin` `/data` `/security` `/architecture` `/presentation` `/pitchdeck` `/audit` | Phase 8.1 | submission form, README, video |
| U2 | Real web app | `https://cropguardian-web.onrender.com` (same routes) | Phase 8.3 | API `APP_BASE_URL` (CORS), Supabase Auth Site URL + Redirect URLs, Turnstile allowed hostnames, CSP, submission form |
| U3 | API | `https://cropguardian-api.onrender.com` (`/healthz`, `/readyz`) | Phase 8.2 | web `VITE_API_BASE_URL`, CSP `connect-src`, UptimeRobot, GitHub secret `API_BASE_URL`, n8n |
| U4 | Supabase project | `https://<project-ref>.supabase.co` | Phase 3 | web `VITE_SUPABASE_URL`, API `SUPABASE_URL`, `SUPABASE_JWKS_URL`, CSP |
| U5 | n8n webhook | `https://<your-n8n>/webhook/cg-alert-published` | Phase 9 | API `N8N_ALERT_WEBHOOK_URL` |
| U6 | Status / uptime page (optional) | UptimeRobot public status page | Phase 9 | README |
| U7 | Custom domain (optional, recommended) | `app.<domain>` → U2, `api.<domain>` → U3, `demo.<domain>` → U1 | Phase 8.5 | replaces U1–U3 everywhere; lets you re-point DNS if Render suspends a service |

Render names must be globally unique — if `cropguardian-web` is taken, Render adds a suffix. **Copy
the exact URL Render shows** and update this table before pasting it anywhere.

---

## Phase 0 — Accounts (Apon, everyone · 16 Oct · 1 h)
All free. Use a team email (e.g. a shared Gmail) as the owner where possible; add members as collaborators.

| Account | Who | Why | Notes |
|---|---|---|---|
| GitHub | all 5 | code, CI, Dependabot, secrets | enable 2FA |
| Render | Apon (+ Taeen as workspace member) | hosting (static sites + API) | sign up with GitHub |
| Supabase | Apon (+ Taeen) | DB, vector search, storage, auth | sign up with GitHub |
| Anthropic Console | Raisa / Salwa | LLM API key | **set a monthly spend limit** before creating keys |
| Cloudflare | Apon | Turnstile CAPTCHA (free) | also free DNS if you buy a domain |
| Google (Colab) + Kaggle | Taeen | free GPU training | Kaggle needs phone verification for GPU |
| n8n Cloud trial **or** self-host | Apon | automation | see [other platforms §5](03-other-platforms-guide.md) |
| UptimeRobot (or cron-job.org) | Apon | keep-warm + uptime alerts | free |
| Telegram | team | team alert channel via a bot | create the bot with @BotFather |

**Expected:** everyone can log in; 2FA on GitHub, Render, Supabase. **If it fails:** use the
"Sign in with GitHub" option everywhere so one identity covers all platforms.

## Phase 1 — Tools on Windows (each developer · 16 Oct · 1 h)
Open **PowerShell** and install (if a `winget` ID is not found, run `winget search <name>`):

```powershell
winget install --id Git.Git -e
winget install --id Microsoft.VisualStudioCode -e
winget install --id OpenJS.NodeJS.LTS -e
winget install --id Python.Python.3.12 -e
winget install --id GitHub.cli -e
winget install --id Docker.DockerDesktop -e      # optional: test the API image + run n8n locally
winget install --id GrafanaLabs.k6 -e            # load tests (Apon)
```
VS Code extensions: Python, ESLint, Docker, Mermaid preview, GitLens.

Verify (close and reopen PowerShell first):
```powershell
git --version; node -v; npm -v; py -3.12 --version; gh --version; docker --version; k6 version
git config --global user.name "Your Name"; git config --global user.email "you@example.com"
```
If PowerShell blocks scripts (virtualenv activation): `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

**Expected:** every command prints a version. **If it fails:** reboot after Docker Desktop (it needs
WSL 2); Python must be 3.12 to match the production container.

## Phase 2 — GitHub repository (Apon · 16 Oct · 30 min)
The **contents of `cropguardian/` become the repository root** (Render looks for `render.yaml` at the
root and resolves `rootDir` from there).

```powershell
gh auth login
Copy-Item -Recurse "C:\Hackathon\BracU Hackathon\cropguardian" "$HOME\code\cropguardian"
cd "$HOME\code\cropguardian"
git init -b main
git add .
git commit -m "chore: Crop Guardian template"
gh repo create cropguardian --private --source . --push
```
Then on github.com → the repo → **Settings**:
1. **Collaborators** → invite Taeen, Salwa, Raisa, Sara (Write).
2. **Branches** → protect `main` (rules in [`.github/README.md`](../../.github/README.md) §5).
3. **Code security** → enable Dependabot alerts, Dependabot security updates, secret scanning.
4. **Actions → General** → "Require approval for all external contributors".
5. Replace the handles in `.github/CODEOWNERS` with real GitHub usernames.
6. **Before submission (by 30 Oct):** make the repository **public** (judges must be able to open it).

**Expected:** all members can push branches and open PRs. **If it fails:** check the invite emails.

## Phase 3 — Supabase (Apon · 16–17 Oct · 2 h)
Full click-path: [`02-supabase-guide.md`](02-supabase-guide.md). Summary:
1. New project → name `cropguardian` → region nearest Bangladesh (Mumbai or Singapore) → strong DB
   password saved in a password manager.
2. Write `db/migrations/0001_init.sql` and `0002_rls.sql` from [`db/SCHEMA-SPEC.md`](../../db/SCHEMA-SPEC.md);
   run them in **SQL Editor**; run the synthetic seed.
3. **Advisors → Security Advisor** → zero errors (RLS enabled on every table).
4. **Storage** → buckets `scans` and `models`, both **private**.
5. **Authentication** → Email provider on; **URL Configuration**: Site URL = U2, Redirect URLs =
   U2 + `http://localhost:5173/**`; **Bot and Abuse Protection** → CAPTCHA = Cloudflare Turnstile.
6. Create the two demo users (Authentication → Users → Add user), put their ids in the seed.
7. Collect: project URL (U4), **publishable key**, **secret key**, JWKS URL
   `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json`, **pooler** connection string (Connect button).

**Expected:** tables visible, Security Advisor clean, buckets private. **If it fails:** see
[Supabase guide §10](02-supabase-guide.md#10-troubleshooting).

## Phase 4 — Local backend (Apon, Taeen · from 18 Oct)
```powershell
cd services\api
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
Copy-Item ..\..\.env.example .env      # then fill the values (never commit .env)
uvicorn app.main:app --reload --port 8000
```
Open `http://localhost:8000/healthz` → `{"status":"ok"}` and `http://localhost:8000/docs`.
Run tests: `pytest ..\..\tests -q`. Test the container like Render will:
```powershell
docker build -t cropguardian-api .
docker run --rm -p 10000:10000 -e PORT=10000 --env-file .env cropguardian-api
```
**Expected:** `/healthz` 200 locally and in Docker. **If it fails:** `$PORT` not used in the start
command; Python not 3.12; missing `.env` values (the app must still start — only `/readyz` fails).

## Phase 5 — Local frontend (Sara · from 18 Oct)
```powershell
cd apps\web
npm install                     # creates package-lock.json — COMMIT it (Render runs npm ci)
notepad .env.local              # paste the four VITE_* lines from the root .env.example and fill them
npm run dev                     # http://localhost:5173
npm run lint; npm run typecheck; npm run build
npx playwright install          # once, for E2E tests
```
**Expected:** app opens in Bangla; build creates `dist/`. **If it fails:** Node version < 20; missing
`package-lock.json` breaks `npm ci` on Render.

## Phase 6 — Train and register the model (Taeen · 16–25 Oct)
1. Download D1 and D2 (and D3 for out-of-distribution tests) — links in [`datasets.md`](../data/datasets.md).
2. Upload them to Kaggle (private dataset) or Google Drive; open a GPU notebook; follow
   [`ml/vision/train.md`](../../ml/vision/train.md) and the config in [`ml/vision/README.md`](../../ml/vision/README.md).
3. Export int8 ONNX ([`export_onnx.md`](../../ml/vision/export_onnx.md)); compute SHA-256:
   `Get-FileHash classifier.int8.onnx -Algorithm SHA256`.
4. Supabase → Storage → `models` → upload to `crop-disease-classifier/<semver>/classifier.int8.onnx`.
5. Insert the `model_versions` row (hash, τ, T, evaluation summary); activate from `/admin`.

**Expected:** API boot log shows "model loaded sha256=…"; `/readyz` 200. **If it fails:** hash mismatch
→ re-upload; file too large/slow → choose MobileNetV3 per the selection rule.

## Phase 7 — Knowledge base (Salwa · 16–22 Oct)
Register each DAE/BRRI/BARI document (licence note first), then follow
[`ml/rag/ingest.md`](../../ml/rag/ingest.md): extract → chunk → embed → insert → run the golden set.
**Expected:** Recall@8 measured; citation coverage 100 % on the golden set.

## Phase 8 — Deploy to Render (Apon)
Full guide: [`01-render-guide.md`](01-render-guide.md).

### 8.1 Prototype static site — **do this on 16 Oct** (public URL U1)
Render → **New → Static Site** → connect the GitHub repo → Root Directory `prototype` → Build Command
`echo static` → Publish Directory `.` → Create. Then **Redirects/Rewrites**: add the 10 route rewrites
(`/app` → `/app.html`, …) listed in the Render guide §4. Open every route on a phone.

### 8.2 API web service (U3) — from 20 Oct
**New → Web Service** → repo → Language **Docker** → Root Directory `services/api` → Instance type
**Free** → Health Check Path `/healthz` → add environment variables (Render guide §5: secrets typed
in the dashboard, never in files) → Create. Watch the logs for "model loaded" and "ready".

### 8.3 Web app static site (U2) — from 21 Oct
**New → Static Site** → Root Directory `apps/web` → Build `npm ci && npm run build` → Publish `dist` →
env vars `VITE_*` → rewrite `/*` → `/index.html` → security headers (Render guide §6).

### 8.4 Wire the URLs together (21 Oct, M2)
U2 → API `APP_BASE_URL` (CORS) · U2 → Supabase Site URL/Redirect URLs · U2 → Turnstile hostnames ·
U3 → web `VITE_API_BASE_URL` and CSP · redeploy the web site (VITE_* are baked in at build time).

### 8.5 Custom domain (optional, recommended before 30 Oct)
Render → service → **Settings → Custom Domains** → add `app.<domain>` / `api.<domain>` /
`demo.<domain>` → create the DNS records Render shows → TLS is issued automatically. Two custom
domains are included on the Hobby workspace; extra ones are billed. Keeping your own domain means you
can point DNS at a backup host if Render suspends a free service ([challenges §H](04-free-tier-challenges.md)).

### 8.6 Blueprint (optional)
Once all three services work, capture them in a `render.yaml` Blueprint (template in the Render guide
§8) so the whole stack can be recreated in a new workspace in minutes.

## Phase 9 — Automation & monitoring (Apon, Taeen · 23–27 Oct)
1. UptimeRobot: HTTP monitor on `U3/healthz` (keep-warm during demo windows) + monitors on U1, U2.
2. n8n: credentials (Telegram bot token, API signing secret) → build workflows 01–08 from
   [`automation/n8n/`](../../automation/n8n/README.md) → set the webhook URL (U5) in the API.
3. GitHub Actions: heartbeat workflow ([`.github/README.md`](../../.github/README.md) §3) with secrets
   `API_BASE_URL`, `N8N_WEBHOOK_SECRET`; Claude security review workflow with `CLAUDE_API_KEY`.
4. Sentry (optional): DSN into API env `SENTRY_DSN`.

## Phase 10 — Test the deployment (all · 25–28 Oct)
| Check | How | Owner |
|---|---|---|
| Smoke | n8n workflow 05 green; manual: demo → scan → advice → alerts → admin → audit | Apon |
| E2E | `BASE_URL=<U2> npx playwright test tests/e2e` (bn + en, phone size) | Sara |
| Security | everything in [`security-testing-guide.md`](../testing/security-testing-guide.md) | Apon, Salwa |
| Load | `k6 run -e BASE=<U3>` — short run only (Render may suspend for unusual outbound traffic) | Apon |
| Cold start | [`tests/timeout/cold_start_e2e.md`](../../tests/timeout/cold_start_e2e.md) | Sara |
| Devices | [`tests/manual/device-matrix.md`](../../tests/manual/device-matrix.md) | Sara, Raisa |
| Headers | securityheaders.com and Mozilla Observatory on U1, U2, U3 | Apon |

## Phase 11 — Go-live, submission & demo day
- **28 Oct code freeze** → final deploy → rollback rehearsal (Render "Rollback"; model re-activation).
- **29–30 Oct**: open U1–U3 on a phone **on mobile data, logged out** (judges are logged out); fill the
  [submission checklist](../congress/submission-checklist.md); repository public.
- **Demo day**: keep-warm 30 min before the slot; Supabase active; LLM budget checked; recorded video
  ready; prototype URL as the no-backend fallback ([demo script](../congress/demo-script.md)).

## Cost summary
| Item | Cost |
|---|---|
| Render static sites ×2 + API (free) | ৳0 (within 750 h, bandwidth and build-minute limits) |
| Supabase free project | ৳0 (500 MB DB, pauses after 1 week idle) |
| Cloudflare Turnstile, UptimeRobot, GitHub Actions (public repo), Colab/Kaggle | ৳0 |
| n8n | ৳0 self-hosted / trial; paid after the Cloud trial |
| LLM API | pay-per-use — **set a spend cap**; cache advice to keep it small |
| Custom domain | optional, yearly registrar fee |
