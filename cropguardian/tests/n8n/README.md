# n8n workflow tests

Each workflow in `automation/n8n/workflows/` has a manual "Test" trigger fed with a fixture from
`fixtures/`. Expected outcomes:

| Workflow | Fixture | Expected |
|---|---|---|
| 01 alert fan-out | `alert_approved.json` | recipients fetched; one message per channel per recipient to the **sandbox** channel; API receives `alert_sent` |
| 01 (bad signature) | `alert_approved.json` with wrong HMAC | workflow stops at verification node |
| 03 keep-warm | — | `/healthz` 200 recorded with latency |
| 04 heartbeat | — | API 200; heartbeat row timestamp updated |
| 05 synthetic monitor | fixture image | all assertions pass; on forced failure (wrong URL) team alert fires |
| 07 retention | seeded old synthetic scans | thumbnails created; deletion-flagged synthetic user removed |
| 08 demo reset | — | demo history equals seed |

The synthetic monitor (05) is also our continuous **production smoke test**.
