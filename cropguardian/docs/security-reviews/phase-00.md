# Security review — Phase 0 (17 Oct work, executed 2026-10-21)

**Method (honest label):** manual review by the implementing assistant plus tool output. The built-in
`/security-review` command has **not** been run on this diff — run it before the gate is considered signed off, and
append its output below. Scope: `backend/`, `infra/`, `docker-compose*.yml`, `frontend/` skeleton, `.github/`, `ml/` data
pipeline, `kb/`. Unresolved high items are marked **UNRESOLVED-HIGH** (the gate fails while that marker appears).

## Tool results
| Tool | Result |
|---|---|
| Bandit (`-ll`, backend/app) | no findings |
| `check_forbidden.py`, `check_layers.py`, `check_honesty.py` | 0 violations |
| `npm audit --omit=dev` (shipped dependencies) | 0 vulnerabilities |
| `npm audit` (all) | 0 critical, 5 high, 2 moderate — all in the Tailwind 3 build chain (`braces`, `micromatch`, `fast-glob`, `chokidar`, `postcss-selector-parser`); accepted with expiry 2026-11-30 in `frontend/scripts/audit-gate.mjs` (build-time, our own globs, no fix inside Tailwind 3). Vite/Vitest/esbuild/tinypool findings **fixed** by upgrading to vite 8 / vitest 5 (DECISIONS D-009) |
| `pip-audit` (backend + ml, OS trust store via `truststore`; verification on) | **0 known vulnerabilities** after fixes below. Before: 7 in `starlette 0.41.3`, 25 in `pillow 11.1.0` |
| gitleaks 8.30.1 (binary checksum verified) | **git history: 0 leaks in 7 commits; working tree: 0** (config `.gitleaks.toml` allow-lists only gitignored/third-party paths) |
| Real-Postgres tests (RLS, append-only, hash chain) | 11 passed; repeated run on a fresh DB: passed |
| Real Nginx edge checks (`infra/nginx/verify.sh`) | 16 / 16 passed; Chromium smoke through Nginx passed |

## Findings fixed during the work
0. **Vulnerable dependencies found by pip-audit**: `starlette 0.41.3` (7 advisories; FastAPI 0.115.6 pinned it) → FastAPI 0.156.4 + Starlette 1.9.0, all 141 tests still pass; `pillow 11.1.0` in the ML pipeline (25 advisories; it decodes untrusted dataset images) → Pillow 13.0.0, pipeline outputs byte-identical.
1. **Duplicate security headers** (Nginx + FastAPI both emitted CSP/HSTS) → Nginx now hides the upstream copies.
2. **Nginx config errors** caught only by running it (duplicate directives) → fixed; verified by the edge script.
3. **TLS key unreadable by the unprivileged Nginx user** → cert script sets permissions inside the generating container.
4. **Migration seeded `platform_settings` after `FORCE ROW LEVEL SECURITY`** (owner blocked) → seed now runs first.
5. **Tamper test polluted the shared DB** → now rolls back; the chain verifier is checked before and after.
6. Redis container could not start with `cap_drop: ALL` → run as UID 999.
7. Dev dependencies with critical advisories (`tinypool`, `vitest`) → upgraded.
8. Minimum-contrast failure in the specified `--text-subtle` colour → adjusted (DECISIONS D-007).
9. **Nginx kept proxying to a dead address after the API container was recreated (504)** → `depends_on: api: {restart: true}`; verified with `docker compose restart api`.
10. Stray throwaway private key and junk files from an early mount mistake → deleted; a fake JWT literal in a test is now built at runtime.
11. CI workflows would never have run (git root is the parent folder) → moved to the root `.github/` (DECISIONS D-013).

## Residual risks (accepted or open)
| # | Risk | Status |
|---|---|---|
| R1 | Dev compose / CI use fixed role passwords (`dev-api-pw`, `dev-migrator-pw`, `test-only-password`) in `infra/postgres/init/01-roles.sql`. Postgres is not published in dev compose and is bound to 127.0.0.1 in the test compose. These files must never be used for the hosted stack (Supabase gets NOLOGIN roles from the migration) | accepted, dev only |
| R2 | uvicorn's own access log is not redacted by our structlog processor and prints query strings | **FIXED**: `app/core/worker.py` sets `access_log=False` explicitly (gunicorn.conf.py uses it); tested in `tests/unit/test_worker_logging.py` (runs in CI/Linux; skipped on Windows because gunicorn is POSIX-only) |
| R3 | `/health` is public and returns process uptime | accepted (no sensitive data) |
| R4 | `X-Forwarded-For` is overwritten by Nginx; the app does not yet read client IPs (rate limiting arrives in Phase 1 and must honour `TRUSTED_PROXY_IPS`) | open for Phase 1 |
| R5 | RustFS (dev S3 store) is an unaudited young project, pinned by digest; dev/test only | accepted |
| R6 | Supabase role membership grant (`GRANT cg_app ... TO current_user`) may not be permitted for the pooler user; the migration logs a NOTICE and continues | open: verify on the hosted DB and re-run `check_rls.py` there |
| R7 | Team notes say the old Supabase DB password was weak and exposed together with a secret key via `.env.example`. **gitleaks finds nothing in the 7-commit git history**, so any exposure was outside git (a pasted terminal/chat, a dashboard screenshot, an earlier uncommitted draft). Cannot be verified from here | **UNRESOLVED-HIGH** until the owner rotates the DB password and secret key (steps in `docs/DEPLOYMENT.md`) and records the date here |
| R11 | A Render API key was pasted into this chat during MCP setup (with literal `<` `>` brackets, so possibly not even valid) | **UNRESOLVED-HIGH**: revoke it in Render → Account Settings → API Keys and add a new one without pasting it anywhere |
| R8 | Third-party skills: `webapp-testing/scripts/with_server.py` uses `shell=True` by design | accepted: local use only (documented in `.claude/skills/README.md`) |
| R9 | `ml/` data pipeline extracts third-party archives: zip-slip, symlink, ratio and size limits are enforced and tested; RAR extraction shells out to 7-Zip/unrar with fixed arguments and re-validates the result | accepted |
| R10 | KB documents are untrusted input; OCR/PDF parsing has no sandbox yet (Phase 5 adds parser time-outs, size limits) | open for Phase 5 |

| R12 | The Render `SECRET_KEY` was generated in an assistant session and passed through the chat | **ROTATE before sessions go live (Phase 1) and again for submission**: generate a new 64-hex value, set it in the Render dashboard, redeploy. It currently signs nothing |

## Not reviewed
`frontend` application code (placeholder only), auth/sessions/CSRF (Phase 1), upload pipeline (Phase 4), LLM paths
(Phase 6). Hosted stack configuration (not deployed).

## Sign-off
Gate rule: no unresolved high finding. **R7 and R11 are UNRESOLVED-HIGH** and only the owner can close them (rotate the Supabase
DB password and secret key, then change this entry to RESOLVED with the date). Until then the gate step
`6 security review` fails by design.
