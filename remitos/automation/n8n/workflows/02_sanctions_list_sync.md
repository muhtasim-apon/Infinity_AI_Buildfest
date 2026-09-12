# Workflow 02 — sanctions_list_sync

**Trigger:** Cron, daily 02:00 BST
**Human gate:** Yes - every new hit, without exception

## Purpose

Fetch OFAC, UN, EU and UK-HMT lists, diff against the previous snapshot, and re-screen the ENTIRE existing customer book against the delta

## Design note

A name added today may match a customer onboarded two years ago. Transaction-time-only screening would never notice. Matching is deterministic: exact, phonetic, transliteration-aware, fuzzy - never semantic similarity.

## Standing conventions

- **Idempotent.** Safe to re-run; schedules fire more often than expected.
- **Fails loud.** Dead-man's switch: absence of a success heartbeat pages on-call.
  A stopped workflow produces no error, so its silence must be the alarm.
- **No secrets in the repo.** Credentials are sealed-secrets only.
- **No PII leaves the boundary.** Subject to the same egress filter as application
  code (ADR 0011).

## Artefact

Exported JSON lives alongside this spec as `02_sanctions_list_sync.json`. The JSON is the machine
representation; **this spec is what gets reviewed**, because workflow JSON diffs poorly.

Never imported or executed.
