# Architecture

| Document | Purpose |
|---|---|
| `system-overview.md` | C4 Level 1-3, the layer map, service catalogue |
| `data-flow.md` | End-to-end money and data movement, sequence diagrams |
| `adr/` | Architecture Decision Records, numbered and immutable once accepted |

## The one-paragraph version

RemitOS is a **decision layer**, not a rail. A send request enters through the Flutter
client, is authenticated and risk-scored, and is then handed to the **routing engine**,
which solves a constrained optimisation over every available payout path. Compliance
runs in parallel as a RAG-grounded agent that cites the regulation behind each verdict.
The winning route is executed by a **saga orchestrator** against partner rails, written
to a double-entry **ledger**, and reconciled by an n8n workflow. Every step emits an
immutable audit event.

## Layer map (aligned to Congress Participants Guide section 7)

| Congress layer | RemitOS implementation |
|---|---|
| User Interaction | Flutter for Android, iOS and Web; USSD/IVR bridge |
| Application Logic | gateway, payments-orchestrator saga state machine |
| AI Intelligence | agent-orchestrator plus 8 specialist ML models |
| Knowledge Retrieval | rag-service: hybrid dense + BM25 + reranker, GraphRAG |
| Agent Orchestration | ml/agents with an MCP tool registry and human-in-the-loop gates |
| Data Infrastructure | Postgres, Kafka, Qdrant, Neo4j, object store, dbt warehouse |
| Automation and Integration | automation/n8n - 12 workflows |
| Deployment | infra - Docker, Kubernetes with overlays, Terraform |
