# Service: routing-engine

**Bounded context:** Which path. **This is the commercial core.**

## Responsibilities

Candidate generation, ML cost and ETA prediction, regulatory constraint filtering,
optimisation, and Bangla rationale generation.

## Datastore

Redis (candidate and prediction cache) + model server.

## Design note

Regulatory ceilings are inputs to the optimiser, not validations after the fact
(ADR 0007). The engine returns a compliant path, a legal split, or honest
infeasibility - always **before** the sender pays.

See `app/optimiser.py` for the full contract.

Budget: p95 under 400 ms including inference (FR-01).

Stub. Never built or run.
