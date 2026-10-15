# Threat model (STRIDE)

Owner: **Apon** · Reviewed with Salwa (LLM threats). Assets: farmer PII (phone, approximate
location), photos, diagnoses, KB integrity, model file integrity, alert channel, API keys,
availability during judging.

## Data-flow diagram trust boundaries
TB1 browser↔API · TB2 browser↔Supabase (anon) · TB3 API↔Supabase (service role) · TB4 API↔LLM ·
TB5 n8n↔API · TB6 n8n↔SMS/email/Telegram. See `docs/architecture/system-overview.md`.

| # | STRIDE | Threat | Boundary | Mitigation | Test |
|---|---|---|---|---|---|
| T1 | Spoofing | Stolen/forged JWT | TB1 | verify signature, `exp`, `aud`; short TTL; refresh rotation | `tests/security/test_auth.py` |
| T2 | Spoofing | Forged n8n webhook triggers mass alert | TB5 | HMAC-SHA256 over body + timestamp, 5-min window, nonce cache | `test_webhook_hmac.py` |
| T3 | Spoofing | Demo account abused as a real account | TB1 | `demo` role: sandboxed writes, rate-limited, nightly reset | `test_demo_sandbox.py` |
| T4 | Tampering | Malicious upload (polyglot, SVG/HTML, zip bomb, huge dimensions) | TB1/2 | signed URL with content-type + size; magic-byte check; Pillow decode with `MAX_IMAGE_PIXELS`; re-encode JPEG; reject non-JPEG/PNG/WebP | `test_upload_sanitiser.py` |
| T5 | Tampering | KB poisoning (malicious text instructing the LLM) | TB4 | admin-only KB writes; source allow-list; chunks treated as data; validator | red-team suite |
| T6 | Tampering | Model file swapped | TB3 | ONNX sha256 checked at load vs `model_versions` | `test_model_integrity.py` |
| T7 | Tampering | Role self-escalation via profile update | TB2 | RLS `with check` keeps role; role changes admin-only, audited | `test_rls.py` |
| T8 | Repudiation | Admin changes threshold, denies it | TB3 | hash-chained `audit_log`; actor id from JWT | `test_audit_chain.py` |
| T9 | Info disclosure | IDOR: read another farmer's scan by id | TB1/2 | ownership check in service + RLS | `test_idor.py` |
| T10 | Info disclosure | GPS in EXIF reveals farm location | TB1 | client strip + server re-encode drops EXIF | `test_exif_stripped.py` |
| T11 | Info disclosure | PII sent to LLM / logs | TB4 | prompt builder takes typed fields only; log scrubber | `test_no_pii_egress.py` |
| T12 | Info disclosure | Service-role key in frontend bundle | TB2 | CI grep gate; key only in Render env group | CI |
| T13 | Info disclosure | Prompt injection exfiltrates other data | TB4 | agent tools scoped to caller; no cross-user tool | red-team |
| T14 | DoS | Request flood / scan spam exhausts free hours, LLM budget | TB1 | per-user + per-IP rate limits; LLM daily budget cap; cache | `tests/concurrency/` |
| T15 | DoS | Large images exhaust memory | TB1 | 5 MB cap, pixel cap, thread-pool semaphore | `test_large_image.py` |
| T16 | DoS | Cold start during judging | — | keep-warm schedule; UI waking state; recorded backup demo | `tests/timeout/` |
| T17 | Elevation | SQL injection | TB3 | SQLAlchemy/asyncpg parameters only; no string SQL | Bandit + Schemathesis |
| T18 | Elevation | Agent uses write tool to send alert | TB4 | only `create_alert_draft`; approval required | `test_agent_tools.py` |
| T19 | Elevation | XSS via advisory/LLM text or KB content | TB1 | React escaping; no `dangerouslySetInnerHTML`; CSP | Playwright + ZAP |

Residual risks are tracked in `docs/plan/risk-register.md`.
