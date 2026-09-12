# Service: audit

**Bounded context:** Proving what happened.

## Responsibilities

Append-only hash-chained log, evidence snapshots, audit report generation.

## Datastore

Append-only store

## Design note

Chain digests periodically anchored externally, so tampering is detectable rather than merely discouraged. Failures are logged as fully as successes.

## Layout

```
audit/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
