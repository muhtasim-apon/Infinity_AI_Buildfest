# 01 — Outbreak alert fan-out

**Trigger:** Webhook `POST /webhook/cg-alert-approved` (called by API after `POST /v1/alerts/{id}/approve`).
**Payload (no PII):** `{alert_id, disease_code, disease_name_bn, center_lat, center_lon, radius_km, risk, message_bn}`.

| Node | Action |
|---|---|
| Webhook | verify HMAC (Function node, shared secret) → 401 on failure |
| HTTP Request | `GET /v1/internal/alerts/{alert_id}/recipients` (HMAC) → list of `{channel, address_token}` — API resolves subscribers within radius |
| Split In Batches (50) | rate-friendly batches |
| Switch on channel | `sms` → SMS provider HTTP API · `telegram` → Telegram Bot API · `email` → provider HTTP API (not SMTP — Render A10) |
| Error branch | retry ×3 with backoff → dead-letter sheet + team Telegram |
| HTTP Request | `POST /v1/hooks/n8n/alert_sent` with counts → API sets status `sent`, audit row |

Test: "Execute workflow" with fixture payload `tests/n8n/fixtures/alert_approved.json` against staging.
