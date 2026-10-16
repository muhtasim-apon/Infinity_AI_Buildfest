# Audit readiness

The `/audit` page produces a one-click report (`GET /v1/audit/report`) covering:

| Section | Content | Source |
|---|---|---|
| Security | auth config, RLS status per table, last dependency scan, last ZAP scan, open findings | DB catalog, CI artefacts |
| Privacy | consent counts by purpose, deletion requests & completion time, retention job status | `consents`, n8n logs |
| Governance | active model version + card link, τ and T, threshold change history | `model_versions`, `audit_log` |
| Responsible AI | not-sure rate, alert dismiss rate, citation coverage, blocked advisories | `diagnoses`, `alerts`, `advisories` |
| Data sovereignty | hosting regions, data classes leaving the system (none personal) | config |
| Operational readiness | uptime (n8n monitor), cold-start count, p95 latency, error rate | monitors |
| Risk | top open risks with owner and status | `docs/plan/risk-register.md` |
| Integrity | audit chain verification result (recompute hashes) | `audit_append` chain |

Before measurements exist, every numeric cell shows "not yet measured", never a placeholder number.

## Audit-chain verification
Recompute `row_hash` for each row in id order from `prev_hash` + fields; any mismatch → report
"chain broken at id N". Run nightly by n8n and on demand from `/audit`.

## Incident register
| Date | Incident | Impact | Root cause | Fix | Owner |
|---|---|---|---|---|---|
| — | none yet | | | | |
