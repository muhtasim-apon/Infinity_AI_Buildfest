# ADR 0009 — Double-entry, event-sourced ledger

**Status:** Accepted · **Date:** 2026-09-12

## Context

A common prototype shortcut is a `balance` column updated in place. It is fast to build
and it is unauditable: it cannot answer "what was this balance on 3 March and why", it
loses history on every update, and it silently absorbs bugs as money.

RemitOS orchestrates across partner rails that fail partially and asynchronously. Without
a ledger that records *why* every movement happened, partial failures become
irreconcilable.

## Decision

A **double-entry, event-sourced** ledger. Balances are never stored as mutable state;
they are derived from an append-only journal.

- Every movement posts balanced debit and credit entries. The sum of all entries in an
  account set is invariantly zero, and this is asserted continuously, not just tested.
- Entries are **immutable**. A correction is a new compensating entry that references
  the original — never an update, never a delete.
- Every posting carries an **idempotency key** derived from the transfer plus leg, so a
  retried request cannot double-post.
- Money uses integer minor units (poisha) with an explicit currency. No floating point
  touches a monetary value anywhere in the system.
- Account taxonomy: `user_payable`, `partner_settlement`, `fee_income`, `fx_spread`,
  `suspense`, `regulatory_hold`. Anything unexplained lands in `suspense` and raises an
  alert — it is never netted away.
- Balances are read from projections rebuilt from the journal, so a projection bug is
  recoverable by replay rather than by a data-fix script.

## Consequences

**Positive** — full auditability by construction; point-in-time reconstruction for any
date; reconciliation against partner statements becomes a comparison rather than an
investigation; the `/audit` report is generated from the journal rather than assembled by
hand. Congress §11.1 scores "Responsible AI, Data Sovereignty & Presentation" — an
immutable journal is the substrate that makes any such claim checkable.

**Negative** — more storage and more write volume; balance reads need maintained
projections; the model is unfamiliar to most student teams and carries a real learning
cost. That cost is paid once and is the single highest-leverage piece of engineering
discipline in the repository.

Go was chosen for this service (ADR 0003) specifically for predictable latency under
concurrent posting.

**Rejected** — mutable balance column (unauditable); single-entry log (cannot prove
conservation of money); relying on the partner rail's records (they are not consistent
with each other, which is the whole reason reconciliation exists).
