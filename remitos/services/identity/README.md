# Service: identity

**Bounded context:** Who the user is.

## Responsibilities

OIDC, RBAC, device binding, step-up authentication, session lifecycle.

## Datastore

PostgreSQL

## Design note

Device binding is the primary factor. SMS OTP alone is NOT sufficient for high-value transfers - SIM swap is a live attack in this market.

## Layout

```
identity/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
