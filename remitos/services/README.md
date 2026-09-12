# Services

Fourteen microservices, one bounded context each (ADR 0003). Each owns its own
datastore; no service reads another service database.

Contracts live in `packages/api-contracts/`. Events are registered in `data/schemas/`.

See `docs/architecture/system-overview.md` for the full catalogue and the reasoning.

**Differentiators:** `routing-engine/` and `compliance/`.

All stubs. Nothing built or run.
