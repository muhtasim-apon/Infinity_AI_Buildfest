# Service: kyc

**Bounded context:** Proving who they are.

## Responsibilities

Document capture, OCR extraction, liveness, screening hooks, CDD tier assignment.

## Datastore

PostgreSQL + object store

## Design note

Extraction proposes; verification confirms. OCR is never authentication. Agent-assisted capture exists for users who cannot self-serve.

## Layout

```
kyc/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
