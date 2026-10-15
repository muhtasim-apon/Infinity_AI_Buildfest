# API contract outline (v1)

FastAPI generates the full OpenAPI at `/openapi.json` (disabled in production; exported to
`apps/web/src/lib/api-types.ts` with openapi-typescript). This file is the human-readable contract.

Conventions: JSON, `snake_case`; `Authorization: Bearer <supabase JWT>`; writes accept
`Idempotency-Key`; errors are RFC 9457 `application/problem+json`
`{type, title, status, detail, instance, code}`; pagination `?limit=1..50&cursor=`.

## Health
| | |
|---|---|
| `GET /healthz` | 200 `{status:"ok"}` — no DB, < 200 ms |
| `GET /readyz` | 200 `{db:"ok", model:{name, version, sha256}}` or 503 with failing component |

## Demo
`POST /v1/demo/session` `{role: "user"|"admin"}` → 200 `{access_token, expires_in, role}`. Rate limit 10/min/IP.

## Scans
`POST /v1/scans`
```json
{ "crop": "rice", "field_id": "uuid|null", "sha256": "64 hex", "lat_coarse": 23.85, "lon_coarse": 90.26,
  "captured_at": "2026-10-20T08:15:00+06:00", "client_quality_flag": null }
```
→ 201 `{scan_id, upload_url, upload_expires_at}` · 200 same body if `(user, sha256)` exists (idempotent).
Errors: 422 validation · 429 rate limit.

`POST /v1/scans/{id}/analyze` → 200
```json
{ "scan_id": "uuid", "status": "diagnosed|needs_review",
  "diagnosis": { "model_version": "1.0.0", "top3": [{"code":"blast","name_bn":"ব্লাস্ট","prob":0.0}],
                 "abstained": false, "confidence_band": "high|medium|low" },
  "advisory": { "status": "ok|fallback|blocked", "summary_bn": "...", "steps_bn": ["..."],
                "chemical": null, "safety_bn": "...",
                "citations": [{"title":"...","publisher":"BRRI","page":12,"url":"..."}] } }
```
Errors: 404 · 409 not uploaded · 413 too large · 415 unsupported type · 422 invalid image · 503 inference timeout (`Retry-After`).

`GET /v1/scans?limit=&cursor=` → history · `GET /v1/scans/{id}` → as analyze response.

## Review (agronomist)
`GET /v1/review/queue` → scans with `needs_review` in caller's upazila.
`POST /v1/review/{scan_id}` `{verdict: confirm|correct|unclear, corrected_code?, note?}` → 201.

## Alerts
`GET /v1/alerts?lat=&lon=` → approved alerts near a coarse point.
`GET /v1/alerts/drafts` (agronomist) · `POST /v1/alerts/{id}/approve` `{message_bn}` · `POST /v1/alerts/{id}/dismiss`.
`PUT /v1/me/alert-subscription` `{channel, radius_km}`.

## Admin
`GET/PUT /v1/admin/settings` (τ, outbreak radius/min/window; `reason` required) ·
`GET /v1/admin/models` · `POST /v1/admin/models/{id}/activate` ·
`GET/POST /v1/admin/kb/documents` · `POST /v1/admin/kb/documents/{id}/retire` ·
`GET /v1/admin/users` · `PUT /v1/admin/users/{id}/role`.

## Audit
`GET /v1/audit/report?format=json|html` → sections per `docs/security/audit-readiness.md`.

## Hooks (n8n → API)
`POST /v1/hooks/n8n/{event}` headers `X-CG-Timestamp`, `X-CG-Signature: sha256=<hmac>`;
events: `heartbeat`, `retention`, `export_labels`, `reset_demo`, `verify_audit_chain`, `alert_sent`.

## Internal (n8n only, HMAC — never exposed to browsers)
`GET /v1/internal/alerts/{id}/recipients` → `[{channel, address_token}]` for subscribers within the radius
(address resolved server-side; n8n never stores the list) ·
`GET /v1/admin/digest` → daily counts (workflow 02) · `GET /v1/admin/drift` → weekly drift stats (workflow 06).
The two `admin/*` routes also accept HMAC instead of an admin JWT.

## Timeouts (server budget)
healthz 0.2 s · reads 2 s · analyze 25 s (inference 4 s + LLM 20 s) · audit report 10 s.
