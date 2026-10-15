-- Migration 0001 — initial schema + RLS
-- NOTE: never executed. Run with psql from the db/ directory:
--   psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f migrations/0001_init.sql
-- Migrations are additive: later changes are 0002_*.sql, never edits to this file.

begin;
\ir ../schema.sql
\ir ../rls_policies.sql
commit;
