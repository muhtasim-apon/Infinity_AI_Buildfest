# Workflow 05 — aml_alert_triage

**Trigger:** Event: compliance.decided
**Human gate:** Yes - always. This workflow exists to reach a human

## Purpose

Route alerts to the officer queue by risk and available capacity; track SLA; age unactioned items into alerts

## Design note

An unactioned escalation must never expire silently. Ageing into an alert is the control that keeps the human gate real.

## Standing conventions

- **Idempotent.** Safe to re-run; schedules fire more often than expected.
- **Fails loud.** Dead-man's switch: absence of a success heartbeat pages on-call.
  A stopped workflow produces no error, so its silence must be the alarm.
- **No secrets in the repo.** Credentials are sealed-secrets only.
- **No PII leaves the boundary.** Subject to the same egress filter as application
  code (ADR 0011).

## Artefact

Exported JSON lives alongside this spec as `05_aml_alert_triage.json`. The JSON is the machine
representation; **this spec is what gets reviewed**, because workflow JSON diffs poorly.

Never imported or executed.
