# Workflow 03 — fx_rate_ingestion

**Trigger:** Cron, every 15 minutes
**Human gate:** No

## Purpose

Ingest rate feeds, validate against sanity bounds, publish to fx-service, alert on staleness

## Design note

A stale rate served as binding is worse than no quote. Staleness past threshold disables binding quotes and the UI says so rather than quietly serving an old number.

## Standing conventions

- **Idempotent.** Safe to re-run; schedules fire more often than expected.
- **Fails loud.** Dead-man's switch: absence of a success heartbeat pages on-call.
  A stopped workflow produces no error, so its silence must be the alarm.
- **No secrets in the repo.** Credentials are sealed-secrets only.
- **No PII leaves the boundary.** Subject to the same egress filter as application
  code (ADR 0011).

## Artefact

Exported JSON lives alongside this spec as `03_fx_rate_ingestion.json`. The JSON is the machine
representation; **this spec is what gets reviewed**, because workflow JSON diffs poorly.

Never imported or executed.
