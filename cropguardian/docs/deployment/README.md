# Deployment guides

Read in this order:

| # | Guide | What it covers |
|---|---|---|
| 00 | [Zero to deployment](00-zero-to-deploy.md) | accounts → tools → repo → Supabase → local run → model → knowledge base → Render → automation → testing → go-live; the **URL plan** (every public URL, where it is created and where it is pasted) |
| 01 | [Render](01-render-guide.md) | prototype + web static sites, Docker API, env vars, rewrites, security headers, custom domain, Blueprint template, rollback |
| 02 | [Supabase](02-supabase-guide.md) | project, keys (publishable/secret), pooler, schema, RLS, private buckets, auth + CAPTCHA, backups, pause/restore |
| 03 | [Other platforms](03-other-platforms-guide.md) | GitHub, Anthropic, Cloudflare Turnstile, Colab/Kaggle, n8n, UptimeRobot, Sentry, Telegram, custom domain, security tools |
| 04 | [Free-tier challenges & recovery](04-free-tier-challenges.md) | every free-tier limit that can slow or **turn off** the app, with prevention, detection, recovery — and the "Render turned us off" runbook |

Security: [checklist (19 controls)](../security/security-checklist.md) · [security testing guide](../testing/security-testing-guide.md).
