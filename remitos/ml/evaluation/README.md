# Evaluation

Golden sets, regression harness, fairness suite and red-team prompts.
Targets and gates: `docs/ai/eval-plan.md`.

```
evaluation/
├── golden/         per-model golden sets, temporally split
├── fairness/       group-stratified suites (incl. device tier)
├── redteam/        injection via retrieved docs, limit-override social engineering,
│                   attempts to elicit another user data
├── rag/            regulatory Q&A with gold citations
├── agents/         scenario suite with officer-agreement rubric
└── harness.py      runner; CI gate
```

RAG regression runs on every **corpus** update, not only on code changes - a new
circular can break retrieval without a line of code changing.

Stubs only. No evaluation has been run.
