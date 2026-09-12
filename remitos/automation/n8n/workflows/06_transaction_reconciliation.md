# Workflow 06 — transaction_reconciliation

**Trigger:** Cron, daily 01:00 BST
**Human gate:** On any unexplained break

## Purpose

Compare the ledger journal against partner settlement statements; open breaks; invoke the reconciliation agent for hypotheses

## Design note

Unexplained amounts land in the suspense account and raise an alert. They are never netted away - a reconciliation that always balances is not a reconciliation.

## Standing conventions

- **Idempotent.** Safe to re-run; schedules fire more often than expected.
- **Fails loud.** Dead-man's switch: absence of a success heartbeat pages on-call.
  A stopped workflow produces no error, so its silence must be the alarm.
- **No secrets in the repo.** Credentials are sealed-secrets only.
- **No PII leaves the boundary.** Subject to the same egress filter as application
  code (ADR 0011).

## Artefact

Exported JSON lives alongside this spec as `06_transaction_reconciliation.json`. The JSON is the machine
representation; **this spec is what gets reviewed**, because workflow JSON diffs poorly.

Never imported or executed.
