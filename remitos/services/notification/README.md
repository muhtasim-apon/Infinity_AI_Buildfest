# Service: notification

**Bounded context:** Telling people.

## Responsibilities

Push, SMS, Bangla IVR, USSD bridge, templated messaging.

## Datastore

PostgreSQL

## Design note

Carries the feature-phone path (ADR 0008). No amounts or names in lock-screen previews. IVR speaks Bengali numerals and lakh/crore convention.

## Layout

```
notification/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
