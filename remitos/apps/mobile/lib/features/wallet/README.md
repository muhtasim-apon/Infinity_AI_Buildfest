# Feature: wallet

Balance and funding methods on the sending side.

## Structure (Clean Architecture, per CLAUDE.md)

```
wallet/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
