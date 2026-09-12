# Service: gateway

**Bounded context:** Edge BFF.

## Responsibilities

REST + GraphQL aggregation, authn, per-user and per-corridor rate limiting, correlation-id issuance.

## Datastore

none (stateless)

## Design note

Cost-aware throttling: a quote invokes ML inference, so quote endpoints are rate-limited more tightly than reads.

## Layout

```
gateway/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
