# ADR 0004 — RAG answers in regulated paths must cite or refuse

**Status:** Accepted · **Date:** 2026-09-12

## Context

The compliance service reasons over Bangladesh Bank circulars, FATF recommendations,
sanctions guidance and partner corridor rules. An LLM asked "may this transfer proceed?"
will always produce a fluent answer. In a regulated domain, a fluent wrong answer is
worse than silence: it creates a decision the institution cannot defend to a supervisor.

The Congress guide reinforces this from two directions — §14 requires *explainability of
the intelligence core*, and §15 requires transparency in AI reasoning.

## Decision

Every RAG response on a regulated path carries **structured citations** — document id,
section, effective date, retrieval score. Enforcement is mechanical, not advisory:

1. Hybrid retrieval (dense + BM25), then cross-encoder rerank.
2. If no reranked passage clears `RAG_MIN_CITATION_SCORE` (default 0.55), the service
   returns `NOT_FOUND` and the request escalates to a human officer.
3. A post-generation verifier checks every factual claim maps to a retrieved span.
   Unsupported claims are stripped, and the response is marked partial.
4. Retrieved documents are wrapped as **data**, never as instructions — prompt injection
   from an ingested PDF is an explicit threat in `docs/security/threat-model.md`.
5. Superseded circulars are retained but down-ranked and labelled; effective-date
   filtering is applied before retrieval, because last year's rule is not merely
   irrelevant, it is wrong.

## Consequences

**Positive** — every compliance decision is defensible; the `/audit` report can
reconstruct the exact regulatory basis for any historical transfer; hallucination on the
highest-risk path is structurally prevented rather than prompted against.

**Negative** — higher refusal rate, which increases human review load. This is the
correct trade: a false ALLOW is a regulatory breach, a false ESCALATE is an officer's
ten minutes. Latency rises by the rerank + verify step (budgeted ~300 ms, off the
synchronous quote path). Corpus curation becomes an ongoing operational duty, owned by
n8n workflow 07.

**Rejected** — fine-tuning a model on regulations instead of retrieving (cannot cite,
cannot be updated when a circular lands on a Tuesday); plain RAG without a verifier
(citations present but not actually checked — the common and misleading half-measure).
