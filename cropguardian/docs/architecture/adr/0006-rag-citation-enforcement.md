# ADR 0006 — Advice only from retrieved sources, citations enforced

**Status:** Accepted · **Date:** 2026-10-16 · **Deciders:** Salwa, Raisa, Apon

## Context
LLMs can invent pesticide names, doses and practices. Bad dosage advice is a safety issue.

## Decision
- The advisory prompt passes only retrieved KB chunks as context and instructs: answer only
  from them; output strict JSON with `citations` (chunk ids).
- A server-side **validator** rejects the output if: no citation; a cited id was not in the
  retrieved set; dosage text not present in a cited chunk; any banned active ingredient appears.
- Rejected → fallback message + escalation to agronomist; logged as `advisories.status='blocked'`.
- UI shows the source title, publisher and page for each citation.

## Consequences
+ Every piece of advice is traceable. + Measurable: citation coverage must be 100 %.
− Coverage limited by KB quality → Salwa's KB collection is on the critical path (Gantt).
