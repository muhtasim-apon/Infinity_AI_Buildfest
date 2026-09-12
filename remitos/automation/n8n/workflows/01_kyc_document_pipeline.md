# Workflow 01 — kyc_document_pipeline

**Trigger:** Webhook on document upload
**Human gate:** On low extraction confidence, or any NID number field below threshold

## Purpose

OCR extraction, quality scoring, routing to the verification queue

## Design note

Repeated extraction failure must route to agent-assisted capture, never to a dead end. Exclusion by OCR is a real harm (see the doc-intelligence model card).

## Standing conventions

- **Idempotent.** Safe to re-run; schedules fire more often than expected.
- **Fails loud.** Dead-man's switch: absence of a success heartbeat pages on-call.
  A stopped workflow produces no error, so its silence must be the alarm.
- **No secrets in the repo.** Credentials are sealed-secrets only.
- **No PII leaves the boundary.** Subject to the same egress filter as application
  code (ADR 0011).

## Artefact

Exported JSON lives alongside this spec as `01_kyc_document_pipeline.json`. The JSON is the machine
representation; **this spec is what gets reviewed**, because workflow JSON diffs poorly.

Never imported or executed.
