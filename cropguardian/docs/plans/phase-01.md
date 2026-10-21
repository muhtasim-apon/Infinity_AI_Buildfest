# Phase 1 plan - Identity, sessions, tenancy, security core
One person builds every role's Phase 1 work. Out of scope: P2 design system, P3, P4 models, P5, P6, notifications endpoints, admin console.

## 18 Oct
Apon: migration 0002 + RLS, security core (Argon2id, sessions, CSRF, rate limits, CAPTCHA, authz), authz-matrix harness.
Raisa: Bangla/English auth copy, consent texts v1, SMS/email templates. Salwa/Taeen/Sara: none yet.
Exit: matrix harness runs; `check_rls.py` passes on the new tables.

## 19 Oct
Apon: endpoints, scripts, test-only router, gate steps. Sara: fetch wrapper, route guards, login/TOTP/register/verify/reset/demo, role homes, 403/404.
Salwa: security review -> `docs/security-reviews/phase-01.md`.
Exit: `make gate PHASE=1` PASS; a farmer on `/admin` gets 404.
