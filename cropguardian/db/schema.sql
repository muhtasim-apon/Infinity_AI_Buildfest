-- Crop Guardian — PostgreSQL schema v1 (Supabase: Postgres 15+, pgvector)
--
-- NOTE: never executed. Reviewed design; apply via migrations/0001_init.sql.
-- Conventions: snake_case, uuid PKs (gen_random_uuid), created_at on every table,
-- coarse location only (numeric(6,2) ≈ 1 km), RLS enabled on every table (rls_policies.sql).
-- ER diagram: docs/diagrams/erd.mmd · dictionary: docs/data/erd.md

create extension if not exists pgcrypto;
create extension if not exists vector;

-- ── Enumerations ─────────────────────────────────────────────────────────────
create type user_role       as enum ('farmer', 'agronomist', 'admin', 'demo');
create type scan_status     as enum ('pending_upload', 'uploaded', 'diagnosed', 'needs_review', 'failed');
create type pathogen_type   as enum ('fungal', 'bacterial', 'viral', 'pest', 'healthy', 'other');
create type review_verdict  as enum ('confirm', 'correct', 'unclear');
create type advisory_status as enum ('ok', 'fallback', 'blocked');
create type alert_status    as enum ('draft', 'approved', 'sent', 'dismissed');
create type risk_level      as enum ('low', 'medium', 'high');
create type consent_purpose as enum ('service', 'training_use', 'sms_alerts');
create type notify_channel  as enum ('inapp', 'sms', 'email', 'telegram');

-- ── Identity ─────────────────────────────────────────────────────────────────
create table profiles (
  id            uuid primary key references auth.users (id) on delete cascade,
  role          user_role   not null default 'farmer',
  display_name  text        not null check (char_length(display_name) between 1 and 80),
  phone_e164    text        check (phone_e164 ~ '^\+8801[3-9][0-9]{8}$'),   -- restricted column
  locale        text        not null default 'bn' check (locale in ('bn', 'en')),
  district      text,
  upazila       text,
  deleted_at    timestamptz,
  created_at    timestamptz not null default now()
);

create table consents (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references profiles (id) on delete cascade,
  purpose     consent_purpose not null,
  granted     boolean not null,
  text_version text not null,               -- which consent wording the user saw
  created_at  timestamptz not null default now()
);
create index consents_user_purpose on consents (user_id, purpose, created_at desc);

-- ── Reference data ───────────────────────────────────────────────────────────
create table crops (
  id        smallint primary key,
  code      text unique not null,
  name_bn   text not null,
  name_en   text not null,
  created_at timestamptz not null default now()
);

create table disease_catalog (
  id             smallint primary key,
  crop_id        smallint not null references crops (id),
  code           text unique not null,        -- matches ml/vision/configs/labels.yaml
  name_bn        text not null,
  name_en        text not null,
  pathogen       pathogen_type not null,
  is_notifiable  boolean not null default false,  -- triggers outbreak logic
  created_at     timestamptz not null default now()
);

-- ── Farms & fields ───────────────────────────────────────────────────────────
create table farms (
  id         uuid primary key default gen_random_uuid(),
  owner_id   uuid not null references profiles (id) on delete cascade,
  name       text not null check (char_length(name) between 1 and 80),
  created_at timestamptz not null default now()
);
create index farms_owner on farms (owner_id);

create table fields (
  id           uuid primary key default gen_random_uuid(),
  farm_id      uuid not null references farms (id) on delete cascade,
  crop_id      smallint not null references crops (id),
  variety      text,                         -- e.g. BRRI dhan28
  area_decimal numeric(8,2) check (area_decimal > 0),   -- local unit "decimal"
  sowing_date  date,
  lat_coarse   numeric(6,2) check (lat_coarse between 20 and 27),
  lon_coarse   numeric(6,2) check (lon_coarse between 88 and 93),
  created_at   timestamptz not null default now()
);
create index fields_farm on fields (farm_id);

-- ── Model registry ───────────────────────────────────────────────────────────
create table model_versions (
  id            uuid primary key default gen_random_uuid(),
  name          text not null,
  semver        text not null,
  architecture  text not null,               -- e.g. efficientnetv2_b0
  onnx_sha256   char(64) not null,
  threshold     real not null check (threshold between 0 and 1),
  temperature   real not null check (temperature > 0),
  eval_summary  jsonb not null default '{}',  -- metrics WITH split id + commit; empty until measured
  is_active     boolean not null default false,
  created_at    timestamptz not null default now(),
  unique (name, semver)
);
create unique index model_versions_one_active on model_versions (name) where is_active;

-- ── Scans & diagnoses ────────────────────────────────────────────────────────
create table scans (
  id                  uuid primary key default gen_random_uuid(),
  user_id             uuid not null references profiles (id) on delete cascade,
  field_id            uuid references fields (id) on delete set null,
  crop_id             smallint not null references crops (id),
  storage_path        text not null,          -- scans/{user_id}/{id}.jpg
  sha256              char(64) not null,
  status              scan_status not null default 'pending_upload',
  lat_coarse          numeric(6,2),
  lon_coarse          numeric(6,2),
  client_quality_flag text,                   -- 'dark' | 'blurry' | null
  captured_at         timestamptz,
  created_at          timestamptz not null default now(),
  unique (user_id, sha256)                    -- idempotent upload
);
create index scans_user_recent on scans (user_id, created_at desc);
create index scans_review_queue on scans (created_at) where status = 'needs_review';
create index scans_geo on scans (lat_coarse, lon_coarse, created_at);

