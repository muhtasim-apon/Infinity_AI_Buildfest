# Database specification — Supabase Postgres + pgvector

**Status: specification only — no SQL files yet.** Owner: **Apon**. Write the migration from this spec
on Gantt day 17 Oct and apply it with the [Supabase guide](../docs/deployment/02-supabase-guide.md).
ER diagram: [`docs/diagrams/erd.mmd`](../docs/diagrams/erd.mmd) · dictionary: [`docs/data/erd.md`](../docs/data/erd.md).

Files to create: `db/migrations/0001_init.sql` (extensions, enums, tables, indexes, functions),
`db/migrations/0002_rls.sql` (RLS), `db/seed_synthetic.sql` (reference + synthetic demo data).
Migrations are additive — never edit an applied one; add `0003_…`.

## 1. Conventions
- Extensions: `pgcrypto` (UUIDs, hashing), `vector` (embeddings).
- Primary keys `uuid default gen_random_uuid()` (reference tables use `smallint`).
- Every table has `created_at timestamptz not null default now()`.
- **RLS enabled on every table** (checklist: Row level security).
- Location only as `numeric(6,2)` (≈ 1 km). Exact GPS is never stored.
- No personal data in `audit_log.detail`.

## 2. Enumerations
| Enum | Values |
|---|---|
| `user_role` | farmer, admin, demo |
| `scan_status` | pending_upload, uploaded, diagnosed, not_sure, failed |
| `pathogen_type` | fungal, bacterial, viral, pest, healthy, other |
| `advisory_status` | ok, fallback, blocked |
| `alert_status` | published, dismissed |
| `risk_level` | low, medium, high |
| `consent_purpose` | service, in_app_alerts |

## 3. Tables
### profiles (1 : 1 with `auth.users`)
| Column | Type | Rule |
|---|---|---|
| id | uuid PK | references `auth.users(id)` on delete cascade |
| role | user_role | default `farmer`; changed only by admin API (audited) |
| display_name | text | 1–80 chars |
| locale | text | `bn` (default) or `en` |
| district, upazila | text | optional |
| deleted_at | timestamptz | soft delete before hard delete |

### consents
user_id → profiles · purpose consent_purpose · granted boolean · text_version text (wording shown) · index (user_id, purpose, created_at desc).

### crops / disease_catalog (reference, public read)
crops: id smallint, code unique, name_bn, name_en.
disease_catalog: id smallint, crop_id → crops, code unique (matches `ml/vision` labels), name_bn, name_en, pathogen, is_notifiable boolean.

### farms / fields
farms: id, owner_id → profiles, name 1–80.
fields: id, farm_id → farms, crop_id, variety, area_decimal > 0, sowing_date, lat_coarse 20–27, lon_coarse 88–93.

### model_versions (public read — transparency)
id · name · semver · architecture · onnx_sha256 char(64) · threshold 0–1 · temperature > 0 · eval_summary jsonb (empty until measured, always with split id + commit) · is_active · unique (name, semver) · **partial unique index: one active per name**.

### scans
| Column | Type | Rule |
|---|---|---|
| id | uuid PK | |
| user_id | uuid | → profiles |
| field_id | uuid | → fields, nullable |
| crop_id | smallint | → crops |
| storage_path | text | `scans/{user_id}/{id}.jpg` (private bucket) |
| sha256 | char(64) | **unique (user_id, sha256)** → idempotent uploads |
| status | scan_status | default pending_upload |
| lat_coarse, lon_coarse | numeric(6,2) | |
| client_quality_flag | text | dark / blurry / null |
| captured_at | timestamptz | |
Indexes: (user_id, created_at desc) · (lat_coarse, lon_coarse, created_at).

### diagnoses
scan_id unique → scans · model_version_id → model_versions · top1_disease_id · top1_prob 0–1 · top3 jsonb · abstained boolean · abstain_reason text · latency_ms ≥ 0 · index (top1_disease_id, created_at). Rows are never updated.

### kb_documents / kb_chunks (public read; admin write via API)
kb_documents: title, publisher (DAE/BRRI/BARI/other), source_url, **licence_note (required)**, edition_date, language, retired_at.
kb_chunks: document_id, page, content, embedding vector(384), meta jsonb {crop, disease, stage, topic}. Indexes: HNSW on embedding (cosine) · GIN full-text on content · GIN on meta.

