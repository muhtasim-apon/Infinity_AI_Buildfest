# Feature: ai_assistant

Grounded Bangla Q&A over the user's own case data and the RAG corpus. Never speculates about a compliance decision - reports the recorded reason or escalates.

## Structure (Clean Architecture, per CLAUDE.md)

```
ai_assistant/
├── data/          DTOs, datasources, repository implementations
├── domain/        entities, repository interfaces, use cases (imports nothing else)
└── presentation/  pages, widgets, BLoC
```

All files are stubs. Nothing here has been compiled or run.
