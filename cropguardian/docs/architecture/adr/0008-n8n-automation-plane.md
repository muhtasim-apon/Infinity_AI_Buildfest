# ADR 0008 — n8n as the automation plane

**Status:** Accepted · **Date:** 2026-10-16 · **Deciders:** Apon, Taeen

## Context
We need scheduled and event-driven glue: alert fan-out, digests, keep-warm pings, Supabase
heartbeat, synthetic monitoring, dataset export. Render free has no cron/one-off jobs [R1].
The guide prefers automation tooling and workflow orchestration (S1 §14).

## Decision
n8n workflows (specs in `automation/n8n/workflows/`), talking to the API over HMAC-signed
webhooks. Business rules stay in the API; n8n only schedules, routes and notifies.

## Consequences
+ Visual, demoable workflows; quick to change. + Replaces cron we don't have.
− Another component to host (n8n cloud trial or self-host) → if n8n is down, the app still
works; only notifications/monitoring degrade.
