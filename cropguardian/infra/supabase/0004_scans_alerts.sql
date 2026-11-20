-- Crop Guardian: bring the hosted Supabase DB from 0002 to 0004.
-- Paste into Supabase Dashboard -> SQL Editor and Run ONCE. Generated from the Alembic migrations
-- (backend/alembic/versions/0003_*.py and 0004_*.py); do not edit by hand.
-- Safe to re-run? 0003 yes (REVOKEs); 0004 no (CREATE TABLE) - the guard below stops a second run.
BEGIN;
DO $$ BEGIN IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='scans') THEN RAISE EXCEPTION 'scans already exists: 0004 was applied before'; END IF; END $$;
-- 0003 revoke API roles
DO $$
DECLARE r text;
BEGIN
  FOREACH r IN ARRAY ARRAY['anon', 'authenticated'] LOOP
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
      EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA public FROM %I', r);
      EXECUTE format('REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM %I', r);
      EXECUTE format('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM %I', r);
      EXECUTE format(
        'ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON FUNCTIONS FROM %I', r);
      EXECUTE format(
        'ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM %I', r);
    END IF;
  END LOOP;
END $$;
-- 0004 tables
CREATE TABLE scans (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  idempotency_key text NOT NULL CHECK (char_length(idempotency_key) BETWEEN 8 AND 80),
  image_sha256    text NOT NULL CHECK (image_sha256 ~ '^[0-9a-f]{64}$'),
  region_code     text NOT NULL CHECK (region_code ~ '^BD-[A-H]$'),
  status          text NOT NULL CHECK (status IN ('diagnosed','not_sure','healthy')),
  crop            text CHECK (crop IS NULL OR char_length(crop) <= 40),
  disease         text CHECK (disease IS NULL OR disease ~ '^[a-z_]{2,40}$'),
  confidence_band text CHECK (confidence_band IS NULL OR confidence_band IN ('high','medium')),
  reason          text CHECK (reason IS NULL OR reason ~ '^[a-z_]{2,40}$'),
  advice          jsonb NOT NULL DEFAULT '{}',
  citations       text[] NOT NULL DEFAULT '{}',
  advice_source   text NOT NULL DEFAULT 'none' CHECK (advice_source IN ('llm','static_card','none')),
  model           text CHECK (model IS NULL OR char_length(model) <= 120),
  prompt_version  text CHECK (prompt_version IS NULL OR char_length(prompt_version) <= 40),
  latency_ms      integer CHECK (latency_ms IS NULL OR latency_ms BETWEEN 0 AND 600000),
  synthetic       boolean NOT NULL DEFAULT false,
  created_at      timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT uq_scans_user_idem UNIQUE (user_id, idempotency_key)
);
CREATE INDEX ix_scans_user ON scans (user_id, created_at DESC);
CREATE INDEX ix_scans_cluster ON scans (tenant_id, disease, region_code, created_at DESC)
  WHERE status = 'diagnosed';

CREATE TABLE outbreak_alerts (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  disease      text NOT NULL CHECK (disease ~ '^[a-z_]{2,40}$'),
  region_code  text NOT NULL CHECK (region_code ~ '^BD-[A-H]$'),
  case_count   integer NOT NULL CHECK (case_count BETWEEN 1 AND 100000),
  window_start timestamptz NOT NULL,
  window_end   timestamptz NOT NULL,
  status       text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','approved','rejected')),
  decided_by   uuid REFERENCES users(id) ON DELETE SET NULL,
  decided_at   timestamptz,
  note         text CHECK (note IS NULL OR char_length(note) <= 500),
  synthetic    boolean NOT NULL DEFAULT false,
  created_at   timestamptz NOT NULL DEFAULT now(),
  CHECK (window_end >= window_start),
  CHECK ((status = 'draft') = (decided_at IS NULL))
);
-- at most one open draft per disease + division: new cases update it instead of duplicating
CREATE UNIQUE INDEX uq_alerts_open_draft ON outbreak_alerts (tenant_id, disease, region_code)
  WHERE status = 'draft';
CREATE INDEX ix_alerts_tenant ON outbreak_alerts (tenant_id, status, created_at DESC);
-- 0004 RLS
ALTER TABLE scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE scans FORCE ROW LEVEL SECURITY;
ALTER TABLE outbreak_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE outbreak_alerts FORCE ROW LEVEL SECURITY;

-- scans: a farmer sees and creates only their own rows; staff of the same tenant may read
-- (to review a draft alert's evidence). Nobody but SYSTEM updates or deletes.
CREATE POLICY scans_select ON scans FOR SELECT TO cg_app, cg_worker
  USING (is_system() OR (tenant_id = app_tenant()
         AND (user_id::text = app_uid() OR app_role() IN ('reviewer','admin'))));
CREATE POLICY scans_insert ON scans FOR INSERT TO cg_app, cg_worker
  WITH CHECK (is_system() OR (tenant_id = app_tenant() AND user_id::text = app_uid()));
CREATE POLICY scans_system ON scans FOR UPDATE TO cg_app, cg_worker
  USING (is_system()) WITH CHECK (is_system());
CREATE POLICY scans_delete ON scans FOR DELETE TO cg_app, cg_worker USING (is_system());

-- alerts: farmers read APPROVED alerts of their tenant only; staff read all of their tenant.
-- Drafts are created by SYSTEM (the outbreak rule); reviewers/admins decide them.
CREATE POLICY alerts_select ON outbreak_alerts FOR SELECT TO cg_app, cg_worker
  USING (is_system() OR (tenant_id = app_tenant()
         AND (status = 'approved' OR app_role() IN ('reviewer','admin'))));
CREATE POLICY alerts_insert ON outbreak_alerts FOR INSERT TO cg_app, cg_worker
  WITH CHECK (is_system());
CREATE POLICY alerts_update ON outbreak_alerts FOR UPDATE TO cg_app, cg_worker
  USING (is_system() OR (tenant_id = app_tenant() AND app_role() IN ('reviewer','admin')))
  WITH CHECK (is_system() OR (tenant_id = app_tenant() AND app_role() IN ('reviewer','admin')));
CREATE POLICY alerts_delete ON outbreak_alerts FOR DELETE TO cg_app, cg_worker USING (is_system());
-- 0004 grants
GRANT SELECT, INSERT, UPDATE, DELETE ON scans, outbreak_alerts TO cg_app, cg_worker;
DO $$
DECLARE r text;
BEGIN
  FOREACH r IN ARRAY ARRAY['anon', 'authenticated'] LOOP
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
      EXECUTE format('REVOKE ALL ON scans, outbreak_alerts FROM %I', r);
    END IF;
  END LOOP;
END $$;
UPDATE alembic_version SET version_num = '0004';
COMMIT;
-- verify: SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class WHERE relname IN ('scans','outbreak_alerts');
