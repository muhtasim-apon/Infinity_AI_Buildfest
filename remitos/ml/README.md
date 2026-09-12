# ML

Pipelines, models, RAG, agents and evaluation. Nothing here has been trained or run.

| Path | Contents |
|---|---|
| `pipelines/` | ingest -> feature -> train -> eval -> register -> deploy (Airflow/Prefect DAG stubs) |
| `features/` | Feature-store definitions (Feast-style YAML) |
| `models/` | 8 models, each with a card in `docs/ai/model-cards/` |
| `rag/` | Ingestion, chunking, hybrid retrieval, reranking, GraphRAG, guardrails |
| `agents/` | 5 agents with an MCP tool registry (`docs/ai/agent-design.md`) |
| `evaluation/` | Golden sets, regression harness, fairness suite, red-team prompts |
| `notebooks/` | EDA and analysis stubs with markdown narrative |

## Non-negotiables

1. **Temporal splits, never random.** A random split on transaction data leaks the
   future into training and produces a model that evaluates beautifully and fails in
   production.
2. **A model card exists before the model is referenced anywhere.**
3. **Fairness gates block releases.** Per group, never aggregated.
4. **Device tier is a wealth proxy** and is evaluated explicitly on every risk model.
