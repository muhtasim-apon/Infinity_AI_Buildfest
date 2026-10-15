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
| AuthN | Supabase Auth (phone OTP / email), short-lived JWT, refresh rotation |
| AuthZ | Role claims (farmer, agronomist, admin) + Postgres Row-Level Security |
| Transport | HTTPS only (Render and Supabase terminate TLS); HSTS; strict CORS allow-list |
| Uploads | signed URLs, 5 MB cap, MIME + magic-byte check, re-encode, EXIF strip |
| Secrets | Render environment groups; never committed; `.env.example` only |
| Rate limiting | per-user and per-IP token bucket on scan and advisory endpoints |
| Audit log | append-only `audit_log` table, hash-chained rows |

## Responsible-AI security
Prompt injection is an untrusted-input problem. Retrieved documents and user text are
wrapped as data, never instructions; the agent has no write tools except `create_alert_draft`,
which requires agronomist approval. See `docs/ai/agent-design.md` and `tests/security/`.
