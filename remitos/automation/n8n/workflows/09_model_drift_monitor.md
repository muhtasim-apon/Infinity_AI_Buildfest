# Workflow 09 — model_drift_monitor

**Trigger:** Cron, daily
**Human gate:** Yes - on any step-down decision

## Purpose

PSI on top features, rolling performance against gates, group-wise fairness metrics

## Design note

On concept drift the system steps DOWN the degradation ladder rather than continuing to decide confidently on a stale model. Fairness breach triggers rollback, not a backlog ticket.

## Standing conventions

- **Idempotent.** Safe to re-run; schedules fire more often than expected.
- **Fails loud.** Dead-man's switch: absence of a success heartbeat pages on-call.
  A stopped workflow produces no error, so its silence must be the alarm.
- **No secrets in the repo.** Credentials are sealed-secrets only.
- **No PII leaves the boundary.** Subject to the same egress filter as application
  code (ADR 0011).

## Artefact

Exported JSON lives alongside this spec as `09_model_drift_monitor.json`. The JSON is the machine
representation; **this spec is what gets reviewed**, because workflow JSON diffs poorly.

Never imported or executed.
