# 01 — Outbreak alert notice

**Trigger:** Webhook `POST /webhook/cg-alert-published`, called by the API right after the rules engine
publishes an alert. **Payload (no personal data):** `{alert_id, disease_code, disease_name_bn,
center_lat, center_lon (coarse), radius_km, risk, report_count, label}`.

Farmers see alerts **in the app** (source of truth). This workflow only informs the team and keeps a
record, so a wrong alert can be dismissed quickly.

| Node | Action |
|---|---|
| Webhook | verify signature (Function node, shared secret) → stop on failure |
| Telegram | post to the team channel: disease, area, risk, report count, link to `/admin` |
| Data table / Sheet | append a row (alert id, time, risk) for the weekly dismiss-rate figure |
| Error branch | retry ×3 with backoff → team Telegram "alert notice failed" |

Test: run with the synthetic fixture described in [`tests/n8n/README.md`](../../../tests/n8n/README.md).
