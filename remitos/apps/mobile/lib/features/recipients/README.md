# Feature: recipients

Saved recipients with CRDT merge (add-wins, tombstoned deletes). Ordered by the recipient recommender; never auto-selected.

## Structure (Clean Architecture, per CLAUDE.md)

```
recipients/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
