# ADR 0010 — Other AgriSphere challenges as domain packs

**Status:** Accepted · **Date:** 2026-10-16 · **Deciders:** whole team

## Context
AgriSphere AI lists Precision Farm, Crop Guardian, FarmMarket, YieldMax and Climate Smart
Farming (S1 §6.4). The judging rubric rewards scalability and business value (§11.1). The user
base, field registry, alerts and advisory agent are shared needs.

## Decision
Core = identity, farms/fields, scans/media, alerts, advisory agent, RAG, audit. A **pack**
supplies only: config (crops, thresholds), schemas (extra tables), prompts, and models.
Crop Guardian is the active pack. Precision Farm (irrigation/input timing from weather and
sensor data) is the first documented future pack.

## Consequences
+ A path from one feature to a farm-advisory platform. − Abstraction cost kept small: no
generic plugin loader now; the pack boundary is a folder convention plus review discipline.
