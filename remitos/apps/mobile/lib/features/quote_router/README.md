# Feature: quote_router

Presentation of ranked RouteOptions. Leads with landed BDT, never with fee. Renders the split proposal with icons and a voice option.

## Structure (Clean Architecture, per CLAUDE.md)

```
quote_router/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
