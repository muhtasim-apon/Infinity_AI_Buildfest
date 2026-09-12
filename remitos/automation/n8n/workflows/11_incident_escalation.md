# Workflow 11 — incident_escalation

**Trigger:** Alert webhook
**Human gate:** Yes

## Purpose

Page on-call, open an incident record, assemble a timeline from the audit log

## Design note

Timeline assembly from the hash-chained audit log is what makes a post-incident review evidence-based rather than recollection-based.

## Standing conventions

- **Idempotent.** Safe to re-run; schedules fire more often than expected.
- **Fails loud.** Dead-man's switch: absence of a success heartbeat pages on-call.
  A stopped workflow produces no error, so its silence must be the alarm.
- **No secrets in the repo.** Credentials are sealed-secrets only.
- **No PII leaves the boundary.** Subject to the same egress filter as application
  code (ADR 0011).

## Artefact

Exported JSON lives alongside this spec as `11_incident_escalation.json`. The JSON is the machine
representation; **this spec is what gets reviewed**, because workflow JSON diffs poorly.

Never imported or executed.
