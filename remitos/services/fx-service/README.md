# Service: fx-service

**Bounded context:** What rate.

## Responsibilities

Rate feed ingestion, quote generation, spread management, hedge window.

## Datastore

PostgreSQL + Redis

## Design note

Produces the BINDING quote. The corridor cost model only predicts and ranks; it never commits a price.

## Layout

```
fx-service/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
