# ADR 0003 — Supabase instead of Render Postgres

**Status:** Accepted · **Date:** 2026-10-16 · **Deciders:** Apon

## Context
Render free Postgres expires **30 days after creation**, then a 14-day grace before deletion,
with no backups [R1]. A database created on 16 Oct would expire around 15 Nov — the very date
preliminary selection is announced — and would be gone before Congress Day (26 Dec). We also
need vector search, object storage and auth.

## Decision
Use one Supabase free project for Postgres (with `pgvector`), Storage (private buckets
`scans`, `models`) and Auth (email OTP now; phone OTP needs a paid SMS provider such as Twilio; JWT). The API connects with the service-role
key through the pooled connection string; the browser uses only the anon key under RLS.

## Alternatives rejected
- **Render Postgres free** — expiry above. Paid Render Postgres — budget.
- **Neon + S3 + Auth0** — three vendors, three free-tier limit sets, more secrets.
- **SQLite on Render disk** — disk is ephemeral [R1]; data would vanish on restart.

## Consequences
+ Stateful parts survive Render restarts and redeploys. + RLS gives defence in depth.
− Free projects pause after a week of inactivity [R2] → daily n8n heartbeat query.
− 500 MB DB limit [R2] → images in Storage, never in the DB; thumbnails after 90 days.
− Data hosted in the chosen Supabase region (nearest available, e.g. Singapore/Mumbai) —
  documented in `docs/data/data-sovereignty.md`.
