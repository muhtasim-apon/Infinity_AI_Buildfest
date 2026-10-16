# Entity-relationship model & table dictionary

Diagram: [`../diagrams/erd.mmd`](../diagrams/erd.mmd) · column-level spec, RLS and storage:
[`../../db/SCHEMA-SPEC.md`](../../db/SCHEMA-SPEC.md).

## Design principles
1. **3NF for operational data**; JSONB only for variable payloads (top-3, advice steps, eval summaries).
2. **Ownership column on every user-data table** → RLS policies are one line each.
3. **Location is coarse by construction** (2 decimals ≈ 1 km) — exact GPS is never stored.
4. **Immutable history**: diagnoses and audit rows are never updated.
5. **Every model output references the model version** that produced it.

## Tables
| Table | Purpose | Owner module | RLS summary |
|---|---|---|---|
| `profiles` | 1:1 with `auth.users`; role (farmer/admin/demo), locale, district, upazila | auth | self read/update (no role change); admin all |
| `consents` | purpose-specific consent (service, in-app alerts) | auth | self |
| `crops`, `disease_catalog` | reference data; classes the model can output | admin | public read |
| `farms`, `fields` | farmer's farm and plots (crop, variety, sowing date, coarse location) | scans | owner |
| `scans` | one photo submission; status incl. `not_sure` | scans | owner; admin read |
| `model_versions` | registry: architecture, hash, τ, T, evaluation summary | inference | public read; admin write via API |
| `diagnoses` | model output for a scan (top-3, abstained + reason) | inference | via scan |
| `advisories`, `citations` | generated advice and the KB chunks it cites | advisory | via scan |
| `kb_documents`, `kb_chunks` | knowledge base with licence note; text + embedding | rag | public read (non-retired) |
| `alerts` | automatic rule-based outbreak alerts (published/dismissed) | alerts | published: public read; admin all |
| `alert_preferences` | in-app alerts on/off and radius | alerts | self |
| `app_settings` | admin-tunable thresholds | admin | admin read; API write |
| `audit_log` | append-only, hash-chained log of admin and system actions | audit | admin read; insert via function only |

## Cardinalities
profile 1—N farms 1—N fields 1—N scans 1—0..1 diagnosis 1—0..1 advisory 1—N citations N—1 kb_chunk
N—1 kb_document. disease 1—N alerts. profile 1—0..1 alert_preferences.

## Indexes (performance)
`scans (user_id, created_at desc)` — history · `scans (lat_coarse, lon_coarse, created_at)` +
`diagnoses (top1_disease_id, created_at)` — outbreak window query · HNSW on `kb_chunks.embedding` ·
GIN full-text on `kb_chunks.content` · unique `(user_id, sha256)` on scans — idempotent uploads ·
partial unique index — one active model per name.

## Retention
| Data | Retention |
|---|---|
| Original images | 90 days, then thumbnail only |
| Scans / diagnoses | while the account is active; deleted with the account |
| Audit log | 1 year minimum |
| Demo accounts | reset nightly |
