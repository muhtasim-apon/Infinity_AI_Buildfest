# Security review - Phase 1 (identity, sessions, tenancy)
**Method (honest label):** adversarial re-read of the diff by the implementing assistant against the spec 19.4 checklist, plus tests. It is not an independent human review and the built-in `/security-review` has not been run: run it and append its output.

## Evidence
Authz matrix 204 cases (every route x 7 principals; a route without an entry fails); IDOR/mass-assignment (422)/CSRF/cookie flags/uniform errors/timing (<50 ms median gap)/lockout/OTP/TOTP replay/recovery/step-up/invite-only/log redaction/injection corpus tests; audit chain under 8 concurrent writers; schemathesis 29 operations, zero 5xx; bandit and forbidden-pattern checks clean; 7 real-browser journeys.

## Found and fixed during the work
1. Audit hash chain restarted at genesis for non-admin inserts (trigger could not see the previous row under RLS) and could misorder under concurrency -> fixed in migration 0002 (SECURITY DEFINER tail lookup, id assigned under the lock).
2. A wrong OTP logged the user out (session dropped before verification) -> drop only after success.
3. Weak new password burned the reset code/token -> policy checked before consuming.
4. Shared demo users: "sign out everywhere" and the device list would have hit other visitors -> scoped to the caller's session.
5. `CG_ENV=test` (test router, CAPTCHA bypass) could run on a hosted service -> refused when `RENDER` is set.
6. Registration/OTP responses differed by account state (429 only for pending) -> same limits spent in every branch.
7. `return_to` ignored after sign-in by a redirect race (functional; open-redirect validation was already in place).

## Residual risks
| # | Risk | Status |
|---|---|---|
| P1-1 | An attacker can lock a victim's login for 15 min with 10 bad attempts (availability trade-off) | accepted |
| P1-2 | First-login 2FA enrolment: someone holding a new staff password before its owner signs in could enrol their own authenticator | accepted; invite links are single use and 72 h |
| P1-3 | Per-IP limits are only as good as `TRUSTED_PROXY_HOPS` | open: must be 1 on Render |
| P1-4 | Unknown-phone OTP verify is slightly cheaper than known-phone | accepted |
| P1-5 | Local TLS check in smoke test skipped on loopback only | accepted |
| R7 | Phase 0 DB password / secret key exposure | **RESOLVED 2026-10-21 (owner-attested)**, see phase-00.md |
| R11 | Render API key pasted in chat | **RESOLVED 2026-10-21 (owner-attested)**, see phase-00.md |
| R12 | `SECRET_KEY` passed through chat; sessions now depend on it | **RESOLVED 2026-10-21 (owner-attested)**: owner reports `SECRET_KEY` was rotated on Render. The assistant cannot verify the value; it only observed the hosted API healthy afterwards |
| R6 | Supabase role-membership grant may be refused for the pooler user | **VERIFIED 2026-10-21** on the hosted DB: `postgres` is a member of `cg_app`, `cg_worker`, `cg_readonly` (`pg_auth_members`). Not yet re-run: `check_rls.py` against Supabase |
| R13 | Found on the hosted DB after applying 0002: `audit_tail_hash()` (SECURITY DEFINER) was executable by `anon`/`authenticated` via PostgREST, because 0002 revoked function access before creating it and Supabase grants new functions to those roles directly. Leaks only the latest audit hash | **RESOLVED 2026-10-21**: revoked on the live DB (advisor now clean of it); migration 0003 repeats the revoke and sets default privileges so fresh deployments are covered |
| R14 | `vector` extension is installed in `public` (Supabase advisor `extension_in_public`, WARN) | accepted: schema-qualified use is not needed yet; revisit when embeddings are used in Phase 5 |
