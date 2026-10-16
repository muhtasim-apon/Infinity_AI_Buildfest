● Updated plan
  ⎿  /plan to preview

● Updated plan

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Ready to code?

 Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Plan — Docs-only repository template + platform, security & free-tier guides

 Context

 The user wants cropguardian/ to be a template only: no code. The team will implement it piece
 by piece later. Confirmed choices: docs-only template (remove every code/stub/config file; each
 folder keeps a spec .md saying what to build, where, the contract and the owner) and keep the
 prototype/ (static HTML/CSS/JS clickable demo). They also asked for:
 - large deployment guides for Render, Supabase and the other platforms;
 - security and testing guidance covering the 20-point checklist in
   received_1631649765008129.webp (RLS, auth on every route, never trust the frontend, rate limiting,
   sanitise input, parameterised queries, CORS, HTTPS, IDOR, debug off, CAPTCHA, log admin actions,
   private buckets, hide admin pages properly, update packages, upload-type checks, Claude security
   review, security headers, webhook signatures);
 - every Render free-tier / free-domain challenge (the service "can be turned off") with solutions.

 Verified facts (fetched 2026-10-16, to be added to docs/research/sources.md):
 - Render free: suspends ALL free web services when 750 h used; bandwidth over limit with no payment
   method → all free services suspended for the month; build minutes over → builds disabled (existing
   build keeps running); may suspend a free web service for unusually high outbound traffic (calls to
   external DBs/APIs/object storage); may restart any time; usage-alert emails. Upgrading the
   workspace does not lift limits — only the service's compute plan does.
 - Render custom domains: Hobby workspace includes 2; auto TLS; onrender.com subdomain can be disabled
   once a custom domain exists.
 - Already verified earlier (R1–R8): spin-down 15 min, ~1 min cold start, ephemeral disk, single
   instance, SMTP ports blocked, PG 30-day expiry; Docker env vars become build args; env-var groups
   can't use sync:false; Supabase publishable/secret keys (legacy deprecated end-2026), JWKS
   verification, pooler IPv4 (5432 session / 6543 transaction, asyncpg statement_cache_size=0),
   phone OTP needs paid SMS, free project pauses after 1 week, 500 MB.
 - Supabase Auth CAPTCHA: hCaptcha or Cloudflare Turnstile; Settings → Authentication → Bot and Abuse
   Protection; protects sign-in, sign-up, password reset.
 - Claude security review: GitHub Action anthropics/claude-code-security-review (secret
   CLAUDE_API_KEY, PR comments, not hardened against prompt injection → trusted PRs only) and Claude
   Code /security-review for local changes.

 Step 0 — Remove every human-review feature (user decision: no time to build it)

 Exclude completely — no roadmap mention, no stubs, no UI:
 - Agronomist review queue, expert_reviews, feedback_labels, the agronomist role, review routes
   (/app/review, /v1/review/*), the label-export data flywheel and n8n workflow 09.
 - Human approval of alerts and the agent's create_alert_draft tool.

 Replacements (behaviour must stay safe without humans):
 - Abstain stays (ADR 0005 rewritten as "calibrated confidence + abstain"): below τ the app says
   "not sure" and shows retake tips + a static "contact your local agriculture office" card. No queue.
 - Alerts become automatic, conservative, in-app only: rules v1 publish when thresholds are met,
   labelled "possible outbreak — unverified, rule-based"; per-area cooldown; no SMS/broadcast; admin can
   only dismiss afterwards (an operator kill-switch, not a review step). n8n workflow 01 fans out to
   in-app/Telegram team channel only.
 - Model improvement = retraining on public datasets only (no user labels).

 Files to update for this (representative): ADR 0005 + ADR index; SDD (requirements F4/F8, data flow,
 API table, agents, KPIs); docs/data/erd.md, docs/diagrams/erd.mmd, db spec (drop tables/role,
 RLS rules); docs/architecture/* (sequence 3 and 4, overview modules, data flow §2); docs/ai/*
 (agent tools, eval-plan, responsible-ai, outbreak card, statistics §9); docs/product/* (Karim persona
 → removed; journeys J2/J4/J5); docs/security/threat-model.md (T3, T18), audit-readiness;
 docs/plan/gantt.md + RACI (re-assign freed days: Apon 22 Oct → rate limiting & audit log; Sara
 review-UI time → polish/a11y); congress rubric map, video and demo scripts; automation/n8n (drop 09,
 change 01); tests (drop review cases); prototype (admin.html review + approve tabs → removed/
 dismiss-only; app.html "sent to an agronomist" copy; synthetic-data.js reviewQueue/drafts;
 audit.html agreement row); i18n strings review.*.

 Step 1 — Convert the repo to docs-only

 Remove (all are stubs/config, nothing implemented): services/api/app/** (.py), Dockerfile,
 .dockerignore, requirements*.txt; apps/web/src/** (.ts/.tsx), package.json,
 package-lock.json, tsconfig.json, vite.config.ts, index.html, eslint.config.js;
 db/*.sql, db/migrations/; tests/**/*.py|.ts|.js, tests/conftest.py; .github/workflows/*.yml,
 .github/dependabot.yml; render.yaml; scripts/*.py; docs/report/report.html, parts/,
 report.css; all __pycache__.

 Keep: all .md; prototype/ (approved); LICENSE; .gitignore; .env.example (variable list,
 not code); apps/web/src/i18n/bn.json|en.json → move to apps/web/i18n/ (copy text content);
 docs/diagrams/*.mmd; ml/rag/golden_set.template.csv; .github/CODEOWNERS, PR and issue templates;
 the PDF report.

 Replace each removed area with a spec file (content carried over from the stubs' docstrings so no
 design detail is lost). Each spec has: file tree to create, per-file responsibility and contract
 (inputs/outputs/errors/timeouts), owner, Gantt day, definition of done, and which tests prove it.
 - services/api/SPEC.md — app factory, config vars, routers (all 17 endpoints), schemas (fields and
   validation rules), security modules, ML (preprocess/inference/decision rules), RAG (retriever, prompt,
   validator V1–V6), services (scan flow, advisory, outbreak rules, audit chain), dependencies list,
   container spec (non-root, $PORT, 1 worker, no build ARGs, model downloaded at boot).
 - apps/web/SPEC.md — stack, file tree, routes table, lib/api contract (cold-start/retry rules),
   outbox, image pipeline, feature pages ↔ prototype screens, lint/CI rules, env vars.
 - db/SCHEMA-SPEC.md — enums, every table with column/type/constraint tables, indexes, the audit
   hash-chain function as a described algorithm, RLS rules as a table (including the two recursion
   pitfalls found earlier → SECURITY DEFINER helpers), migration order, seed (synthetic) contents.
 - tests/<type>/README.md — test-case tables replacing each stub file (cases already written in the
   stubs: decision, validator, upload, outbreak, HMAC, blackbox partitions, timeouts, races, k6 profile,
   security per threat, ML gates/robustness, E2E journeys, a11y); n8n fixture described in
   tests/n8n/README.md.
 - ml/vision/README.md — labels taxonomy + training config as tables (from labels/train_base yaml).
 - .github/README.md — CI pipeline spec (jobs, gates, when strict), Dependabot spec, Claude security
   review workflow spec, heartbeat workflow spec.

 Step 2 — New and updated guides (the "large" part)

 New files under docs/deployment/ (index: docs/deployment/README.md):
 1. 00-zero-to-deploy.md — master order of work from zero: Phase 0 accounts → 1 tools on Windows
    (winget IDs, versions, VS Code extensions, verify commands) → 2 GitHub repo (repo root =
    cropguardian/ contents, branch protection, team access, secrets, public before submission) → 3
    Supabase → 4 local backend → 5 local frontend → 6 ML training → 7 RAG ingest → 8 Render → 9
    automation → 10 deployed testing → 11 go-live/demo day; each phase: owner, Gantt day, steps,
    expected result, "if it fails".
 2. 01-render-guide.md (replaces render-guide.md) — free-tier model; service plan (prototype
    static, web static, API Docker); Blueprint template (as a documented reference block, with the
    sync:false-not-in-groups rule); dashboard click-paths; env vars table (public vs secret); health
    checks; CORS; rewrites for SPA and prototype routes; security headers; custom domain (2 included,
    auto TLS, disable onrender.com); deploy hooks/rollback; logs/metrics; usage alerts.
 3. 02-supabase-guide.md — project + region; keys (publishable/secret, JWKS); pooler strings;
    applying the schema spec via SQL editor; RLS enable + testing; Security Advisor; private buckets +
    policies; Auth (email OTP, URL config, CAPTCHA Turnstile/hCaptcha, rate limits, custom SMTP for
    pilots); demo users; backups/export (free has none → manual pg_dump schedule); pause/restore.
 4. 03-other-platforms-guide.md — GitHub (Actions, secrets, Dependabot, branch rules,
    CODEOWNERS), Anthropic Console (key, spend cap, key hygiene), Google Colab / Kaggle (GPU,
    checkpoints), dataset downloads, n8n (Cloud trial vs self-host Docker; credentials; HMAC),
    UptimeRobot / cron-job.org (keep-warm, status alerts), Telegram bot (team alerts), Cloudflare
    Turnstile (CAPTCHA keys), optional custom domain registrar/DNS.
 5. 04-free-tier-challenges.md (expands challenges-and-recovery.md, which becomes this) —
    every challenge with cause, prevention, detection, recovery, owner: Render spin-down/cold start,
    750 h suspension, bandwidth suspension, build-minute lockout, outbound-traffic suspension,
    random restarts, ephemeral disk, single instance, SMTP blocked, PG expiry, onrender.com domain
    dependency, Supabase pause/500 MB/egress/connection limits/no backups/key deprecation, LLM quota,
    n8n trial expiry, GitHub cron delays; plus "if Render turns us off" runbook: backup static host
    for prototype/web (GitHub Pages or Cloudflare Pages), backup API host options to evaluate, custom
    domain so DNS can be repointed, recorded demo video, rebuild-from-blueprint in a new workspace.
    Platform limits of backup hosts are marked "verify before relying on".

 New/updated under docs/security/ and docs/testing/:
 6. docs/security/security-checklist.md — the 20 items from the image + ours (secrets, PII,
    prompt injection, audit chain): for each → what it means, how Crop Guardian does it, where it is
    configured (Render / Supabase / API module / web), owner, the test that proves it, status box.
    "Hide admin pages properly" = server-side role check + RLS + no admin data in public bundles, not
    CSS hiding. "Claude security review" = GitHub Action on PRs + /security-review before merge.
 7. docs/testing/security-testing-guide.md — how to run security testing per platform: RLS
    tests with publishable key, IDOR, auth/JWT tampering, rate-limit, upload abuse, CORS/header
    checks, OWASP ZAP baseline on staging, dependency + secret scans, webhook replay, LLM red-team,
    Supabase Security Advisor, Claude security review, schedule (per PR / nightly / pre-release).
 8. Update docs/testing/test-strategy.md and test-links.md to point to test-case READMEs (no code
    files) and add the new tools.

 Step 3 — Consistency pass

 - Re-point every Markdown link/backtick path that named a removed file to its spec (grep for
   .py, .ts, .sql, render.yaml, Dockerfile, scripts/).
 - Update CLAUDE.md (docs-only template rule), cropguardian/README.md, root README.md,
   docs/README.md, SDD links, CONTRIBUTING.md DoD (no bn.json path change issues).
 - Add new sources (Render suspension rules, custom domains, Supabase CAPTCHA, Claude security review)
   to docs/research/sources.md.
 - Rebuild the PDF with the builder kept outside the repo (scratchpad copy of
   build_report.py/chrome_pdf.py/parts/css), adding the new guides as chapters; only the PDF stays
   in docs/report/.

 Coverage of the image checklist (all 20 → security-checklist.md rows, each with config place + test)

 Row level security · Auth on every API route · Never trust the frontend · Rate limiting · Sanitize user
 input · Parameterized queries · Lock down CORS · HTTPS everywhere · Stop IDOR bugs · Debug mode off in
 prod · CAPTCHA on public forms (Turnstile via Supabase Auth + on the demo-session endpoint) · Log admin
 actions (hash-chained audit) · Private storage buckets · Hide admin pages properly (server-side role +
 RLS + separate lazy chunk, noindex) · Update vulnerable packages (Dependabot + pip-audit/npm audit) ·
 Check file upload types (magic bytes + re-encode) · Claude security review (GitHub Action on PRs +
 /security-review) · Security headers (CSP, HSTS, nosniff, frame-ancestors, referrer) · Verify webhook
 signatures (HMAC + replay window).

 Deploy & URL guideline (in 00-zero-to-deploy.md + 01-render-guide.md)

 Final public URLs and how each is created: prototype https://cropguardian-prototype.onrender.com
 (+ /app, /demo-user, /demo-admin, /admin, /data, /security, /architecture,
 /presentation, /pitchdeck, /audit rewrites), web https://cropguardian-web.onrender.com, API
 https://cropguardian-api.onrender.com/healthz, Supabase project URL; optional custom domain
 (2 included, auto-TLS) mapped as app.<domain>, api.<domain>, demo.<domain> so DNS can be
 repointed if Render suspends a service. Includes the order to create them, where each URL is pasted
 (CORS origin, Supabase redirect URLs, VITE_API_BASE_URL, CSP connect-src, UptimeRobot, GitHub
 secrets, submission form) and a "verify every URL from a phone on mobile data, logged out" checklist.

 Verification


 - find cropguardian -type f outside prototype/ shows only .md, .mmd, .csv, .json (i18n
   text), .env.example, .gitignore, LICENSE, CODEOWNERS, PDF.
 - Link check script (scratchpad): zero broken relative links; grep finds no references to removed
   files except as "file to create" inside specs.
 - Every one of the 20 image items appears in security-checklist.md with a test reference.
 - grep -ri "agronomist\|review queue\|expert_review\|feedback_label\|approve" across cropguardian/
   returns nothing (except unrelated words, checked by hand).
 - Prototype still opens (no change); PDF rebuilds and chapter pages resolve.
 - Nothing committed, pushed or deployed.
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
