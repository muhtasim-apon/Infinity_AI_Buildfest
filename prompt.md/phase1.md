 Updated plan
  ⎿  /plan to preview

────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
 Ready to code?

 Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Plan: Phase 1 — Identity, sessions, tenancy, security core — every team member's P1 work, built by one person

 Who does what for Phase 1 (Gantt PDF re-read pp. 2–23, spec Phase 1 + s2, s7.1, s8.4, s12, s14, s16.4–16.15, s19.4)

 ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┬──────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────┐
 │                                                   Role                                                   │      Gantt item that touches P1      │                                     What I build here                                     │
 ├──────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │ Apon (owner, "Salwa reviews")                                                                            │ Sun 18 P1: models, RLS, core         │ everything backend/DB below; make gate PHASE=1                                            │
 │                                                                                                          │ security; Mon 19 P1 finish           │                                                                                           │
 ├──────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │                                                                                                          │ Mon 19 "review Apon's P1 PRs         │ an independent adversarial review pass of the P1 diff with the s19.4 checklist →          │
 │ Salwa                                                                                                    │ (security reviewer)"                 │ docs/security-reviews/phase-01.md (honest limit: same assistant, so it is a separate      │
 │                                                                                                          │                                      │ checklist-driven re-read + extra attack tests, not a second human)                        │
 ├──────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │                                                                                                          │ P1 build #6 (functional frontend)    │ fetch wrapper, route guards, login / TOTP / register / verify / forgot-reset / demo role  │
 │ Sara                                                                                                     │ and Mon 19 "P2: shells + route       │ picker, placeholder role homes, DEMO ribbon, 403/404 pages; only the few form elements    │
 │                                                                                                          │ guards" — only the guard/auth part   │ those pages need (no design-system build-out)                                             │
 ├──────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │                                                                                                          │ s14 notification wording, s16.17     │ Bangla (source) + English strings for all P1 screens/errors, OTP/SMS and email templates  │
 │ Raisa                                                                                                    │ consents (versioned Bangla text),    │ (bilingual, autoescaped), consent texts v1 (service, training_use, push_alerts),          │
 │                                                                                                          │ Bangla copy for auth screens         │ new-device notice; reviewed against docs/BANGLA_STYLE.md                                  │
 ├──────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │ Taeen                                                                                                    │ none (no P1 task in the Gantt)       │ nothing                                                                                   │
 ├──────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │ Not built (belongs to other phases): P2 primitives/shells/landing/3D/i18n-lint build-out, P3             │                                      │                                                                                           │
 │ pHash/split, P5 ingestion, P6 prompt/golden Q&A, Monday's "begin fields/scans/diagnoses models" (P4),    │                                      │                                                                                           │
 │ notifications endpoints/Web Push (P8), admin console pages (P10), scans/ML/RAG.                          │                                      │                                                                                           │
 ├──────────────────────────────────────────────────────────────────────────────────────────────────────────┼──────────────────────────────────────┼───────────────────────────────────────────────────────────────────────────────────────────┤
 │ Phase-1 acceptance: gate PASS; no route without an authz-matrix entry. Corner case CC-32. Exit checks:   │                                      │                                                                                           │
 │ Sun 18 — authz matrix harness runs; check_rls.py passes on new tables. Mon 19 — make gate PHASE=1 →      │                                      │                                                                                           │
 │ PASS; farmer hitting /admin → 404.                                                                       │                                      │                                                                                           │
 └──────────────────────────────────────────────────────────────────────────────────────────────────────────┴──────────────────────────────────────┴───────────────────────────────────────────────────────────────────────────────────────────┘

 Hard facts that shape this plan

 - Gantt rule: a gate passes only after its dependencies' gates passed. P1 depends on P0, and P0's last two failing items are owner actions (rotate Supabase DB password + secret key; revoke the pasted Render key → R7/R11). So make gate PHASE=1
   will show every P1 step PASS but stop at "dependency gate 0 not passed" until the user rotates and I flip R7/R11 and re-run P0. I will not bypass that rule.
 - Hosted has no Redis; sessions/limits need it (auth fails closed 503 without it). Decision given: create a free Render Key Value (Singapore) and set REDIS_URL.
 - Supabase MCP session is stale (restart Claude Code); no Supabase write without an explicit "apply".
 - I never run git commit/git push; I list the exact files to commit.
 - Dev-compose Redis is "unhealthy" (P0 defect) — fixed first.

 Order of work (each step ends green before the next)

 0. Prerequisites: fix dev-compose Redis healthcheck; Redis service + env in the root CI workflow; pin/install argon2-cffi, pyotp, zxcvbn, cryptography, dev schemathesis, factory-boy; frontend react-router-dom@6, @tanstack/react-query@5,
 react-hook-form, zod, @hookform/resolvers, vitest-axe; re-run pip-audit/npm audit.

 1. Raisa — Bangla/English copy first (everything else consumes it): bn.json keys then en.json for login, TOTP, register, verify, OTP, forgot/reset, demo picker, errors (uniform login error, lockout, rate-limit, CAPTCHA, session expired,
 waking server), DEMO ribbon, role names; OTP SMS and email templates (verify/reset/invite/new-device) in backend/app/templates/; consent texts v1 in backend/app/core/consent_texts.py with text_version; additions to docs/BANGLA_STYLE.md.
 Marked "team-authored, not expert-reviewed". Tests: i18n completeness, ≤15-word sentences, danda, placeholders, templates autoescape.

 2. Apon — models + migration 0002_identity.py + RLS (Sun 18). Tables: users, sessions, otp_codes, email_tokens, totp_credentials, recovery_codes, consents, push_subscriptions (table only), invites, notifications, email_outbox; extend
 idempotency_keys (route, status_code, response_json per 7.1). UUID v7 ids, tenant_id check ('real','demo') + ownership column on every user-data table, ENABLE+FORCE RLS with policies per spec 16.10 (own rows; admin; SYSTEM where listed; every
 policy tenant-scoped; missing context matches nothing). Pre-auth lookups use a server-internal SYSTEM context that cannot be produced from request data (tested). Reversible (up/down/up) on real Postgres; no RLS exemptions.

 3. Apon — core security modules (Sun 18), each with tests and 100% branch coverage: core/ids.py · core/security.py (Argon2id t=3/m=64 MiB/p=2 + rehash, secrets tokens, SHA-256/HMAC, constant-time compare, AES-GCM via HKDF(SECRET_KEY),
 password policy farmer 8–128 zxcvbn ≥2 / staff 12–128 zxcvbn ≥3, bundled SecLists common-password list with attribution — honestly "common passwords", not HIBP) · core/redis.py · core/sessions.py (256-bit token, SHA-256 stored, Redis + DB
 fallback, rotation 15 min + 30 s grace, idle/absolute per role, list/revoke, logout-all) · core/csrf.py (__Host-cg_csrf, HMAC-bound, Origin/Referer) · core/ratelimit.py (Lua sliding window, every row of 16.8, Retry-After, fail closed 503 for
 auth/OTP/demo, fail open for reads) · core/authz.py (Principal incl. demo roles, @policy registry, authorize(), 404 not-owned / 403 wrong role / 404 admin area) · core/redirects.py · core/idempotency.py · core/captcha.py (ALTCHA-style HMAC
 proof-of-work, single use via Redis, honeypot, min fill 2 s, bypass only in CG_ENV=test) · core/tenancy.py · domain/phone.py (E.164, Bangla digits). core/config.py: SMS_PROVIDER, EMAIL_PROVIDER (console|disabled|http), DEMO_ENABLED,
 DEMO_SEED_ON_START, CAPTCHA_BYPASS, PUBLIC_ORIGIN, plus production refusals (16.14).
 Sun 18 exit: authz matrix harness runs (backend/tests/security/authz_matrix.yaml; harness iterates every OpenAPI route × principals) and check_rls.py passes on all new tables.

 4. Apon — endpoints, scripts, test router (Mon 19), /api/v1, extra="forbid", problem+json, role-shaped outputs: GET /captcha/challenge; GET /auth/csrf; POST /auth/register/farmer, /auth/register/staff (invite only); /auth/otp/send|verify;
 /auth/email/verify|resend; /auth/login, /auth/login/totp, /auth/step-up; /auth/logout, /auth/logout-all; /auth/password/forgot|reset|change; /auth/totp/setup|confirm, /auth/recovery-codes; GET/PATCH /me, GET/DELETE /me/sessions[/{id}],
 GET/PUT /me/consents; POST /demo/session; minimal admin skeleton GET /admin/users, POST /admin/invites (admin + TOTP + step-up) so "farmer → /admin → 404" and invite acceptance are real. Behaviour per 16.4: uniform errors + dummy-hash timing,
 progressive delay after 5 failures, 15-min lock after 10/h, adaptive CAPTCHA after 3, OTP 6 digits HMAC-stored (5 min, 5 attempts, 60 s resend, 5/h), email tokens single-use (24 h/30 min; reset revokes all sessions), forced staff TOTP
 (AES-GCM, ±1 step, replay blocked, 10 Argon2id recovery codes), step-up 10 min, new-device notification row, demo sessions bound to tenant_id='demo'. services/auth.py, users.py, demo.py; providers console/disabled/http + email_outbox.
 Scripts: create_admin.py (prints TOTP URI once); seed.py (demo users now; the "base catalog/stages/areas" part needs P4 tables — recorded as a DECISIONS deviation, not faked); DEMO_SEED_ON_START idempotent and non-fatal if schema absent.
 __test__ router only when CG_ENV=test, startup assertion; boot tests prove each production refusal. /health/ready also checks Redis.

 5. Sara — functional frontend (P1 build #6 + guard part of Mon 19): src/lib/api.ts (same-origin credentials, CSRF header, 15 s abort, 401→login with validated return_to, 403 toast, 429 Retry-After, 503 waking UI), router + route guards (spec
 15.4: unauthenticated → /login?return_to=…, wrong role → /403, admin → /404, PENDING → /verify, staff without TOTP → /setup-2fa, demo ribbon), pages: login, TOTP step, register, verify, forgot/reset, demo role picker, placeholder role homes,
 403/404; admin code in a lazy chunk (non-admins never request it); language toggle; token-based markup using only the form elements these pages need. Tests: wrapper (MSW), guards, Zod forms, return_to validation, axe on these pages.
 CC-40-style long-Bangla-string check on the auth forms at 360 px.

 6. Salwa — security review (Mon 19): run the s19.4 checklist and extra attack tests against the finished diff (fixation, IDOR sweep, mass assignment, timing, CSRF matrix, cookie flags, RLS bypass attempts, tenant isolation, production
 refusals, redaction of cookies/OTP/TOTP in logs), fix every high/medium or justify, write docs/security-reviews/phase-01.md.

 7. Hosted (with confirmations): Render MCP — create free Key Value (Singapore, noeviction), set REDIS_URL, SMS_PROVIDER=disabled, EMAIL_PROVIDER=disabled, DEMO_ENABLED=true, DEMO_SEED_ON_START=true, PUBLIC_ORIGIN. Supabase — after Claude Code
 restart + MCP auth for elkhvfcawllyoearrxop: read-only look, then print target ref + exact SQL for 0001+0002 and wait for "apply"; then advisors + check_rls.py against it. New code reaches Render only when the user commits and pushes.

 Tests (by layer; every s19.4 item that applies to P1, incl. invalid input and permission failures)

 Unit/domain · hypothesis (redirect validator, token uniqueness, rate-limit window math, phone normalisation) · integration on real Postgres+Redis (RLS cross-user/cross-tenant via the repository layer, SYSTEM context unreachable from requests,
 session fixation/rotation/idle/absolute expiry, Redis-down → DB fallback + fail-closed limits) · API (every endpoint) · security (authz matrix, IDOR on {id} routes, mass assignment role/tenant_id/status/user_id/synthetic → 422, CSRF
 missing/wrong/foreign Origin, GET-sweep doesn't mutate via DB checksum, cookie flags, uniform errors + timing <50 ms over 50 samples, lockout, OTP expiry/attempts/resend, reset single-use, password policy, TOTP replay, recovery codes,
 step-up, invite-only staff, every 16.8 limit → 429 + Retry-After, headers/CORS/errors/host, CAPTCHA missing/expired/replayed/tampered/honeypot/min-fill, admin 404, production refusals, CC-32) · schemathesis (zero 500s) · frontend unit · E2E
 Chromium: farmer register → OTP via test router → home; staff invite → TOTP → console; lockout; logout-all invalidates another context; demo session → demo home; farmer /api/v1/admin/users → 404; admin bundle never requested by non-admins.

 Gate: make gate PHASE=1 (adds PHASE_CHECKS[1] to phase_gate.py)

 All P0 steps re-run + dependency check "P0 gate PASS" + register+verify+login API script (scripts/p1_smoke.py on the compose stack) + admin TOTP flow + 429 observed on login + audit chain verifies + check_rls.py + authz-matrix completeness +
 schemathesis + per-file coverage (100% branch on security/sessions/csrf/authz/ratelimit/redirects; backend ≥ 80%) + scanners (bandit, gitleaks, pip-audit, npm audit, forbidden/layers/honesty) + compose stack + edge checks + hosted /health,
 /health/ready.
 Manual check, run by me: register a farmer via console OTP; invite and log in a reviewer with TOTP; open /demo and enter each role; farmer → /api/v1/admin/users → 404.

 Documents I write/update

 docs/plans/phase-01.md (this plan with '18 Oct' and '19 Oct' sections), docs/security-reviews/phase-01.md, PROGRESS.md (one line per role-day: DONE/PARTIAL/BLOCKED), DECISIONS.md, docs/DEPLOYMENT.md (Redis, new env vars), docs/BANGLA_STYLE.md
 additions. /security-review itself is user-triggered; I say so.

 Risks and open items

 - P1 gate cannot print PASS until P0's R7/R11 are closed by the user. Everything else is demonstrated green first and the single blocker is named.
 - Cross-origin cookies: hosted SPA (Vercel) and API (Render) are different sites; __Host-/SameSite cookies need one origin → Vercel /api/* rewrite (to verify; SSE through it untested until P4). The public SPA stays a placeholder; judged paths
   run on the compose stack until then (DECISIONS item).
 - No SMS/email provider on the public demo (production refuses console): farmers use the one-click demo; staff accounts come from create_admin.py run by the owner.
 - SECRET_KEY (R12) feeds HKDF/session HMACs from now on: rotate before sessions go live on Render.
 - 100% branch coverage on six modules is the main effort risk; gaps are listed, never excluded silently.
 - Supabase pooler: app connects as postgres then SET LOCAL ROLE cg_app; role grants may be restricted on Supabase (0001 logs a NOTICE) — verified at apply time.

 Final checklist (Phase 1 done = every box with evidence)

 1. make gate PHASE=1 report saved; any remaining blocker named with its owner. 2) All 11 new tables ENABLE+FORCE RLS; check_rls.py green (local; Supabase advisors after apply). 3) Authz matrix covers every route. 4) 100% branch on the six
    core modules. 5) Register→OTP→login, staff invite→TOTP→console, lockout, 429, logout-all, demo session, admin 404 verified by script/E2E. 6) Production refusals proven. 7) Audit chain verifies after the flows. 8) Scanners clean. 9) Hosted
    /health, /health/ready (db + redis), demo-session smoke. 10) Copy (bn/en), consent texts, templates reviewed against BANGLA_STYLE. 11) Security review written, highs/mediums closed. 12) Docs/PROGRESS/DECISIONS updated; nothing committed by
    me; exact commit list given.
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