create table diagnoses (
  id               uuid primary key default gen_random_uuid(),
  scan_id          uuid not null unique references scans (id) on delete cascade,
  model_version_id uuid not null references model_versions (id),
  top1_disease_id  smallint references disease_catalog (id),
  top1_prob        real not null check (top1_prob between 0 and 1),
  top3             jsonb not null,            -- [{disease_id, prob}]
  abstained        boolean not null,
  latency_ms       integer check (latency_ms >= 0),
  created_at       timestamptz not null default now()
);
create index diagnoses_disease_time on diagnoses (top1_disease_id, created_at);

-- ── Knowledge base (RAG) ─────────────────────────────────────────────────────
create table kb_documents (
  id            uuid primary key default gen_random_uuid(),
  title         text not null,
  publisher     text not null,                -- DAE | BRRI | BARI | other
  source_url    text not null,
  licence_note  text not null,                -- permission / licence basis
  edition_date  date,
  language      text not null check (language in ('bn', 'en')),
  retired_at    timestamptz,
  created_at    timestamptz not null default now()
);

create table kb_chunks (
  id           uuid primary key default gen_random_uuid(),
  document_id  uuid not null references kb_documents (id) on delete cascade,
  page         integer,
  content      text not null,
  embedding    vector(384) not null,          -- multilingual-e5-small
  meta         jsonb not null default '{}',   -- {crop, disease, stage}
  created_at   timestamptz not null default now()
);
create index kb_chunks_embedding on kb_chunks using hnsw (embedding vector_cosine_ops);
create index kb_chunks_fts on kb_chunks using gin (to_tsvector('simple', content));
create index kb_chunks_meta on kb_chunks using gin (meta);

-- ── Advisory ────────────────────────────────────────────────────────────────
create table advisories (
  id            uuid primary key default gen_random_uuid(),
  diagnosis_id  uuid not null unique references diagnoses (id) on delete cascade,
  language      text not null default 'bn',
  content       jsonb not null,               -- {summary, steps[], dosage, safety}
  llm_model     text,
  status        advisory_status not null,
  created_at    timestamptz not null default now()
);

create table citations (
  id           uuid primary key default gen_random_uuid(),
  advisory_id  uuid not null references advisories (id) on delete cascade,
  chunk_id     uuid not null references kb_chunks (id),
  score        real not null,
  created_at   timestamptz not null default now()
);
create index citations_advisory on citations (advisory_id);

-- ── Human review & labels ───────────────────────────────────────────────────
create table expert_reviews (
  id                   uuid primary key default gen_random_uuid(),
  scan_id              uuid not null references scans (id) on delete cascade,
  reviewer_id          uuid not null references profiles (id),
  verdict              review_verdict not null,
  corrected_disease_id smallint references disease_catalog (id),
  note                 text check (char_length(note) <= 1000),
  created_at           timestamptz not null default now(),
  check (verdict <> 'correct' or corrected_disease_id is not null)
);
create index expert_reviews_scan on expert_reviews (scan_id);

create table feedback_labels (
  id                uuid primary key default gen_random_uuid(),
  review_id         uuid not null unique references expert_reviews (id) on delete cascade,
  disease_id        smallint not null references disease_catalog (id),
  consent_training  boolean not null,
  exported          boolean not null default false,
  created_at        timestamptz not null default now()
);

-- ── Alerts ──────────────────────────────────────────────────────────────────
create table alerts (
  id            uuid primary key default gen_random_uuid(),
  disease_id    smallint not null references disease_catalog (id),
  center_lat    numeric(6,2) not null,
  center_lon    numeric(6,2) not null,
  radius_km     real not null check (radius_km > 0 and radius_km <= 50),
  report_count  integer not null check (report_count > 0),
  risk          risk_level not null,
  rule_version  text not null,                -- 'rules-v1' until an ML model is promoted
  status        alert_status not null default 'draft',
  approved_by   uuid references profiles (id),
  message_bn    text,
  created_at    timestamptz not null default now()
);
create index alerts_status_time on alerts (status, created_at desc);

create table alert_subscriptions (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references profiles (id) on delete cascade,
  channel     notify_channel not null,
  radius_km   real not null default 5 check (radius_km between 1 and 50),
  created_at  timestamptz not null default now(),
  unique (user_id, channel)
);

-- ── Audit (append-only, hash-chained) ───────────────────────────────────────
create table audit_log (
  id          bigint generated always as identity primary key,
  actor_id    uuid,
  action      text not null,                  -- e.g. scan.analyze, review.correct, admin.threshold.update
  entity      text not null,
  entity_id   text,
  detail      jsonb not null default '{}',    -- never contains phone numbers or raw coordinates
  prev_hash   char(64),
  row_hash    char(64) not null,
  created_at  timestamptz not null default now()
);

create or replace function audit_append(p_actor uuid, p_action text, p_entity text,
                                        p_entity_id text, p_detail jsonb)
returns bigint language plpgsql security definer set search_path = public as $$
declare
  v_prev char(64);
  v_hash char(64);
  v_id   bigint;
begin
  perform pg_advisory_xact_lock(42);          -- serialise appends so the chain is linear
  select row_hash into v_prev from audit_log order by id desc limit 1;
  v_hash := encode(digest(coalesce(v_prev, '') || p_action || p_entity ||
                          coalesce(p_entity_id, '') || p_detail::text || now()::text, 'sha256'), 'hex');
  insert into audit_log (actor_id, action, entity, entity_id, detail, prev_hash, row_hash)
  values (p_actor, p_action, p_entity, p_entity_id, p_detail, v_prev, v_hash)
  returning id into v_id;
  return v_id;
end $$;

revoke update, delete on audit_log from public, anon, authenticated;
