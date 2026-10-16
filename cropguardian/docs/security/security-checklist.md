# Security checklist — the 19 controls from the checklist image (+ Crop Guardian extras)

Source of the 19 items: the team's security checklist image (`received_1631649765008129.webp`).
Every row says **what it means**, **how Crop Guardian does it**, **where it is configured**, the
**owner**, and the **test that proves it** (IDs from [`tests/`](../../tests/README.md)). Tick the box only
when the test passes on the deployed system. How to run each test per platform:
[`security-testing-guide.md`](../testing/security-testing-guide.md).

| # | Control | What it means | How we do it | Where configured | Owner | Proved by | ✓ |
|---|---|---|---|---|---|---|---|
| 1 | **Row level security** | The database itself refuses rows a user may not see, even if app code is wrong | RLS **enabled on every table**; one-line ownership policies; role via SECURITY DEFINER `app_role()`; Security Advisor clean | Supabase (migration `0002_rls.sql`) · [`db/SCHEMA-SPEC.md`](../../db/SCHEMA-SPEC.md) §4 | Apon | S7, S8, S9 | ☐ |
| 2 | **Auth on every API route** | No endpoint works without a valid identity, except health and demo entry | JWKS-verified Supabase token on every `/v1/*` route except demo session; deny by default; `exp`/`aud` checked; `alg:none`/HS256 rejected | API `security/auth.py` | Apon | S1–S4 | ☐ |
| 3 | **Never trust the frontend** | Everything from the browser is untrusted; the server re-checks | server-side validation (Pydantic), server-side role check from DB, server-side image re-encode, server-side CAPTCHA verify; UI hiding is never a control | API (all routers) | Apon | S4, S5, BB1–BB10 | ☐ |
| 4 | **Rate limiting** | Stop brute force, spam and cost abuse | token bucket per user and per IP: scans 30/h, advice 60/h, demo 10/min/IP; daily LLM token budget; Supabase Auth rate limits | API `security/ratelimit.py` · Supabase Auth settings | Apon | S15, CC3 | ☐ |
| 5 | **Sanitize user input** | Reject or neutralise bad input before use | strict schemas (types, ranges, lengths, patterns); coarse-location rule; farmer questions wrapped as data for the LLM; output rendered as plain text | API schemas · `rag/prompt.py` · web rendering | Apon, Salwa | BB1–BB10, S21, RT1–RT7 | ☐ |
| 6 | **Parameterized queries** | No SQL built by string concatenation | asyncpg/SQL parameters only; no dynamic SQL; Bandit in CI | API `db.py` and all services | Apon | S26 (Schemathesis injection payloads), Bandit | ☐ |
| 7 | **Lock down CORS** | Only our web app may call the API from a browser | `allow_origins = [APP_BASE_URL]` (+ localhost in dev); explicit methods/headers; no `*`; no credentials mode | API `main.py` · Render env `APP_BASE_URL` | Apon | S22 | ☐ |
| 8 | **HTTPS everywhere** | No plain-HTTP traffic | Vercel, Render and Supabase serve TLS only; HSTS header on web and API; all URLs in the URL plan are `https://`; custom domain gets automatic TLS | `vercel.json` headers · API `security/headers.py` | Apon | S23, Render checklist §11 | ☐ |
| 9 | **Stop IDOR bugs** | Changing an id in a URL must not expose someone else's data | ownership check in every service function **and** RLS; other users' ids return 404 | API services · Supabase RLS | Apon | S6, S7 | ☐ |
| 10 | **Debug mode off in prod** | No stack traces, docs or verbose errors in production | `ENVIRONMENT=production` disables `/docs` + `/openapi.json`; problem+json errors without internals; log level info; source maps off | Render env · API `main.py` · web build | Apon, Sara | S24 | ☐ |
| 11 | **CAPTCHA on public forms** | Bots cannot create accounts or spam public endpoints | Cloudflare Turnstile on Supabase sign-in/sign-up/password reset **and** on the public demo-session endpoint (verified server-side) | Cloudflare · Supabase Auth → Bot and Abuse Protection · API `security/captcha.py` | Apon | S14, E1 | ☐ |
| 12 | **Log admin actions** | Every privileged change is recorded and tamper-evident | hash-chained `audit_log` via `audit_append`; reason required for settings, model activation, role change, alert dismiss; visible in `/audit`; nightly chain verification | DB function · API `services/audit_chain.py` · n8n workflow | Apon | S10, S11, CC4, IT5, IT6 | ☐ |
| 13 | **Private storage buckets** | Photos and models are never publicly readable | buckets `scans`, `models` private; 5-min signed upload URLs; owner-only signed downloads; MIME + size limits on the bucket | Supabase Storage | Apon | S25 | ☐ |
| 14 | **Hide admin pages properly** | Admin access is enforced by the server, not by hiding links | admin API routes require role admin (from DB); admin UI is a lazy chunk loaded only after the API confirms the role; `noindex`; RLS restricts admin tables | API `require_role("admin")` · web `/admin` · RLS | Apon, Sara | S5, E7 | ☐ |
| 15 | **Update vulnerable packages** | Known-vulnerable dependencies are found and fixed fast | Dependabot alerts + weekly version PRs; `pip-audit`, `npm audit` in CI; pinned versions; base image updates | GitHub settings · CI | Apon | S28 | ☐ |
| 16 | **Check file upload types** | Only real images of allowed types and size | client re-encode + server magic-byte check (JPEG/PNG/WebP), 5 MB cap, pixel cap, decode check, **re-encode to JPEG** (drops EXIF/GPS and polyglot payloads); bucket MIME allow-list | API `security/upload.py` · Supabase bucket settings | Apon | WB-U1–U11, S16 | ☐ |
| 17 | **Claude security review** | An AI security review of every change before merge | Claude Code `/security-review` before opening a PR; `anthropics/claude-code-security-review` GitHub Action comments on PRs (trusted PRs only — it is not hardened against prompt injection) | developer machine · GitHub Actions (`CLAUDE_API_KEY`) | Apon, Salwa | PR comments on every PR | ☐ |
| 18 | **Security headers** | Browsers enforce safe defaults | CSP, HSTS, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `X-Frame-Options: DENY` / `frame-ancestors 'none'`, `Permissions-Policy` | `prototype/vercel.json` + `apps/web/vercel.json` · API headers | Apon | S23, securityheaders.com | ☐ |
| 19 | **Verify webhook signatures** | Only n8n (with the shared secret) can trigger hooks | HMAC-SHA256 over `timestamp.body`, constant-time compare, 5-min window, replay cache; same scheme for API → n8n | API `security/webhook_sig.py` · n8n Function node | Apon | WB-W1–W6, S12 | ☐ |

All 19 items in the image are covered one-to-one by rows 1–19.

## Crop Guardian extras (beyond the image)
| # | Control | How | Proved by |
|---|---|---|---|
| X1 | Secrets never in code or bundles | Render/GitHub secrets only; CI grep for `sb_secret_`; GitHub push protection; no secrets in Docker build | S27 |
| X2 | No personal data to the LLM or logs | typed prompt builder; log scrubber; audit `scrub()` | S18 |
| X3 | Prompt-injection resistance | sources and questions wrapped as data; read-only agent tools; validator V1–V6 | RT1–RT8, S19 |
| X4 | Model integrity | SHA-256 check at boot | S17, IT9 |
| X5 | Privacy by design | EXIF strip, coarse location, purpose consent, deletion within 7 days | WB-U10, privacy.md |
| X6 | Abuse of public alerts | alerts only from rules; conservative thresholds + cooldown; unverified label; admin kill-switch | WB-O1–O10, IT5 |

## Release gate
Before 28 Oct (code freeze): every row ticked on **staging**; before 30 Oct: rows re-checked on the
**production URLs** ([`00-zero-to-deploy.md`](../deployment/00-zero-to-deploy.md) Step 9).