### advisories / citations
advisories: diagnosis_id unique, language, content jsonb {summary, steps, chemical, safety}, llm_model, status advisory_status.
citations: advisory_id, chunk_id, score.

### alerts
| Column | Rule |
|---|---|
| disease_id | → disease_catalog (notifiable only) |
| center_lat, center_lon | numeric(6,2) |
| radius_km | 0–50 |
| report_count | > 0 |
| risk | risk_level |
| rule_version | e.g. `rules-v1` |
| status | published (default) / dismissed |
| dismissed_by, dismiss_reason | set only by admin dismiss (audited) |
Index (status, created_at desc). Cooldown: at most one published alert per (disease, ~area) within `OUTBREAK_COOLDOWN_HOURS`.

### alert_preferences
user_id unique → profiles · enabled boolean · radius_km 1–50.

### app_settings (admin-tunable values)
key text PK (`confidence_threshold`, `outbreak_radius_km`, `outbreak_min_reports`, `outbreak_window_days`, `outbreak_cooldown_hours`) · value jsonb · updated_by · updated_at. Every change also writes an audit row with the reason.

### audit_log (append-only, hash-chained) — checklist: Log admin actions
id bigint identity · actor_id · action (e.g. `admin.settings.update`, `admin.alert.dismiss`, `admin.model.activate`, `admin.role.change`, `scan.analyze`) · entity · entity_id · detail jsonb (scrubbed) · prev_hash · row_hash · created_at.

**Append function (algorithm to implement as `audit_append`, SECURITY DEFINER):** take a
transaction-level advisory lock (keeps the chain linear under concurrency) → read the latest
`row_hash` → `row_hash = sha256(prev_hash ‖ action ‖ entity ‖ entity_id ‖ detail ‖ created_at)` → insert.
`UPDATE` and `DELETE` on `audit_log` revoked from `public`, `anon`, `authenticated`.

## 4. Row-Level Security rules
Helper functions are **SECURITY DEFINER** so a policy never queries the same table under the caller's
RLS — two pitfalls found during design: (1) a policy on `profiles` that selects from `profiles` raises
*"infinite recursion detected in policy"*; (2) a policy that looks up *another* user's profile returns
nothing because the caller can only see their own row.

| Helper | Returns |
|---|---|
| `app_role()` | role of `auth.uid()` |

| Table | Policy |
|---|---|
| profiles | select own row or admin; update own row **with check role = app_role()** (no self-escalation) |
| consents, alert_preferences | all operations on own rows only |
| crops, disease_catalog, model_versions, kb_chunks | select for everyone |
| kb_documents | select where `retired_at is null` |
| farms | own rows (owner_id = auth.uid()) |
| fields | rows whose farm belongs to the caller |
| scans | select/insert own; admin select all |
| diagnoses, advisories, citations | visible only when the parent scan is visible |
| alerts | select where status = published; admin select all |
| app_settings | admin select; writes only through the API |
| audit_log | admin select; inserts only via `audit_append` |

The API uses the Supabase **secret key** (bypasses RLS) for server work; RLS protects any direct
browser access with the publishable key and is defence in depth.

## 5. Storage buckets (private) — checklist: Private storage buckets
| Bucket | Content | Access |
|---|---|---|
| `scans` | compressed leaf photos | upload via short-lived signed URL from the API; read only by the owner's signed URL; never public |
| `models` | ONNX files `models/<name>/<semver>/classifier.int8.onnx` | API (secret key) only |

## 6. Seed (synthetic only)
crops: rice. disease_catalog: healthy, bacterial_leaf_blight, brown_spot, narrow_brown_spot, blast,
sheath_blight, tungro (notifiable: BLB, blast, tungro; Bangla names pending expert check).
model_versions: one placeholder row `0.0.0-placeholder`, eval_summary `{"status":"not trained"}`.
Demo profiles: "ডেমো কৃষক (Synthetic)" role demo, "Demo Admin (Synthetic)" role admin — created through
Supabase Auth first, their UUIDs used in the seed.
