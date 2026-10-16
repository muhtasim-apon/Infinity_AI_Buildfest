# Security Policy

## Scope
Crop Guardian stores farmer phone numbers, approximate field locations and crop photos.
Photos can carry GPS EXIF data and faces. Every component is in scope.

## Reporting a vulnerability
Report privately to Apon (security owner, see `.github/CODEOWNERS`). Do not open a public
issue. Acknowledgement within 48 h; remediation plan within 7 days.

Do not test against any environment you do not own. Congress §20.11 prohibits malware,
exploiting vulnerabilities and interfering with event infrastructure.

## Security posture summary

| Control | Specified in |
|---|---|
| Threat model (STRIDE) | `docs/security/threat-model.md` |
| OWASP Top 10 + OWASP LLM Top 10 mapping | `docs/security/owasp-mapping.md` |
| Privacy (EXIF strip, coarse geo, consent, retention) | `docs/security/privacy.md` |
| Data sovereignty | `docs/data/data-sovereignty.md` |
| Audit readiness | `docs/security/audit-readiness.md` |
| AuthN | Supabase Auth — email OTP / magic link now; phone OTP later (needs a paid SMS provider); short-lived JWT, refresh rotation |
| AuthZ | Roles (farmer, admin, demo) read from the database on every request + Postgres Row-Level Security |
| Transport | HTTPS only (Render and Supabase terminate TLS); HSTS; strict CORS allow-list |
| Uploads | signed URLs, 5 MB cap, MIME + magic-byte check, re-encode, EXIF strip |
| Secrets | typed into each Render service's Environment tab (never in env groups or files); never committed; `.env.example` lists names only |
| Rate limiting | per-user and per-IP token bucket on scan and advisory endpoints |
| Audit log | append-only `audit_log` table, hash-chained rows |

## Responsible-AI security
Prompt injection is an untrusted-input problem. Retrieved documents and user text are
wrapped as data, never instructions; the agent has read-only tools only. Full 19-point checklist:
`docs/security/security-checklist.md`. Tests: `tests/security/`.
