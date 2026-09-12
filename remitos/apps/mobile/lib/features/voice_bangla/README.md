# Feature: voice_bangla

Voice-first flows. Every captured amount is read back and confirmed before money moves. Voice is never a credential.

## Structure (Clean Architecture, per CLAUDE.md)

```
voice_bangla/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
