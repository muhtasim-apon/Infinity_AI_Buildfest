# Service: agent-orchestrator

**Bounded context:** Multi-step reasoning.

## Responsibilities

Agent runtime, MCP tool registry, authority enforcement, HITL escalation.

## Datastore

PostgreSQL

## Design note

Authority is enforced at the TOOL BOUNDARY, not by prompt. L3 tools are absent from the registry entirely - an agent cannot see them (ADR 0010).

## Layout

```
agent-orchestrator/
├── app/       routers, service logic, adapters
├── tests/     unit and contract tests
├── Dockerfile
└── pyproject.toml
```

No service reads another service's database (ADR 0003). Contracts live in
`packages/api-contracts/`.

Stub. Never built or run.
