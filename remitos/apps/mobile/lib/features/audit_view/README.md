# Feature: audit_view

Officer surface: evidence bundles including contradictory evidence, graph subgraph rendering, decision capture at decision time.

## Structure (Clean Architecture, per CLAUDE.md)

```
audit_view/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
