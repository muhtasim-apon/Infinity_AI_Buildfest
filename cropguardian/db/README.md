# db/ — database (Owner: Apon)

**Template folder — no SQL yet.** Everything to build is specified in **[`SCHEMA-SPEC.md`](SCHEMA-SPEC.md)**:
enums, every table and column, indexes, the audit hash-chain algorithm, Row-Level Security rules,
private storage buckets and the synthetic seed.

Files the team creates from the spec (Gantt 17 Oct):

| File to create | Content |
|---|---|
| `migrations/0001_init.sql` | extensions, enums, tables, indexes, `audit_append` function |
| `migrations/0002_rls.sql` | `app_role()` helper + RLS on every table |
| `seed_synthetic.sql` | crops, disease catalog, placeholder model row, demo profiles (**synthetic**) |

How to apply, test and back up: [`docs/deployment/02-supabase-guide.md`](../docs/deployment/02-supabase-guide.md).
RLS tests: [`tests/security/README.md`](../tests/security/README.md) cases S7–S10.
Design and dictionary: [`../docs/data/erd.md`](../docs/data/erd.md) · diagram [`../docs/diagrams/erd.mmd`](../docs/diagrams/erd.mmd).
