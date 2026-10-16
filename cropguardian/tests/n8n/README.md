# n8n workflow tests

Each workflow in [`automation/n8n/`](../../automation/n8n/README.md) has a manual "Test" trigger.
Use only synthetic payloads. Example fixture for workflow 01 (paste into the n8n test trigger):
`alert_id` any UUID · `disease_code` blast · `disease_name_bn` ব্লাস্ট · `center_lat` 23.85 ·
`center_lon` 90.26 · `radius_km` 5 · `risk` medium · `label` "possible outbreak — unverified, rule-based" ·
`_synthetic` true.

| Workflow | Test | Expected |
|---|---|---|
| 01 alert published | fixture above, valid signature | team Telegram message; in-app alert visible |
| 01 | wrong signature | stops at verification node |
| 02 daily digest | manual run | counts posted; no personal data |
| 03 keep-warm | manual run | `/healthz` 200 recorded with latency |
| 04 heartbeat | manual run | API 200; Supabase heartbeat row updated |
| 05 synthetic monitor | fixture image; then a wrong URL | all assertions pass; failure alert fires on the wrong URL |
| 06 drift monitor | manual run | weekly stats posted |
| 07 retention | seeded old synthetic scans | thumbnails created; deletion-flagged synthetic user removed |
| 08 demo reset | manual run | demo history equals seed |

Workflow 05 is also the continuous smoke test of the deployed system.
