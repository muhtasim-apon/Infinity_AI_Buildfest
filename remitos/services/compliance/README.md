# Service: compliance

**Bounded context:** Is it allowed. **Core differentiator.**

## Responsibilities

Sanctions screening, Travel Rule payload construction, AML risk scoring,
RAG-grounded rule retrieval, case management, human-gate routing.

## Datastore

PostgreSQL.

## Design note

Cite or refuse (ADR 0004). Every sanctions hit goes to a human regardless of
confidence. Name matching is deterministic and transliteration-aware - never semantic
similarity.

See `app/decision_engine.py` for the full contract.

Stub. Never built or run.
