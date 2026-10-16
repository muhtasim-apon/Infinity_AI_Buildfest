# Other platforms guide — GitHub, Anthropic, Cloudflare, ML compute, n8n, monitoring, Telegram, domain

Order of work: [`00-zero-to-deploy.md`](00-zero-to-deploy.md). Render: [`01`](01-render-guide.md) ·
Supabase: [`02`](02-supabase-guide.md).

## 1. GitHub (Apon)
| Setting | Where | Value |
|---|---|---|
| Collaborators | Settings → Collaborators | 4 members, Write |
| Branch protection | Settings → Branches → `main` | PR required, 1 CODEOWNER approval, required checks, no force-push |
| Dependabot alerts + security updates | Settings → Code security | on (checklist: update vulnerable packages) |
| Secret scanning + push protection | Settings → Code security | on |
| Actions approval | Settings → Actions → General | require approval for external contributors |
| Repository secrets | Settings → Secrets and variables → Actions | `API_BASE_URL`, `N8N_WEBHOOK_SECRET`, `CLAUDE_API_KEY` |
| Visibility | Settings → General | private while building → **public by 30 Oct** |
CI workflows to create are specified in [`.github/README.md`](../../.github/README.md).

## 2. Anthropic Console (Raisa / Salwa)
1. console.anthropic.com → organisation → **Billing**: add credit, set a **monthly spend limit** first.
2. **API keys** → create `cropguardian-prod` (Render) and `cropguardian-dev` (local) — never share keys
   in chat or commit them; rotate if exposed.
3. A separate key for the Claude security-review GitHub Action (`CLAUDE_API_KEY`) — it must be enabled
   for both the Claude API and Claude Code.
4. Keep usage low: cache advice per (disease, crop, stage, KB version); max 1,500 output tokens; 20 s timeout.

## 3. Cloudflare Turnstile — CAPTCHA (Apon)
1. dash.cloudflare.com → **Turnstile** → **Add widget** → name `cropguardian` → hostnames: the web app
   (U2), prototype (U1), custom domain if any, and `localhost` → mode **Managed**.
2. Copy the **site key** → `VITE_TURNSTILE_SITE_KEY` (public) and the **secret key** →
   Supabase Auth CAPTCHA setting **and** API `TURNSTILE_SECRET_KEY`.
3. Used on: sign-in / sign-up / password reset (Supabase Auth) and the public demo-session endpoint (API).

## 4. ML compute — Google Colab and Kaggle (Taeen)
| | Google Colab | Kaggle Notebooks |
|---|---|---|
| GPU | free GPU when available | free GPU after phone verification |
| Sessions | disconnect after idle / runtime limits | time-limited sessions with weekly GPU quota |
| Data | Google Drive mount | upload datasets as private Kaggle datasets |
| Use for | quick experiments | longer training runs |
Rules: checkpoint every epoch to Drive / Kaggle output (sessions end without warning); fixed seeds;
log configs; never upload user data — only the public datasets. Exact quotas change — check each site.

## 5. n8n — automation (Apon, Taeen)
| Option | Pros | Cons | Use when |
|---|---|---|---|
| **n8n Cloud trial** | public HTTPS webhook URL, schedules run 24/7, no setup | trial ends; then paid | demo window (late Oct – Dec) |
| **Self-host with Docker on a laptop** | free | runs only while the laptop is on; webhook needs a tunnel | development |
| Self-host on a small always-on VM | free/cheap, 24/7 | you maintain it | longer term |

Self-host for development:
```powershell
docker volume create n8n_data
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```
Open `http://localhost:5678`, create the owner account. Then: **Credentials** → Telegram bot token;
an "API signing secret" stored as an n8n credential/variable; build workflows 01–08 from
[`automation/n8n/`](../../automation/n8n/README.md); copy the production webhook URL of workflow 01 into
the API env `N8N_ALERT_WEBHOOK_URL`. If n8n is down the app still works — only notices, digests and
monitors pause (fallbacks in §6).

## 6. Monitoring & keep-warm (Apon)
| Tool | Setup | Purpose |
|---|---|---|
| **UptimeRobot** (or cron-job.org) | HTTP monitor on `<API>/healthz`, and on U1, U2; alert contact = team email / Telegram | uptime alerts; keep-warm pings during demo windows (pause outside them to save instance hours) |
| **GitHub Actions heartbeat** | daily cron (spec in `.github/README.md` §3) | Supabase never pauses even if n8n is down |
| **n8n workflow 05** | synthetic end-to-end check | functional smoke test of the deployed stack |
| **Sentry** (optional, free tier) | create a Python project → DSN → API env `SENTRY_DSN` | error tracking with stack traces (scrub PII) |
| Render metrics + usage emails | dashboard | memory, bandwidth, instance hours |

## 7. Telegram team channel (Raisa)
1. Telegram → @BotFather → `/newbot` → name `CropGuardianOpsBot` → copy the bot token (secret → n8n only).
2. Create a private group "Crop Guardian Ops", add the bot, send a message, get the chat id via the
   bot API `getUpdates` → store in n8n.
3. Only operational notices go here (alerts published, monitors, digests) — never personal data.

## 8. Custom domain (optional, Apon)
Buy a cheap domain from any registrar (or use one the team owns) → manage DNS (Cloudflare DNS is free)
→ CNAME `app`, `api`, `demo` to the Render hosts as shown in Render → wait for TLS → update the URL plan
everywhere (CORS, Supabase redirect URLs, Turnstile hostnames, CSP, monitors, submission). Benefit:
if Render suspends a service, re-point the CNAME to a backup host without changing any shared link
([challenges §H](04-free-tier-challenges.md)).

## 9. Security & test tooling (all)
| Tool | Install / use | Purpose |
|---|---|---|
| Claude Code `/security-review` | run in Claude Code before opening a PR | security review of local changes |
| `claude-code-security-review` Action | `.github/README.md` §2 | automatic PR security review |
| OWASP ZAP | Docker image `ghcr.io/zaproxy/zaproxy:stable`, baseline scan against **staging** | DAST |
| gitleaks | GitHub Action or `docker run zricethezav/gitleaks` | secret scanning |
| pip-audit / npm audit / Bandit | in CI | dependency & static checks |
| securityheaders.com, Mozilla Observatory | browser | header grade |
| Postman / Newman, Schemathesis, k6, Playwright | see `docs/testing/test-links.md` | API, load, E2E |
