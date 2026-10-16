# Security tests

Owner: Apon (Salwa for LLM cases). One group per threat in [`threat-model.md`](../../docs/security/threat-model.md).
How to run every type, per platform: [`security-testing-guide.md`](../../docs/testing/security-testing-guide.md).
Checklist mapping: [`security-checklist.md`](../../docs/security/security-checklist.md). LLM red-team: [`red_team_cases.md`](red_team_cases.md).
Never scan or attack systems you do not own (Congress §20.11). Scanners run against **staging** only.

| ID | Threat | Case | Expected |
|---|---|---|---|
| S1 | auth | no `Authorization` header on any `/v1/*` route except demo | 401 problem+json |
| S2 | auth | expired token (1 s past `exp`) | 401 |
| S3 | auth | wrong audience / `alg: none` / HS256-signed token | 401 |
| S4 | auth | token claims admin but `profiles.role = farmer` | treated as farmer |
| S5 | admin pages | farmer calls each `/v1/admin/*` route | 403; nothing logged as admin action |
| S6 | IDOR | farmer B reads / analyzes farmer A's scan id | 404 (not 403 — no id probing) |
| S7 | RLS | publishable key, user A selects scans of user B | 0 rows |
| S8 | RLS | user updates own profile role → admin | rejected by WITH CHECK |
| S9 | RLS | every table in `public` has RLS enabled | true for all (also Supabase Security Advisor clean) |
| S10 | audit | UPDATE/DELETE on `audit_log` as authenticated | permission denied |
| S11 | audit | tamper one row (superuser), run verify | broken id reported |
| S12 | webhook | unsigned / bad signature / replayed request | 401, no side effect |
| S13 | demo | demo token reads real user data / changes settings | 0 rows / 403 |
| S14 | CAPTCHA | demo session without or with invalid Turnstile token | 400/403 |
| S15 | rate limit | 11 demo sessions/min from one IP; 31 scans/hour | 429 + Retry-After |
| S16 | upload | polyglot, renamed HTML/SVG, pixel bomb, GPS EXIF | rejected or re-encoded clean |
| S17 | model integrity | ONNX bytes differ from registered sha256 | not ready (503) |
| S18 | PII egress | capture LLM request body and logs during a full flow | no phone/email/name/precise location |
| S19 | agent | tool registry | read-only tools only; max 4 calls |
| S20 | RAG | retired document | never retrieved |
| S21 | XSS | `<script>` in farmer question and in a test KB chunk | returned as plain text; CSP header present |
| S22 | CORS | request from an origin other than the web app | no `Access-Control-Allow-Origin` |
| S23 | headers | web + API responses | CSP, HSTS, nosniff, Referrer-Policy, frame-ancestors none |
| S24 | debug | `GET /docs`, `/openapi.json` in production; error responses | 404; no stack traces |
| S25 | storage | anonymous GET on a `scans` or `models` object URL | denied (private buckets) |
| S26 | SQL injection | `' OR 1=1 --` style payloads in every string field (Schemathesis) | 4xx, never 5xx or data leak |
| S27 | secrets | gitleaks on repo history; grep web bundle for `sb_secret_` | nothing found |
| S28 | dependencies | pip-audit, npm audit, Dependabot alerts | no high/critical open |
