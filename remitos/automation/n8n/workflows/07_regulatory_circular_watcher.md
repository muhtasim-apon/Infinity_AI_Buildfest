# Workflow 07 — Regulatory Circular Watcher

**Owner:** Backend / Data Engineer · **Trigger:** Cron, every 6 hours
**Human gate:** Yes — on any detected limit or threshold change

---

## Why this workflow matters more than it looks

[ADR 0007](../../../docs/architecture/adr/0007-regulatory-limits-as-constraints.md)
makes Bangladesh Bank's ceilings inputs to the routing optimiser. That design is only
safe if the ceilings are **current**. A stale limit produces confidently wrong routing:
the engine promises a payout the recipient cannot legally take.

This workflow is the mechanism that keeps ADR 0007 honest. It is also the mechanism that
keeps the RAG corpus from citing superseded rules, which
[ADR 0004](../../../docs/architecture/adr/0004-rag-with-citation-enforcement.md) treats
as a hard release gate (`stale-rule leakage = 0`).

## Flow

```
Cron (6h)
   │
   ├─▶ Fetch Bangladesh Bank circular index (BRPD, PSD, FE circulars)
   ├─▶ Fetch BFIU guidance index
   │
   ├─▶ Diff against `ingested_documents` registry (by document id + content hash)
   │       └─ no change ──▶ emit heartbeat ──▶ end
   │
   ├─▶ For each new or amended document:
   │       ├─ Download, verify checksum, record provenance
   │       ├─ Detect language (bn / en — many circulars are Bangla-only)
   │       ├─ Structure-aware chunk (never split a clause or a table)
   │       ├─ Extract metadata: effective_from, supersedes, authority, type
   │       ├─ Embed (in-boundary model) ──▶ Qdrant
   │       ├─ Extract entities ──▶ Neo4j
   │       └─ Mark any superseded document: retain, down-rank, label
   │
   ├─▶ **Limit-change detection** (the critical branch)
   │       ├─ LLM extraction over the document, constrained to a strict schema
   │       ├─ Compare extracted values to current config
   │       └─ Any delta ──▶ HUMAN GATE ──▶ config update with effective_from
   │
   ├─▶ Re-run the RAG regression suite against the updated corpus
   │       └─ any regression ──▶ page on-call, DO NOT promote the index
   │
   └─▶ Emit `corpus.updated`; append to daily ops digest
```

## The human gate, and why it is not optional

An LLM extracting "Tk 30,000" from a circular is doing OCR-adjacent work on a legal
document, in two languages, where a misplaced digit changes a regulatory ceiling by an
order of magnitude.

Automatically writing that value into the optimiser's constraint set would mean a
model error becomes an immediate, system-wide, money-affecting misconfiguration.

So: extraction is **automated**, application is **gated**. A named person sees the old
value, the new value, the source excerpt, and the effective date, and confirms. This is
an L3 action under [ADR 0010](../../../docs/architecture/adr/0010-human-in-the-loop-gates.md)
and is dual-controlled.

Cost of the gate: minutes, a few times a year.
Cost of skipping it: every quote wrong until someone notices.

## Failure modes

| Failure | Handling |
|---|---|
| Source unreachable | Retry ×3 with backoff. Third failure pages — a silent stop is the dangerous case |
| Checksum mismatch | Quarantine; do not ingest; security event (corpus-poisoning threat, TB6) |
| Extraction schema violation | Do not guess. Escalate the document to a human for manual entry |
| RAG regression fails | **Do not promote the index.** Keep serving the previous one and page |
| Ambiguous effective date | Escalate. Never assume "immediately" — an incorrectly early effective date retroactively invalidates decisions already made |

## Dead-man's switch

Absence of a heartbeat for 12 hours pages on-call. A workflow that has stopped running
generates no error, which is precisely why its silence must itself be an alarm.

## Idempotency

Keyed on `(document_id, content_hash)`. Re-running is safe and is expected — after an
outage, after a manual retry, and after a clock change.
