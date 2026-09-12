# Service: reporting

**Bounded context:** Telling the regulator.

## Responsibilities

Regulatory returns, settlement reports, STR/CTR assembly.

## Datastore

Warehouse (read)

## Design note

The compliance agent drafts an STR narrative; an officer reviews, edits and files. The agent never files.

## Layout

```
reporting/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
