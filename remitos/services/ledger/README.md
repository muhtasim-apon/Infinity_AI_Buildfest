# Service: ledger

**Bounded context:** What is owed.

## Responsibilities

Double-entry event-sourced journal, idempotent posting, balance projections.

## Datastore

PostgreSQL (event-sourced)

## Design note

Specified in Go for predictable latency under concurrent posting (ADR 0003). Integer poisha only - no floating point touches money (ADR 0009).

## Layout

```
ledger/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
