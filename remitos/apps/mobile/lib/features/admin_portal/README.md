# Feature: admin_portal

Operations console: partner health, limit configuration with effective dates, feature flags. All changes dual-controlled and audited.

## Structure (Clean Architecture, per CLAUDE.md)

```
admin_portal/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
