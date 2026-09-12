# Feature: agent_mode

Agent tooling: float forecasting, advance notice of large inbound payouts, transparent commission. Agent identity is logged on every assisted action.

## Structure (Clean Architecture, per CLAUDE.md)

```
agent_mode/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
