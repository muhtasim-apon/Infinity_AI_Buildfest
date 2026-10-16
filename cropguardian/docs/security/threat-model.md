# Threat model (STRIDE)

Owner: **Apon** · Reviewed with Salwa (LLM threats). Assets: farmer PII (email, approximate
location), photos, diagnoses, KB integrity, model file integrity, alert channel, API keys,
availability during judging.

## Data-flow diagram trust boundaries
TB1 browser↔API · TB2 browser↔Supabase (publishable key) · TB3 API↔Supabase (secret key) · TB4 API↔LLM ·
TB5 n8n↔API · TB6 n8n↔team Telegram channel. See `docs/architecture/system-overview.md`.

| # | STRIDE | Threat | Boundary | Mitigation | Test |
|---|---|---|---|---|---|
| T1 | Spoofing | Stolen/forged JWT | TB1 | verify signature, `exp`, `aud`; short TTL; refresh rotation | S1–S4 |
| T2 | Spoofing | Forged n8n webhook triggers mass alert | TB5 | HMAC-SHA256 over body + timestamp, 5-min window, nonce cache | S12, WB-W1–W6 |
| T3 | Spoofing | Demo account abused as a real account / bot abuse of demo | TB1 | `demo` role: sandboxed writes, CAPTCHA, rate-limited, nightly reset | S13–S15 |
| T4 | Tampering | Malicious upload (polyglot, SVG/HTML, zip bomb, huge dimensions) | TB1/2 | signed URL with content-type + size; magic-byte check; Pillow decode with `MAX_IMAGE_PIXELS`; re-encode JPEG; reject non-JPEG/PNG/WebP | WB-U1–U11, S16 |
| T5 | Tampering | KB poisoning (malicious text instructing the LLM) | TB4 | admin-only KB writes; source allow-list; chunks treated as data; validator | RT1–RT8 |
| T6 | Tampering | Model file swapped | TB3 | ONNX sha256 checked at load vs `model_versions` | S17, IT9 |
| T7 | Tampering | Role self-escalation via profile update | TB2 | RLS `with check` keeps role; role changes admin-only, audited | S7–S9 |
| T8 | Repudiation | Admin changes threshold, denies it | TB3 | hash-chained `audit_log`; actor id from JWT | S10–S11, CC4 |
| T9 | Info disclosure | IDOR: read another farmer's scan by id | TB1/2 | ownership check in service + RLS | S6 |
| T10 | Info disclosure | GPS in EXIF reveals farm location | TB1 | client strip + server re-encode drops EXIF | WB-U10, S16 |
| T11 | Info disclosure | PII sent to LLM / logs | TB4 | prompt builder takes typed fields only; log scrubber | S18 |
| T12 | Info disclosure | Secret key in frontend bundle | TB2 | CI grep gate; key only in Render environment (secret) | S27 |
| T13 | Info disclosure | Prompt injection exfiltrates other data | TB4 | agent tools scoped to caller; no cross-user tool | red-team |
| T14 | DoS | Request flood / scan spam exhausts free hours, LLM budget | TB1 | per-user + per-IP rate limits; LLM daily budget cap; cache | CC1–CC3, S15 |
| T15 | DoS | Large images exhaust memory | TB1 | 5 MB cap, pixel cap, thread-pool semaphore | WB-U7 |
| T16 | DoS | Cold start during judging | — | keep-warm schedule; UI waking state; recorded backup demo | TO1–TO8 |
| T17 | Elevation | SQL injection | TB3 | SQLAlchemy/asyncpg parameters only; no string SQL | S26, BB* |
| T18 | Elevation | Prompt injection makes the agent send or create an alert | TB4 | agent has read-only tools only; alerts come only from the rules engine | security case S19, red-team RT8 |
| T19 | Elevation | XSS via advisory/LLM text or KB content | TB1 | React escaping; no `dangerouslySetInnerHTML`; CSP | S21, S23 |

Residual risks are tracked in `docs/plan/risk-register.md`.
