# db/ — database (Owner: Apon)

| File | Purpose |
|---|---|
| `schema.sql` | Tables, enums, indexes, `audit_append()` hash-chain function |
| `rls_policies.sql` | Row-Level Security on every table |
| `migrations/0001_init.sql` | Applies schema + RLS in one transaction |
| `seed_synthetic.sql` | Reference data + **synthetic** demo rows |

Design and dictionary: [`../docs/data/erd.md`](../docs/data/erd.md). Diagram: [`../docs/diagrams/erd.mmd`](../docs/diagrams/erd.mmd).

## Runbook (when building)
1. Create the Supabase project (region per `docs/data/data-sovereignty.md`); enable `vector`.
2. `psql "$DATABASE_URL" -f migrations/0001_init.sql`
3. Create demo auth users via Supabase Admin API; put their UUIDs into `seed_synthetic.sql`; run it.
4. Create Storage buckets `scans` (private) and `models` (private).
5. Verify RLS with `tests/security/test_rls.py` (anon key must not read others' scans).

Status: **never executed.**
