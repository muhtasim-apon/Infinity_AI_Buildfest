# ADR 0002 — FastAPI modular monolith, not microservices

**Status:** Accepted · **Date:** 2026-10-16 · **Deciders:** Apon, Taeen

## Context
One free Render instance; 750 instance-hours/month per workspace [R1]; spin-down after 15 min.
Five people, two weeks to preliminary. The ML stack is Python.

## Decision
A single FastAPI application with internal modules (auth, scans, inference, advisory, rag,
review, alerts, admin, audit). Each module owns its tables; cross-module calls go through
service functions. One Docker image, one Uvicorn worker (`WEB_CONCURRENCY=1`).

## Alternatives rejected
- **Microservices** (separate inference/RAG services) — each would cold-start separately and
  consume hours; network hops add latency; operational load for a 5-person team.
- **Supabase Edge Functions only** — Deno runtime cannot run ONNX Runtime Python + our ML code
  comfortably; vision inference needs a real container.
- **Django** — heavier; we need async I/O to the LLM more than an admin framework.

## Consequences
+ One cold start, one deploy, one log stream. + Async endpoints overlap LLM waits.
− CPU-bound inference blocks the event loop → run it in a thread pool (`run_in_threadpool`)
  with a semaphore of 2. − A split later needs discipline now (module boundaries enforced in review).
