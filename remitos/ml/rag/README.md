# RAG

Implementation of `docs/ai/rag-design.md`.

```
rag/
├── ingest.py       fetch, validate, provenance
├── chunk.py        structure-aware; never splits a clause or table
├── embed.py        multilingual e5, in-boundary (ADR 0011)
├── retrieve.py     dense + BM25 + graph, fused by RRF
├── rerank.py       cross-encoder, top 20 -> 5
├── graphrag.py     subgraph retrieval with provenance per edge
├── guardrails.py   citation threshold, claim verifier, injection detection
└── evals.py        recall@5, citation precision, groundedness, stale-rule leakage
```

**Citation precision target is 1.00.** A wrong citation is worse than no citation.
**Stale-rule leakage target is 0** and is a hard release gate.

Stubs only.
