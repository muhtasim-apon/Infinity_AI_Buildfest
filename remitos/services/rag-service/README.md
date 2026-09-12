# Service: rag-service

**Bounded context:** What the rules say.

## Responsibilities

Hybrid dense + BM25 retrieval, reranking, GraphRAG traversal, citation enforcement.

## Datastore

Qdrant + Neo4j

## Design note

Returns NOT_FOUND rather than an ungrounded answer. Retrieved content is data, never instruction (prompt-injection boundary TB6).

## Layout

```
rag-service/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
