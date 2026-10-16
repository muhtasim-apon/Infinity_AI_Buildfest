# Zero to deployment — 9 steps, 14 days

The shortest path to a working public app by the deadline. Each step: **who · which day · what to do ·
done when**. Code is written from the specs ([API](../../services/api/SPEC.md), [web](../../apps/web/SPEC.md),
[database](../../db/SCHEMA-SPEC.md)); this guide is only about getting it **live**.

## The 3 URLs we will have
| URL | What | Live by |
|---|---|---|
| `https://cropguardian-prototype.onrender.com` | clickable prototype (+ `/app`, `/demo-user`, `/demo-admin`, `/admin`, `/data`, `/security`, `/architecture`, `/presentation`, `/pitchdeck`, `/audit`) | **Day 1 (16 Oct)** |
| `https://cropguardian-api.onrender.com` | API (`/healthz`, `/readyz`) | Day 5 (20 Oct) |
| `https://cropguardian-web.onrender.com` | real web app (same routes) | Day 6 (21 Oct) |

Render may add a suffix if a name is taken — **copy the exact URL Render shows** into this table.

## Timeline
| Day | Date | Step |
|---|---|---|
| 1 | Fri 16 Oct | Step 1 accounts & tools · Step 2 GitHub · **Step 3 prototype live** |
| 2 | Sat 17 Oct | Step 4 Supabase |
| 3–5 | 18–20 Oct | Step 5 API running locally → **live on Render** |
| 6 | Wed 21 Oct | Step 6 web app **live**, all URLs connected |
| 5–10 | 20–25 Oct | Step 7 model + knowledge base uploaded (as they become ready) |
| 10 | Sun 25 Oct | Step 8 keep-alive + security checks |
| 13–14 | 28–29 Oct | Step 9 freeze, final checks from a phone, submit on 30 Oct |

---

## Step 1 — Accounts and tools (everyone · Day 1 · 1 h)
**Accounts (free, sign in with GitHub where possible):** GitHub (all), Render + Supabase + Cloudflare +
UptimeRobot (Apon), Anthropic (Raisa, set a spend limit first), Google Colab + Kaggle (Taeen).

**Install (PowerShell):**
```powershell
winget install --id Git.Git -e
winget install --id Microsoft.VisualStudioCode -e
winget install --id OpenJS.NodeJS.LTS -e
winget install --id Python.Python.3.12 -e
winget install --id Docker.DockerDesktop -e      # Apon only — to test the API container
```
Check: `git --version; node -v; py -3.12 --version`. **Done when** every command prints a version.

## Step 2 — GitHub repository (Apon · Day 1 · 20 min)
The **contents of `cropguardian/`** become the repository root.
```powershell
Copy-Item -Recurse "C:\Hackathon\BracU Hackathon\cropguardian" "$HOME\code\cropguardian"
cd "$HOME\code\cropguardian"
git init -b main; git add .; git commit -m "chore: Crop Guardian template"
```
On github.com: **New repository** `cropguardian` (private) → follow "push an existing repository" →
Settings → **Collaborators**: add the 4 members → Settings → **Code security**: turn on Dependabot alerts
and secret scanning. Make the repo **public on 30 Oct** for judges.
**Done when** everyone can push a branch.

