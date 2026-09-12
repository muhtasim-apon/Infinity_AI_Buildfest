# Workflow 04 — corridor_cost_scraper

**Trigger:** Cron, weekly
**Human gate:** No

## Purpose

Collect published competitor and benchmark pricing; write cited rows into docs/research/data/

## Design note

Public published rates only. Respects robots.txt and rate limits. Feeds the corridor cost model and keeps the fee position honest.

## Standing conventions

- **Idempotent.** Safe to re-run; schedules fire more often than expected.
- **Fails loud.** Dead-man's switch: absence of a success heartbeat pages on-call.
  A stopped workflow produces no error, so its silence must be the alarm.
- **No secrets in the repo.** Credentials are sealed-secrets only.
- **No PII leaves the boundary.** Subject to the same egress filter as application
  code (ADR 0011).

## Artefact

Exported JSON lives alongside this spec as `04_corridor_cost_scraper.json`. The JSON is the machine
representation; **this spec is what gets reviewed**, because workflow JSON diffs poorly.

Never imported or executed.
