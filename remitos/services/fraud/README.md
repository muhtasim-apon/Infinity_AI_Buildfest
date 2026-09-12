# Service: fraud

**Bounded context:** Is it genuine.

## Responsibilities

Real-time scoring, velocity checks, device and geo anomaly, graph signals.

## Datastore

Redis + Neo4j

## Design note

Synchronous path, 150 ms p95 budget. Distinct from AML: fraud is committed AGAINST the user, laundering THROUGH the system.

## Layout

```
fraud/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
