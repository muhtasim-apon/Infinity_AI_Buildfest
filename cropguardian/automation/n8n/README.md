# automation/n8n — workflow specifications

Owners: Apon (lead), Taeen. ADR: [0008](../../docs/architecture/adr/0008-n8n-automation-plane.md).
Status: **specified, not built.** Export each built workflow as JSON into `workflows/json/` (no credentials —
credentials live in n8n only; `automation/n8n/credentials/` is git-ignored).

Rules: n8n schedules, routes and notifies; **business rules stay in the API**. Every call to the API is
HMAC-signed (`X-CG-Timestamp`, `X-CG-Signature`). No personal data in workflow logs.

| # | Workflow | Trigger | Purpose | Challenge it answers |
|---|---|---|---|---|
| 01 | [outbreak-alert-fanout](workflows/01-outbreak-alert-fanout.md) | webhook from API on alert approve | notify subscribers | core feature |
| 02 | [daily-digest](workflows/02-daily-digest.md) | cron 08:00 BST | team & agronomist summary | ops |
| 03 | [keep-warm](workflows/03-keep-warm.md) | cron every 10 min in demo windows | avoid cold start | Render A1 |
| 04 | [supabase-heartbeat](workflows/04-supabase-heartbeat.md) | cron daily | prevent free-project pause | Supabase B1 |
| 05 | [synthetic-monitor](workflows/05-synthetic-monitor.md) | cron every 10 min (windows) / hourly | end-to-end smoke test | testing §9 |
| 06 | [model-drift-monitor](workflows/06-model-drift-monitor.md) | cron weekly | abstain rate / class mix drift | ML ops |
| 07 | [retention-and-deletion](workflows/07-retention-and-deletion.md) | cron nightly | thumbnails after 90 d, deletion requests | privacy, B2/B4 |
| 08 | [demo-reset](workflows/08-demo-reset.md) | cron nightly + manual | reset synthetic demo accounts | threat T3 |
| 09 | [label-export](workflows/09-label-export.md) | cron weekly | consented labels → training set | data flywheel |
