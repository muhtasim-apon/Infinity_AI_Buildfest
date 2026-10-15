# Entity-relationship model & table dictionary

Diagram source: [`../diagrams/erd.mmd`](../diagrams/erd.mmd) · DDL: [`../../db/schema.sql`](../../db/schema.sql) ·
RLS: [`../../db/rls_policies.sql`](../../db/rls_policies.sql).

## Design principles
1. **3NF for operational data**, JSONB only for genuinely variable payloads (top-3, advice steps,
   eval summaries).
2. **Ownership column on every user-data table** → RLS policies are one line each.
3. **Location is coarse by construction** (`numeric(6,2)` ≈ 1 km) — exact GPS is never stored.
4. **Immutable history**: diagnoses and audit rows are never updated; corrections are new
   `expert_reviews` rows.
5. **Every model output references the model version** that produced it.

## Tables

| Table | Purpose | Key columns | Owner module | RLS summary |
|---|---|---|---|---|
| `profiles` | 1:1 with `auth.users`, role & locale | `id`, `role`, `locale`, `district`, `upazila` | auth | self read/update; admin all |
| `consents` | purpose-specific consent records | `user_id`, `purpose`, `granted` | auth | self |
| `crops` | reference: crops | `code`, `name_bn`, `name_en` | admin | public read |
| `disease_catalog` | reference: classes the model can output | `crop_id`, `code`, `pathogen_type` | admin | public read |
| `farms` | a farmer's farm | `owner_id` | scans | owner |
| `fields` | plot with crop, variety, sowing date, coarse location | `farm_id`, `crop_id` | scans | via farm owner |
| `scans` | one photo submission | `user_id`, `sha256`, `status` | scans | owner; agronomist read in region |
| `model_versions` | registry: arch, hash, τ, T, eval summary | `is_active` | inference | public read (transparency); admin write |
| `diagnoses` | model output for a scan | `scan_id` (unique), `top1_prob`, `abstained` | inference | via scan |
| `advisories` | generated advice | `diagnosis_id`, `content`, `status` | advisory | via scan |
| `citations` | advisory → KB chunk | `advisory_id`, `chunk_id`, `score` | advisory | via scan |
| `kb_documents` | source documents with licence note | `publisher`, `source_url`, `edition_date` | rag | public read |
| `kb_chunks` | chunk text + embedding | `embedding vector(384)`, `meta` | rag | public read |
| `expert_reviews` | agronomist verdicts | `scan_id`, `reviewer_id`, `verdict` | review | reviewer + admin |
| `feedback_labels` | training-ready labels | `disease_id`, `consent_training`, `exported` | review | admin |
| `alerts` | outbreak alerts | `disease_id`, centre, radius, `risk_level`, `status` | alerts | approved: public read; drafts: agronomist |
| `alert_subscriptions` | who gets alerts where/how | `user_id`, `channel`, `radius_km` | alerts | self |
| `audit_log` | append-only, hash-chained | `prev_hash`, `row_hash` | audit | admin read; insert via function only |

## Cardinalities (summary)
profile 1—N farms 1—N fields 1—N scans 1—0..1 diagnosis 1—0..1 advisory 1—N citations N—1 kb_chunk N—1 kb_document.
scan 1—N expert_reviews 1—0..1 feedback_label. disease 1—N alerts.

## Indexes (performance)
- `scans (user_id, created_at desc)` — history page.
- `scans (status) where status = 'needs_review'` — partial index for the review queue.
- `diagnoses (top1_disease_id, created_at)` + `scans (lat_coarse, lon_coarse)` — outbreak window query.
- `kb_chunks using hnsw (embedding vector_cosine_ops)` — vector search.
- `kb_chunks using gin (to_tsvector('simple', content))` — keyword half of hybrid search.
- unique `(user_id, sha256)` on scans — idempotent uploads.

## Retention
| Data | Retention |
|---|---|
| Original images | 90 days, then thumbnail only — unless labelled with training consent |
| Scans/diagnoses | while account active; deleted with account |
| Audit log | 1 year minimum |
| Demo accounts | reset nightly by n8n |
