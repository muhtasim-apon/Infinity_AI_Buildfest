# Workflow 08 — customer_support_triage_bangla

**Trigger:** Webhook on inbound message
**Human gate:** Yes - on send

## Purpose

Classify intent, route, and draft a grounded Bangla reply from the user's own case data

## Design note

The support agent reports the RECORDED reason for a compliance decision. It never speculates - speculation about an AML hold is both a security leak and a legal problem.

## Standing conventions

- **Idempotent.** Safe to re-run; schedules fire more often than expected.
- **Fails loud.** Dead-man's switch: absence of a success heartbeat pages on-call.
  A stopped workflow produces no error, so its silence must be the alarm.
- **No secrets in the repo.** Credentials are sealed-secrets only.
- **No PII leaves the boundary.** Subject to the same egress filter as application
  code (ADR 0011).

## Artefact

Exported JSON lives alongside this spec as `08_customer_support_triage_bangla.json`. The JSON is the machine
representation; **this spec is what gets reviewed**, because workflow JSON diffs poorly.

Never imported or executed.
