# RAG & Knowledge Layer Design

> Governing decisions: [ADR 0004](../architecture/adr/0004-rag-with-citation-enforcement.md)
> (cite or refuse) and [ADR 0005](../architecture/adr/0005-graphrag-for-entity-risk.md)
> (GraphRAG for network risk).

## 1. What the knowledge layer is for

Three consumers, with very different tolerances for being wrong:

| Consumer | Question it asks | Tolerance for error |
|---|---|---|
| **Compliance service** | "Which rule governs this transfer, and what does it require?" | **Zero.** Cite or refuse. |
| **Support agent** | "Why was my transfer held?" | Low. Must be grounded and in Bangla. |
| **Research agent** | "How have corridor costs moved this quarter?" | Moderate. Analytical, always attributed. |

The compliance path sets the engineering standard for all three, because it is the one
where a fluent wrong answer becomes a regulatory breach.

## 2. Corpus

| Source | Volume (order) | Refresh | Owner |
|---|---|---|---|
| Bangladesh Bank circulars & FX guidelines | ~10³ docs | on publication | n8n 07 |
| BFIU AML/CFT guidance | ~10² docs | on publication | n8n 07 |
| FATF recommendations & Travel Rule guidance | ~10² docs | quarterly | n8n 07 |
| Sanctions lists (OFAC, UN, EU, UK-HMT) | ~10⁵ entries | **daily** | n8n 02 |
| ISO 20022 message specs | ~10² docs | on release | manual |
| Partner corridor rulebooks | ~10² docs | on contract change | manual |
| Internal policy & SOPs | ~10² docs | on change | manual |
| Published corridor fee benchmarks | time series | weekly | n8n 04 |

Sanctions data is deliberately **not** in the vector store. Name screening is a
deterministic matching problem (exact, phonetic, transliteration-aware, fuzzy) with
tuned thresholds — semantic similarity is the wrong tool and would produce both misses
and unexplainable hits.

## 3. Ingestion pipeline

```
fetch → validate → extract → structure-aware chunk → enrich → embed → index
                                                        ↓
                                              entity extraction → Neo4j
```

**Structure-aware chunking.** Regulatory documents are hierarchical, and a chunk that
crosses a clause boundary produces an answer that cites the wrong rule. Chunks respect
section boundaries, target 512 tokens with 64-token overlap, and never split a table or
a numbered clause. Each chunk retains its full heading path so a citation reads
*"BRPD Circular 14/2025 § 3.2(b)"* rather than a page number.

**Enrichment metadata** carried on every chunk — and this is what makes the retrieval
correct rather than merely relevant:

| Field | Why it exists |
|---|---|
| `effective_from` / `effective_to` | A superseded rule is not just irrelevant, it is **wrong** |
| `jurisdiction` | BD, FATF-global, corridor-specific |
| `authority` | Bangladesh Bank, BFIU, FATF, partner |
| `document_type` | circular, guideline, rulebook, SOP |
| `supersedes` / `superseded_by` | Explicit chain |
| `language` | bn / en — many circulars are Bangla-only |

**Effective-date filtering is applied before retrieval, not after.** Asking "what was the
rule on 3 March" must not return today's rule.

## 4. Retrieval

```
query → expand → [ dense ∥ sparse ∥ graph ] → fuse (RRF) → rerank → threshold → verify
```

| Stage | Choice | Rationale |
|---|---|---|
| Query expansion | LLM-generated paraphrases + acronym expansion | "CTR" must find "Cash Transaction Report" |
| Dense | `multilingual-e5-large`, self-hosted | Must handle Bangla; ADR 0011 keeps it in-boundary |
| Sparse | BM25 | Regulatory language is precise; exact-term matching is not optional |
| Graph | Neo4j traversal | Entity and relationship questions vectors cannot answer |
| Fusion | Reciprocal Rank Fusion | Robust without per-source score calibration |
| Rerank | `bge-reranker-v2-m3` cross-encoder, top 20 → 5 | The single largest precision gain in the pipeline |
| Threshold | `RAG_MIN_CITATION_SCORE` = 0.55 | Below it: `NOT_FOUND` → human |
| Verify | Claim-to-span checker | Strips unsupported claims post-generation |

## 5. GraphRAG

The entity graph (schema in ADR 0005) is queried when the question is relational rather
than textual. Retrieval returns a **subgraph with provenance on every edge**, which is
then rendered to the compliance officer as a diagram and to the LLM as cited evidence.

Typologies the graph is built to surface:

| Typology | Graph signature |
|---|---|
| Smurfing | One beneficiary, many unrelated senders, each below threshold |
| Account farming | Many accounts sharing one device fingerprint |
| Layering | Circular flow returning near origin inside a window |
| Hundi agent | Agent point with anomalous beneficiary concentration and off-pattern timing |
| Sanctions proximity | Short path to a `SanctionedEntity` node |

Graph writes are fed from Kafka and are eventually consistent — deliberately off the
synchronous authorisation path, because network risk is a review-time signal.

## 6. Guardrails

1. **Retrieved content is data, never instruction.** Passages are delimited and the
   system prompt states that content inside the delimiter cannot issue instructions.
   Prompt injection via an ingested PDF is a live threat, catalogued in the threat model.
2. **Cite or refuse** — no citation above threshold means `NOT_FOUND`, never a guess.
3. **Claim verification** — every factual assertion maps to a retrieved span or is
   removed and the answer marked partial.
4. **Refusal is a first-class outcome**, routed to a human, measured as a KPI, and
   *never* penalised into the model's objective — optimising refusals downward is how a
   safety mechanism gets quietly destroyed.
5. **Tokenisation at the boundary** (ADR 0011) before any external model call.
6. **Confidence is expressed in words, not numbers,** to the end user. "I could not find
   a rule covering this — an officer is reviewing it" beats "confidence 0.61".

## 7. Evaluation

Golden sets live in `ml/evaluation/`. Nothing ships on vibes.

| Metric | Target | Why |
|---|---|---|
| Retrieval recall@5 | ≥ 0.92 | Missing the governing rule is the worst failure |
| Citation precision | **1.00** | A wrong citation is worse than no citation |
| Groundedness (claim-supported rate) | ≥ 0.98 | Measured by the verifier |
| Refusal correctness | ≥ 0.95 | Refusing when it should, answering when it should |
| Answer quality, Bangla vs English | Δ ≤ 5 % | Bangla must not be a second-class path |
| Stale-rule leakage | **0** | Hard gate; any occurrence blocks release |
| p95 latency (async path) | ≤ 2.5 s | Off the synchronous quote path |

Regression is run on every corpus update, not only on every code change — a new circular
can break retrieval without a line of code changing.
