
● Updated plan

──────────────────────────────────────────────────────────────────────────────────
 Ready to code?
     
 Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Plan — "Zero to deployment" setup guide for Crop Guardian

 Context

 The repo now holds the cropguardian/ template (docs, stubs, clickable prototype,
 report). The user
 wants complete, ordered steps: every tool/account to set up, how to set it up on
 their Windows
 machine, and how to deploy everything (prototype, web app, API, database, model,
 RAG, n8n) from zero.
 Deliverable = a guide in the repo (+ PDF chapter) and a condensed version in
 chat. While verifying facts,
 three things in the current template would make the guide fail, so small fixes
 are included.

 Verified facts driving the guide (fetched 2026-10-16):
 - Render blueprint spec: envVarGroups cannot use sync: false → current
   render.yaml would be
   rejected. Static sites need runtime: static, buildCommand, staticPublishPath;
   rootDir supported;
   blueprint defaults to repo-root render.yaml.
 - Render Docker: service env vars become Docker build args automatically → never
   put secrets in
   build args; model must come from a non-secret URL or be downloaded at boot.
 - Supabase phone OTP requires a paid SMS provider (Twilio/Vonage/MessageBird) →
   MVP uses email
   OTP/magic link + one-click demo accounts.
 - Known gotcha to state with "verify": Supabase's direct DB host is IPv6-only;
   from Render use the
   Supavisor pooler connection string (IPv4); with transaction mode (port 6543)
   asyncpg needs
   statement_cache_size=0.
 - Existing limits already in docs/research/sources.md (R1, R2): 15-min
   spin-down, 750 h, ephemeral
   disk, Render PG 30-day expiry, Supabase 1-week pause, 500 MB.

 Deliverables

 1. New guide cropguardian/docs/deployment/zero-to-deploy.md (main output)

 Ordered phases, each with: who (Apon/Taeen/Salwa/Raisa/Sara), exact commands
 (PowerShell + Git Bash),
 expected result, and "if it fails" line.

 - Phase 0 — Accounts (all free): GitHub, Render, Supabase, Anthropic Console
   (spending cap), Google
   (Colab) + Kaggle, n8n Cloud trial or self-host, UptimeRobot/cron-job.org,
   Telegram (bot via BotFather).
 - Phase 1 — Install tools on Windows with winget IDs: Git, VS Code (+
   extensions: Python, ESLint,
   Mermaid preview, Docker), Node.js 20 LTS, Python 3.12 (match Docker; keep 3.13
   for report build),
   Docker Desktop (optional local image test + local n8n), PostgreSQL client
   psql, Supabase CLI (optional),
   k6, GitHub CLI; Playwright browsers via npx; version-check commands.
 - Phase 2 — Repo: create GitHub repo with cropguardian/ contents as repo root
   (so render.yaml
   and rootDir paths work); commit; branch protection on main; replace CODEOWNERS
   handles; GitHub
   secrets for CI.
 - Phase 3 — Supabase: create project (region nearest Bangladesh — Mumbai or
   Singapore; record in
   data-sovereignty.md); enable vector; run db/schema.sql then
   db/rls_policies.sql in SQL editor
   (or psql -f migrations/0001_init.sql — \ir needs psql); buckets scans, models
   private; Auth:
   email OTP on, site URL + redirect URLs = Render web URL + localhost; create 3
   demo users → UUIDs into
   seed_synthetic.sql → run; copy URL, anon key, service-role key, JWT secret,
   pooler DB URL.
 - Phase 4 — Local backend: venv (py -3.12), pip install -r requirements.txt -r
   requirements-dev.txt,
   .env from .env.example, uvicorn app.main:app --reload, check /healthz (works
   now) and /docs;
   note other endpoints are stubs to implement per Gantt.
 - Phase 5 — Local frontend: npm install, apps/web/.env.local, npm run dev, npm
   run build;
   Playwright install.
 - Phase 6 — ML (Taeen): Colab/Kaggle GPU, download D1/D2/D3, follow
   ml/vision/train.md →
   export_onnx.md; upload ONNX to Supabase models/; insert model_versions row;
   create signed URL.
 - Phase 7 — RAG (Salwa): register docs in kb_documents, follow ml/rag/ingest.md,
   export e5 to ONNX.
 - Phase 8 — Deploy to Render (Apon), in this order:
   a. Prototype static site today (public URLs for judges immediately; /app,
      /admin… rewrites).
   b. Blueprint → web static site + API Docker service; fill secrets in
      dashboard; set APP_BASE_URL,
      VITE_*; verify /healthz; CORS check.
   c. Model delivery: download at boot from signed URL (default) or MODEL_URL
      build arg (non-secret URL).
 - Phase 9 — Automation: keep-warm (UptimeRobot 5-min or n8n), Supabase heartbeat
   (GitHub Actions
   cron or n8n), n8n workflows 01–09 import order, HMAC secret shared with API,
   Telegram team channel.
 - Phase 10 — Test the deployment: smoke checklist, k6 run vs staging, ZAP
   baseline, Playwright
   against Render URL, manual device matrix, cold-start test.
 - Phase 11 — Go-live & demo day: submission checklist, keep-warm window, budget
   caps, rollback
   (Render "Rollback", model flip in /admin), Supabase restore.
 - Troubleshooting table: build fails, port binding, CORS, SPA 404, IPv6/pooler
   connect errors,
   prepared-statement errors, OOM, paused Supabase, 750 h exhausted, LLM 429,
   Bangla font, email OTP not arriving.
 - Cost table: everything ৳0 except LLM usage (cap it) and optional SMS.
 - Mermaid timeline mapping phases onto Gantt days (16–21 Oct).

 2. Fixes so the guide's steps actually work

 - cropguardian/render.yaml: move secrets to per-service envVars with sync:
   false; keep group only
   for non-secret shared values (or drop group); add cropguardian-prototype
   static service
   (rootDir: prototype, buildCommand: echo "static prototype", staticPublishPath:
   ., rewrites
   /app → /app.html, /admin, /data, /security, /architecture, /presentation,
   /pitchdeck,
   /audit, /demo-user, /demo-admin).
 - cropguardian/services/api/.dockerignore (exclude .env, __pycache__, tests);
   Dockerfile comment:
   MODEL_URL must be non-secret (Render passes env vars as build args).
 - cropguardian/.env.example: DATABASE_URL example in pooler format + note on
   IPv4/pooler and
   statement_cache_size=0; services/api/app/db.py docstring gets the same note.
 - cropguardian/apps/web/.env.example (VITE_ vars only) and minimal
   apps/web/eslint.config.js
   (lint script references ESLint 9 flat config).
 - cropguardian/.github/workflows/quality-gates.yml: mark jobs that cannot pass
   on stubs
   (api mypy/pytest coverage, contract, ml) continue-on-error: true with a TODO
   to remove at M4.
 - New cropguardian/.github/workflows/heartbeat.yml: daily cron hitting /healthz
   and Supabase
   heartbeat endpoint (fallback if n8n is down).
 - SECURITY.md / SDD: "phone OTP" → "email OTP now; phone OTP when an SMS
   provider is funded".
 - Link the guide from cropguardian/README.md, docs/README.md,
   docs/deployment/render-guide.md;
   add to CHAPTERS in scripts/build_report.py (Part V); rebuild PDF.

 Verification

 - python scripts/build_report.py builds; new chapter appears with resolved page
 - python scripts/build_report.py builds; new chapter appears with resolved page
   number.
 - Re-run link check + leftover grep script (all relative links resolve).
 - Validate YAML files parse (python -c "import yaml…" if PyYAML present, else
   visual check);
   render.yaml has no sync: false inside envVarGroups.
 - Prototype rewrite targets exist (each /x → /x.html file present).
 - Nothing deployed, committed or pushed; the guide is instructions for the team.
 - Chat reply: condensed 12-step version + link to the file.

 Your note asks for three things: keep the API awake with UptimeRobot, stay
  inside Render's 750 free hours, and know what to do if the hours run low.

  Part 1 — Set up the UptimeRobot keep-alive (10 minutes)

  The free API sleeps after 15 minutes without traffic. A ping every 5 minutes
  means it never reaches 15 idle minutes, so it stays awake.

  1. Make sure your API is deployed and https://<your-api>.onrender.com/healthz
     returns {"status":"ok"}.
  2. Go to uptimerobot.com, click Register for FREE, sign up with the team email
     and confirm it.
  3. On the dashboard, click + New monitor and fill it in:

  | Field               | Value                                         |
  |---------------------|-----------------------------------------------|
  | Monitor type        | HTTP(s)                                       |
  | Friendly name       | Crop Guardian API                             |
  | URL                 | https://<your-api>.onrender.com/readyz        |
  | Monitoring interval | 5 minutes (the shortest the free plan allows) |
  | Alert contacts      | tick the team email                           |

  4. Click Create monitor.
  5. Wait 5–10 minutes. The monitor should turn green (Up).
     - If it's red: open /readyz in your browser. If it says "db":"down", fix
       DATABASE_URL in Render first. Use the Supabase pooler string, with $ in the
       password written as %24.
     - If you need a green monitor right now, use /healthz temporarily, then
       switch back to /readyz once the database works. /readyz matters because it
       also touches the database, which keeps Supabase from pausing.
  6. Optional: add two more monitors for the prototype and web app URLs. They
     don't keep anything awake (static sites never sleep); they only email you if
     a site goes down.

  Check it worked: the next day, open your API URL in a private browser window. It
  should answer instantly, not after about a minute.

  Part 2 — Stay inside the 750 free hours

  One service running all month uses about 744 hours, which just fits.

  1. Never create a second free web service (Web Service with the Free instance
     type) in this Render workspace.
     - Static Sites (prototype, web app) are fine. They use no hours, so create as
       many as you like.
     - For a second backend (for example, staging), run it on your laptop instead.
  2. Check usage once a week, at Monday's stand-up: Render dashboard → your
     workspace name → Usage → "Free instance hours".
  3. Read Render's emails. Render warns you when you're close to the limit.

  Part 3 — If hours run low near the end of the month

  1. In UptimeRobot, open the API monitor and click Pause. The API then sleeps
     when idle and uses fewer hours. It just takes about a minute to wake on the
     first visit.
  2. Resume the monitor about 30 minutes before any demo or judging session.
  3. If the hours run out completely, Render suspends the API until the 1st of
     next month. Your options:
     - Show the prototype URL and the recorded demo video. Static sites usually
       keep working.
     - As a team decision, upgrade only the API service to a paid instance for the
       rest of the month.

  Reminders for 30–31 Oct: the monitor must be green, the Supabase dashboard must
  show the project active, and both should be checked 30 minutes before demo day.

✻ Baked for 22s · done 8:27 PM

─────────────────────────────────────── external-resources-field-loss-evaluation ─
❯ [⧉ In .env.example]
──────────────────────────────────────────────────────────────────────────────────
  ⏵⏵ auto mode on (shift+tab to cycle) · ← 1 agent
