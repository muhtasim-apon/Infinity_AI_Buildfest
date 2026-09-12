# ADR 0006 — n8n as the automation plane, not the application plane

**Status:** Accepted · **Date:** 2026-09-12

## Context

n8n is a visual workflow engine. It is excellent at scheduled and event-triggered
integration work — polling a source, transforming a payload, calling three systems,
escalating to a human. It is a poor place to put business logic that must be versioned,
unit-tested, code-reviewed and reasoned about under load.

The failure mode is well known: a team discovers n8n, moves core logic into it because
it is fast to build, and ends up with untestable business rules living in a JSON blob
that nobody can diff.

## Decision

Draw a hard line.

| n8n **owns** | The application **owns** |
|---|---|
| Scheduled ingestion (sanctions lists, FX rates, circulars) | Routing decisions |
| Cross-system glue and notification fan-out | Compliance verdicts |
| Human-in-the-loop escalation routing | Ledger postings |
| Operational digests and alerting | Fraud scoring |
| Data-quality and drift monitoring triggers | Anything that moves money |
| Onboarding and lifecycle nurture sequences | Anything on the synchronous request path |

n8n calls the application's APIs; the application never calls n8n synchronously in a
user-facing path. Workflows are exported to `automation/n8n/workflows/*.json`, committed,
and each carries a `.md` spec stating trigger, nodes, failure mode and human gate.

The twelve workflows are catalogued in `automation/n8n/README.md`.

## Consequences

**Positive** — integration work that would be hundreds of lines of brittle glue becomes
a reviewable workflow; non-engineers on the team can read the operational surface;
the Congress's "automation tooling and workflow orchestration" expectation (§14) is met
with a real, inspectable artefact rather than a claim.

**Negative** — a second runtime to deploy and monitor. Workflow JSON diffs poorly in
review, so the paired `.md` spec is mandatory and is what actually gets reviewed. n8n
credentials are a high-value secret target — they live in sealed-secrets, never in the
repo, and `automation/n8n/credentials/` holds only `.example` files.

**Rejected** — Airflow (heavier, and this is integration work, not data-pipeline DAGs —
though Airflow/Prefect *is* used for ML pipelines in `ml/pipelines/`, which is the
correct tool for that job); Temporal for everything (right for the payment saga, which
is why the orchestrator uses that pattern, but overkill for a daily list sync); writing
the glue in application code (works, and is ~2,000 lines of code the team does not have
the hours for).
