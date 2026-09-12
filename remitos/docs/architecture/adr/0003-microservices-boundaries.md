# ADR 0003 — Service boundaries follow bounded contexts, not layers

**Status:** Accepted · **Date:** 2026-09-12

## Context

The common student-project failure is a "microservice" architecture that is really a
distributed monolith: an `api-service`, a `db-service`, a `logic-service`. Those are
layers, not contexts. They share a database, so they deploy together, fail together, and
scale together — all the cost of distribution, none of the benefit.

Our load profile is genuinely uneven. The routing engine is CPU-bound and bursty. The
ledger is write-heavy and must never lose data. The RAG service is GPU/embedding-bound.
These cannot share a scaling policy.

## Decision

One service per **bounded context**, each owning its own datastore. Services communicate
by published event (Kafka) or by explicit contract in `packages/api-contracts/`. **No
service reads another service's database.** Fourteen services, listed in
`docs/architecture/system-overview.md`.

Polyglot where justified, not for variety: `ledger` is specified in Go for
predictable-latency concurrent posting; everything else is Python/FastAPI so the team
carries one primary language plus one.

## Consequences

**Positive** — independent scaling and deployment; a failure in `rag-service` degrades
intelligence without touching settlement; clear ownership per Congress §13.2 roles.

**Negative** — distributed transactions. Addressed by the saga pattern in
`payments-orchestrator` with explicit compensating entries, never by two-phase commit.
Local development needs the full `docker-compose` stack; documented in `infra/docker/`.
Operational overhead is real and is why the observability stack is in scope from day one,
not bolted on.

**Rejected** — a modular monolith (simpler, but cannot scale the routing engine
independently and blurs ownership); serverless-per-endpoint (cold starts break the
400 ms quote target).
