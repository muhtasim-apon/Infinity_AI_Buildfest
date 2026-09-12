# ADR 0011 — PII never leaves the in-country boundary

**Status:** Accepted · **Date:** 2026-09-12

## Context

Data sovereignty is not a footnote in this competition — it is named in the judging
criteria (§11.1, "Responsible AI, Data Sovereignty & Presentation") and §15 requires
"respect for governance, compliance, and ownership".

Substantively, RemitOS handles National ID numbers, passport images, biometric templates
and complete financial histories for people who have no practical recourse if that data
is mishandled. Meanwhile the AI architecture depends on LLM APIs that are, by definition,
outside the country.

Those two facts are in direct tension, and most projects resolve it by not thinking about
it.

## Decision

A hard boundary with an enforcement mechanism, not a policy statement.

**1. Classification** (full table in `docs/architecture/data-flow.md`): C1 Identity ·
C2 Financial · C3 Behavioural · C4 Derived · C5 Public.

**2. The rule.** C1–C4 are processed and stored **only** within
`DATA_RESIDENCY_REGION`. They are never placed in a prompt sent to an external model.

**3. Tokenisation at the boundary.** Where an LLM must reason about a record, a
tokenisation proxy replaces every identifier with an opaque token before the call, and
re-hydrates on return:

```
"Rahima Begum, NID 1990123456789, received BDT 45,000 from Riyadh"
   ↓ tokenise at the boundary
"<PERSON_A>, <ID_1>, received <AMOUNT_1> from <CORRIDOR_SA>"
   ↓ external model reasons over structure, never identity
   ↓ re-hydrate inside the boundary
```

The model reasons about *structure and typology*, which is what it is actually good at.
It never sees identity, which it does not need.

**4. Enforcement, not trust.** An egress filter sits in front of every external call and
pattern-matches NID formats, phone numbers, account numbers and known name lists. A match
fails the request and raises a security event. CI runs the same check against prompt
templates, so a developer cannot merge a template that would leak.

**5. Model hosting path.** Where a workload can run on a self-hosted open-weights model
inside the boundary (embeddings, reranking, Bangla ASR), it does — those three are
already specified as in-boundary in `.env.example`. External frontier models are reserved
for reasoning over tokenised structure.

## Consequences

**Positive** — a defensible sovereignty position that survives a supervisor's question;
the architecture works even if cross-border data-transfer rules tighten, which is the
direction of travel globally; genuine differentiation, since most competitors cannot
describe their boundary at all.

**Negative** — the tokenisation proxy is real engineering and a real latency cost;
tokenised context degrades some model performance, which must be measured in
`ml/evaluation/` rather than assumed acceptable; in-boundary GPU hosting for embeddings
and ASR costs more than an API call. All accepted.

**Rejected** — sending PII to external APIs under a data-processing agreement (moves the
risk, does not remove it, and does not satisfy residency); refusing all external models
(gives up the reasoning quality that makes the product work); relying on prompt
instructions to avoid including PII (not an enforcement mechanism — it is a hope).
