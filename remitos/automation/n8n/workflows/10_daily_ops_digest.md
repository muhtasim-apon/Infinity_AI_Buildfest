# Workflow 10 — daily_ops_digest

**Trigger:** Cron, 08:00 BST
**Human gate:** No

## Purpose

SLO attainment, volumes, queue depth, incident summary, and fairness metrics broken down per group

## Design note

Fairness appears per group, never aggregated. An aggregate hides exactly the disparity the digest exists to surface.

## Standing conventions

- **Idempotent.** Safe to re-run; schedules fire more often than expected.
- **Fails loud.** Dead-man's switch: absence of a success heartbeat pages on-call.
  A stopped workflow produces no error, so its silence must be the alarm.
- **No secrets in the repo.** Credentials are sealed-secrets only.
- **No PII leaves the boundary.** Subject to the same egress filter as application
  code (ADR 0011).

## Artefact

Exported JSON lives alongside this spec as `10_daily_ops_digest.json`. The JSON is the machine
representation; **this spec is what gets reviewed**, because workflow JSON diffs poorly.

Never imported or executed.
