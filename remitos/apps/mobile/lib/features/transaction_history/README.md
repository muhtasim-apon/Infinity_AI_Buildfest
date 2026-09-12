# Feature: transaction_history

Transfer list and detail. Shows realised-vs-predicted cost and ETA (FR-14) - the product is held publicly accountable for its own estimates.

## Structure (Clean Architecture, per CLAUDE.md)

```
transaction_history/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
