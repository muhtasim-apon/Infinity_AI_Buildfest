# Feature: kyc

Identity capture and verification. OCR extraction proposes, the user confirms, a human corrects. Agent-assisted capture for users who cannot self-serve (persona P2).

## Structure (Clean Architecture, per CLAUDE.md)

```
kyc/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
