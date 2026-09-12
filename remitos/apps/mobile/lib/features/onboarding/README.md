# Feature: onboarding

Registration, device binding, language choice. Bangla is pre-selected (ADR 0012); the language step never defaults to English.

## Structure (Clean Architecture, per CLAUDE.md)

```
onboarding/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
