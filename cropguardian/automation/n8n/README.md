# automation/n8n — workflow specifications

Owners: Apon (lead), Taeen. ADR: [0008](../../docs/architecture/adr/0008-n8n-automation-plane.md).
**Scheduled for after 31 Oct** (see [`00-zero-to-deploy.md`](../../docs/deployment/00-zero-to-deploy.md) "After 31 Oct"). Until then UptimeRobot covers keep-alive (03) and the database heartbeat (04).
Status: **specified, not built.** When built, export each workflow as JSON (without credentials —
credentials live only inside n8n).

Rules: n8n schedules, routes and notifies; **business rules stay in the API**. Every call to the API
is signed (`X-CG-Timestamp`, `X-CG-Signature`). No personal data in workflow logs.

| # | Workflow | Trigger | Purpose | Challenge it answers |
|---|---|---|---|---|
| 01 | [outbreak-alert-notice](workflows/01-outbreak-alert-fanout.md) | signed webhook from API when an alert is published | team notice + monitoring | core feature |
| 02 | [daily-digest](workflows/02-daily-digest.md) | cron 08:00 BST | team summary | operations |
| 03 | [keep-warm](workflows/03-keep-warm.md) | every 10 min in demo windows | avoid cold start | Render spin-down |
| 04 | [supabase-heartbeat](workflows/04-supabase-heartbeat.md) | daily | prevent free-project pause | Supabase pause |
| 05 | [synthetic-monitor](workflows/05-synthetic-monitor.md) | every 10 min (windows) / hourly | end-to-end smoke test | testing |
| 06 | [model-drift-monitor](workflows/06-model-drift-monitor.md) | weekly | not-sure rate / class mix drift | ML operations |
| 07 | [retention-and-deletion](workflows/07-retention-and-deletion.md) | nightly | thumbnails after 90 days, deletion requests | privacy, storage limits |
| 08 | [demo-reset](workflows/08-demo-reset.md) | nightly + manual | reset synthetic demo accounts | demo abuse |

Free fallback if n8n is unavailable: UptimeRobot / cron-job.org for 03 and a GitHub Actions cron for
04 (see [`.github/README.md`](../../.github/README.md) §3).
