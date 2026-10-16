# Other platforms — only the five we need

Used by [00](00-zero-to-deploy.md). Everything else (n8n, Sentry, Telegram, custom domain) waits until
after 31 Oct.

## 1. GitHub (Apon · Day 1)
- Settings → Collaborators: add Taeen, Salwa, Raisa, Sara.
- Settings → Code security: **Dependabot alerts** and **secret scanning** on (checklist items "update
  vulnerable packages" and no leaked secrets).
- Settings → Branches → protect `main`: pull request + 1 approval.
- Before opening a PR, run `/security-review` in Claude Code (checklist item "Claude security review").
- Make the repository **public on 30 Oct**.

## 2. Anthropic API key (Raisa · Day 1)
console.anthropic.com → Billing → set a **monthly spend limit** first → API Keys → create
`cropguardian-prod` → paste into Render as `ANTHROPIC_API_KEY`. Never paste keys in chat or commit them.
Advice is cached per disease, so normal usage stays small.

## 3. Cloudflare Turnstile — CAPTCHA (Apon · Day 2)
dash.cloudflare.com → **Turnstile** → Add widget → hostnames: `cropguardian-web.vercel.app`,
`cropguardian-prototype.vercel.app` (the exact Vercel hosts) and `localhost` → mode **Managed** →
- **site key** → Vercel web env `VITE_TURNSTILE_SITE_KEY`;
- **secret key** → Supabase (Bot and Abuse Protection) **and** Render API env `TURNSTILE_SECRET_KEY`.

## 4. UptimeRobot — keep-alive + alerts (Apon · Day 10)
New monitor → HTTP(s) → `https://cropgurdian-backend.onrender.com/readyz` → the shortest free interval
→ alert contact = team email. Add monitors for the two Vercel URLs (alerts only — Vercel doesn't sleep). Pause the API monitor only if
Render's usage email warns about instance hours (one always-on free service uses almost all 750 hours).

## 5. Google Colab / Kaggle — training (Taeen · Days 1–10)
Use a GPU notebook; save a checkpoint every epoch to Drive / Kaggle output (sessions end without warning);
use only the public datasets listed in [`external-resources.md`](../research/external-resources.md).
