"""scans + outbreak alerts (Gantt P2/P3): diagnosis results, cited advice, human-approved alerts

Revision ID: 0004
Revises: 0003

Privacy (DECISIONS D-032): the leaf photo itself is NOT stored. A scan row keeps only the SHA-256 of
the re-encoded image (dedupe), the farmer-chosen division code (coarse location, never GPS), the
diagnosis and the validated advice. Alerts are drafts until a reviewer approves them.
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

TABLES_SQL = """
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
"""

RLS_SQL = """
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
"""

GRANTS_SQL = """
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
"""


def upgrade() -> None:
    for block in (TABLES_SQL, RLS_SQL, GRANTS_SQL):
        op.execute(block)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS outbreak_alerts, scans CASCADE")
