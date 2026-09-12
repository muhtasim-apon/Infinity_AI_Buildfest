# ADR 0005 — GraphRAG over an entity graph for network risk

**Status:** Accepted · **Date:** 2026-09-12

## Context

Vector retrieval answers "what does the text say about X?" It cannot answer "is this
beneficiary two hops from a flagged entity?" — and that second question is the one that
actually catches laundering.

The hundi problem is structurally a *network* problem. Reporting on the CID
investigation describes at least 5,000 MFS agents implicated in routing flows outside
formal channels. Those agents are not individually anomalous; they are anomalous as a
pattern of shared beneficiaries, shared devices and circular funding. A per-transaction
classifier is blind to this by construction.

## Decision

Maintain an entity graph in Neo4j alongside the vector store, and use **GraphRAG** —
retrieval that traverses relationships and returns subgraphs as context, not just text
chunks.

**Nodes:** Sender · Beneficiary · Device · Account · Agent · Corridor · Partner ·
SanctionedEntity · Case
**Edges:** `SENT_TO` · `USED_DEVICE` · `PAYS_OUT_AT` · `SHARES_ACCOUNT` ·
`SAME_ID_DOCUMENT` · `MATCHES_SANCTION` · `LINKED_CASE`

Queries the graph answers that vectors cannot:
- Shortest path from beneficiary to any sanctioned entity (n-hop risk)
- Beneficiaries receiving from an implausible number of unrelated senders (smurfing)
- Devices shared across nominally unrelated senders (account farming)
- Circular flows returning to origin within a window (layering)
- Agent points with anomalous beneficiary concentration (the hundi agent signature)

Graph features feed the fraud and AML models as inputs; the subgraph feeds the LLM as
cited evidence.

## Consequences

**Positive** — detects the patterns that carry the actual laundering risk; produces a
visual, human-legible explanation for an officer (a subgraph is far more persuasive in a
case file than a score); the same graph powers the "typology" narratives in the audit
report.

**Negative** — a second specialised datastore to operate, back up and secure. Graph
writes must stay off the synchronous payment path (fed from Kafka, eventually
consistent) — accepted, because network risk is a review-time signal, not a
sub-second-authorisation signal. Graph PII is class C1/C2 and inherits the residency
constraint in ADR 0011.

**Rejected** — recursive SQL over Postgres (works to ~2 hops, collapses beyond, and the
queries become unmaintainable); vector-only retrieval (cannot express relationships at
all); a commercial graph-analytics platform (cost and data-residency incompatibility).
