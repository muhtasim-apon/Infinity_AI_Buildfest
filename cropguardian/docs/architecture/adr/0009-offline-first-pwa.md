# ADR 0009 — Offline capture with an outbox

**Status:** Accepted · **Date:** 2026-10-16 · **Deciders:** Sara, Apon

## Context
Fields often have weak coverage; the API may also be cold-starting.

## Decision
Captured photos and metadata go to an IndexedDB outbox first, with a client-generated
`Idempotency-Key`. The outbox flushes when online and `/healthz` is OK (Background Sync where
supported, otherwise on app focus / manual "send now"). Previously received diagnoses and the
static disease guide are cached for offline reading.

## Consequences
+ No lost photos; cold start becomes invisible to the farmer. + Idempotency prevents duplicates
on retry. − Diagnosis itself needs the network (server-side model) — stated in the UI.
