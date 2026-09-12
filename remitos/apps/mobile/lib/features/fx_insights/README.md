# Feature: fx_insights

Send-timing guidance with explicit uncertainty. Suppressed entirely when the transfer is flagged urgent.

## Structure (Clean Architecture, per CLAUDE.md)

```
fx_insights/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
