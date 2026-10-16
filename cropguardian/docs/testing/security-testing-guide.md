# Security testing guide — how to test every control, per platform

What to prove: [`security-checklist.md`](../security/security-checklist.md) (19 controls + extras) and
[`threat-model.md`](../security/threat-model.md). Case tables: [`tests/security/`](../../tests/security/README.md),
[`tests/whitebox/`](../../tests/whitebox/README.md), [`tests/blackbox/`](../../tests/blackbox/README.md).
Rules: test only systems we own; run scanners and load against **staging**; use synthetic accounts;
never paste real secrets into tickets or chats (Congress §20.11).

## 1. Schedule
| When | What runs | Who |
|---|---|---|
| Before every PR | Claude Code `/security-review`; unit + whitebox tests locally | author |
| Every PR (CI) | lint, Bandit, pip-audit, npm audit, gitleaks, frontend secret grep, unit + whitebox, Claude security-review Action | automatic |
| Nightly (staging) | blackbox (Schemathesis), integration, timeout, E2E, synthetic monitor | automatic / Apon |
| Pre-release (25–28 Oct) | full `tests/security` table, OWASP ZAP baseline, RLS + IDOR manual pass, header grade, LLM red-team, Supabase Security Advisor | Apon, Salwa |
| After deploy to production (29–30 Oct) | re-check rows 1–19 on production URLs, phone + logged-out checks | Apon, Sara |

## 2. Test environments
| Env | Web | API | Database |
|---|---|---|---|
| local | `localhost:5173` | `localhost:8000` | staging Supabase project or local Postgres |
| staging | second static site or local build | second Render workspace / local Docker | second free Supabase project |
| production | U2 | U3 | main Supabase project — **no scanners, no load tests** |

## 3. Supabase (RLS, storage, auth)
1. **Security Advisor** (Advisors tab): zero errors — checklist #1.
2. **RLS as a user** (S7, S8): with supabase-js and the **publishable key**, sign in as demo user A, try
   `select * from scans` → only A's rows; try `update profiles set role='admin' where id = auth.uid()` →
   rejected. Repeat as user B against A's ids → 0 rows.
3. **Anonymous access** (S9, S25): without signing in, select from `scans`, `diagnoses`, `audit_log` → 0
   rows / denied; open a `scans` or `models` object URL without a signed token → denied.
4. **Audit log immutability** (S10): as an authenticated user, `update`/`delete` on `audit_log` → denied.
5. **CAPTCHA** (S14): sign-up without the Turnstile token → rejected by Supabase.
6. **Auth rate limits**: request OTP emails repeatedly → limited.

## 4. API (auth, IDOR, input, rate limits, webhooks)
Use Postman/Newman or `curl` against staging:
| Test | Request | Expected |
|---|---|---|
| no token (S1) | `GET /v1/scans` | 401 problem+json |
| expired / tampered / `alg:none` token (S2, S3) | modify the JWT | 401 |
| role from DB (S4) | token of a farmer whose profile says farmer | farmer only |
| admin routes (S5) | farmer → `GET /v1/admin/settings` | 403 |
| IDOR (S6) | farmer B → `GET /v1/scans/<A's id>` | 404 |
| input (BB1–BB10) | boundary values from the blackbox table | 422 for invalid, 2xx for valid |
| injection (S26) | `schemathesis run <staging>/openapi.json --checks all` | no 5xx, no schema violations |
| rate limit (S15) | 11 demo sessions/min from one IP; 31 scans/hour | 429 + `Retry-After` |
| uploads (S16) | renamed HTML, SVG, pixel bomb, GPS JPEG | 415/422 or clean re-encoded JPEG without EXIF |
| webhook (S12) | `POST /v1/hooks/n8n/heartbeat` unsigned, bad signature, replayed | 401, no side effect |
| CAPTCHA on demo (S14) | `POST /v1/demo/session` without token | 400/403 |
| debug off (S24) | `GET /docs`, `/openapi.json` on production; trigger a 500 on staging | 404; error body has no stack trace |
| CORS (S22) | `curl -H "Origin: https://evil.example" -I <API>/healthz` | no `Access-Control-Allow-Origin` |

## 5. Render & browser (HTTPS, headers, admin pages)
1. **HTTPS** (#8): open `http://` versions of U1–U3 → end on `https://`; HSTS present.
2. **Headers** (#18, S23): check U1, U2, U3 on securityheaders.com and Mozilla Observatory; fix missing
   CSP / nosniff / frame-ancestors / referrer policy.
3. **OWASP ZAP baseline** (staging only):
   `docker run -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t <staging web URL> -r zap-report.html`
   → no High alerts; record Medium alerts with a decision.
4. **Admin pages** (#14, S5, E7): as a farmer open `/admin` → nothing rendered; DevTools Network shows
   the API returned 403 and the admin JavaScript chunk was not downloaded.
5. **Secrets in the bundle** (S27): DevTools → Sources → search the built JS for `sb_secret_`, `SECRET`,
   `sk-` → nothing.

## 6. GitHub (dependencies, secrets, AI review)
1. **Dependabot** (#15, S28): Security tab → no open high/critical alerts; merge update PRs weekly.
2. **pip-audit / npm audit**: in CI; locally `pip-audit -r requirements.txt`, `npm audit --audit-level=high`.
3. **gitleaks** (S27): CI job; locally `docker run -v ${PWD}:/repo zricethezav/gitleaks detect -s /repo`.
4. **Claude security review** (#17): Claude Code → `/security-review` on your branch before the PR; the
   GitHub Action comments on the PR — resolve or justify every comment before merging.

## 7. LLM / RAG (prompt injection, unsafe advice)
Run [`red_team_cases.md`](../../tests/security/red_team_cases.md) RT1–RT8 against staging with a **test**
knowledge base containing one poisoned chunk. Gate: 0 failures. Also verify: citation coverage 1.00 and
banned-ingredient leakage 0 on the golden set ([`eval-plan.md`](../ai/eval-plan.md) §3); no personal data in
captured LLM requests (S18).

## 8. Automation (n8n)
Unsigned / replayed webhook calls are rejected (S12); workflow logs contain no emails or coordinates;
credentials exist only inside n8n (not in exported JSON).

## 9. Load & availability (careful on free tiers)
k6 / Locust only against **staging**, short runs (≤ 10 min, ≤ 20 virtual users): Render may suspend a
free service for unusually high outbound traffic, and bandwidth overruns can suspend all free services
([`04-free-tier-challenges.md`](../deployment/04-free-tier-challenges.md) A3, A5).

## 10. Recording results
For every run: date, environment, commit, tool, result, link to report, decisions on findings. Put the
summary in the `/audit` report and tick the matching rows in the security checklist. Findings → GitHub
issues labelled `security` (private details stay out of public issues — use a private channel).
