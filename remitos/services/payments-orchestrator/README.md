# Service: payments-orchestrator

**Bounded context:** Making it happen.

## Responsibilities

Saga state machine over partner rails with compensating transactions, retry and re-route.

## Datastore

PostgreSQL

## Design note

Distributed transactions are handled by saga plus compensation, never two-phase commit. A failed leg re-routes to next-best rather than failing the transfer.

## Layout

```
payments-orchestrator/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