## Step 3 — Prototype live (Apon · Day 1 · 15 min)
Render → **New → Static Site** → pick the repo → Root Directory `prototype` → Build Command
`echo static` → Publish Directory `.` → Create. Then add the 10 rewrites from
[Render guide §1](01-render-guide.md#1-prototype-static-site). **Done when** every prototype route opens
on a phone.

## Step 4 — Supabase (Apon · Day 2 · 2 h)
Follow [Supabase guide](02-supabase-guide.md) steps 1–6: project → keys → schema → private buckets →
email login + CAPTCHA → two demo users. **Done when** Security Advisor shows no errors and you have the
5 values (URL, publishable key, secret key, JWKS URL, pooler connection string) in the team password
manager.

## Step 5 — API live (Apon, Taeen · Days 3–5)
1. Run locally:
   ```powershell
   cd services\api
   py -3.12 -m venv .venv; .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item ..\..\.env.example .env     # fill the values; never commit .env
   uvicorn app.main:app --reload --port 8000
   ```
   `http://localhost:8000/healthz` → `{"status":"ok"}`.
2. Test the container: `docker build -t cg-api .` then
   `docker run --rm -p 10000:10000 -e PORT=10000 --env-file .env cg-api`.
3. Create the API on Render — [Render guide §2](01-render-guide.md#2-api-web-service).

**Done when** `https://cropguardian-api.onrender.com/healthz` returns 200 (deploy as soon as `/healthz`
works — don't wait for the full API; later code deploys automatically on every push to `main`).

## Step 6 — Web app live + connect the URLs (Sara, Apon · Day 6)
1. Locally: `cd apps\web; npm install; npm run build` — **commit `package-lock.json`**.
2. Create the web site on Render — [Render guide §3](01-render-guide.md#3-web-app-static-site).
3. Connect the URLs (one time):

| Copy this | Into |
|---|---|
| web URL | API env `APP_BASE_URL` · Supabase Auth → URL Configuration · Turnstile widget hostnames |
| API URL | web env `VITE_API_BASE_URL` (then redeploy the web site) |

**Done when** the web app loads, `/demo-user` works, and the browser console shows no CORS errors.

## Step 7 — Model and knowledge base (Taeen, Salwa · Days 5–10, when ready)
- **Model:** train on Colab/Kaggle ([`ml/vision/README.md`](../../ml/vision/README.md)) → export ONNX →
  upload to Supabase Storage bucket `models` → add the `model_versions` row → restart the API on Render.
  **Done when** `/readyz` shows the model's version and hash.
- **Knowledge base:** ingest the guides ([`ml/rag/ingest.md`](../../ml/rag/ingest.md)) into Supabase.
  **Done when** a test scan returns advice with at least one citation.

## Step 8 — Keep-alive and security checks (Apon · Day 10)
1. **UptimeRobot** → New monitor → HTTP(s) → `https://cropguardian-api.onrender.com/readyz` → shortest
   free interval (5 minutes at the time of writing) → alert email = team.
   This one monitor does three jobs: keeps the API from sleeping (Render sleeps after 15 min), keeps the
   database active (Supabase pauses after a week without activity), and emails us if anything is down.
   Add two more monitors for the prototype and web URLs (no keep-alive needed, uptime alerts only).
2. Run the **pre-release checks** in [`security-testing-guide.md`](../testing/security-testing-guide.md) §1
   and tick the [security checklist](../security/security-checklist.md).
**Done when** UptimeRobot is green and every checklist row is ticked.

## Step 9 — Freeze and submit (all · Days 13–14 → submit 30 Oct)
- **28 Oct:** code freeze — only bug fixes. Note the last good deploy in Render (for rollback).
- **29 Oct:** open all 3 URLs **on a phone, on mobile data, logged out** (judges are logged out); run
  the demo script; record the backup demo video.
- **30 Oct:** repository public → submission form ([checklist](../congress/submission-checklist.md)).
- **Demo day:** check UptimeRobot is green and Supabase is active 30 min before; video ready as backup.

## If something breaks
| Problem | First fix |
|---|---|
| A deploy broke the site | Render → service → **Events** → previous deploy → **Rollback** |
| API slow on first request | it was asleep — check the UptimeRobot monitor is running |
| "database down" in `/readyz` | Supabase project paused → dashboard → **Restore** |
| Anything else | [04 Free-tier problems](04-free-tier-challenges.md) |

## After 31 Oct (only if time allows)
n8n workflows ([`automation/n8n/`](../../automation/n8n/README.md)) · custom domain · Render Blueprint ·
Sentry error tracking · Telegram team alerts · staging environment · k6 load test · backup hosting
for the prototype (GitHub Pages / Cloudflare Pages).
