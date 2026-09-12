# Feature: send_money

THE CORE FEATURE. Amount entry, route comparison led by landed amount, split proposal (journey J3), confirmation. See domain/route_option.dart.

## Structure (Clean Architecture, per CLAUDE.md)

```
send_money/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
