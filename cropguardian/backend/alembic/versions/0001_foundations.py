"""foundations: extensions, roles, helpers, platform_settings, audit_log (hash chain), ops tables

Revision ID: 0001
Revises:
"""

import json

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

ROLES_SQL = """
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cg_app') THEN
    CREATE ROLE cg_app NOLOGIN NOBYPASSRLS;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cg_worker') THEN
    CREATE ROLE cg_worker NOLOGIN NOBYPASSRLS;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cg_readonly') THEN
    CREATE ROLE cg_readonly NOLOGIN NOBYPASSRLS;
  END IF;
END $$;
-- The connecting user may only SET ROLE into these (membership), never bypass RLS itself.
DO $$
BEGIN
  EXECUTE format('GRANT cg_app, cg_worker, cg_readonly TO %I', current_user);
EXCEPTION WHEN OTHERS THEN
  RAISE NOTICE 'role membership grant skipped: %', SQLERRM;
END $$;
GRANT USAGE ON SCHEMA public TO cg_app, cg_worker, cg_readonly;
"""

HELPERS_SQL = """
CREATE OR REPLACE FUNCTION app_uid() RETURNS text LANGUAGE sql STABLE
  SET search_path = pg_catalog, public
  AS $$ SELECT NULLIF(current_setting('app.user_id', true), '') $$;
CREATE OR REPLACE FUNCTION app_role() RETURNS text LANGUAGE sql STABLE
  SET search_path = pg_catalog, public
  AS $$ SELECT NULLIF(current_setting('app.role', true), '') $$;
CREATE OR REPLACE FUNCTION app_tenant() RETURNS text LANGUAGE sql STABLE
  SET search_path = pg_catalog, public
  AS $$ SELECT NULLIF(current_setting('app.tenant', true), '') $$;
CREATE OR REPLACE FUNCTION is_admin() RETURNS boolean LANGUAGE sql STABLE
  SET search_path = pg_catalog, public
  AS $$ SELECT COALESCE(app_role() = 'admin', false) $$;
CREATE OR REPLACE FUNCTION is_system() RETURNS boolean LANGUAGE sql STABLE
  SET search_path = pg_catalog, public
  AS $$ SELECT COALESCE(app_role() = 'system', false) $$;
CREATE OR REPLACE FUNCTION in_region(code text) RETURNS boolean LANGUAGE sql STABLE
  SET search_path = pg_catalog, public
  AS $$ SELECT code IS NOT NULL
        AND code = ANY (string_to_array(COALESCE(current_setting('app.region', true), ''), ',')) $$;

CREATE OR REPLACE FUNCTION reject_mutation() RETURNS trigger LANGUAGE plpgsql
  SET search_path = pg_catalog, public AS $$
BEGIN
  RAISE EXCEPTION '% is append-only', TG_TABLE_NAME USING ERRCODE = 'insufficient_privilege';
END $$;
"""

TABLES_SQL = """
CREATE TABLE platform_settings (
  id          bigserial PRIMARY KEY,
  key         text NOT NULL,
  value       jsonb NOT NULL,
  version     integer NOT NULL CHECK (version >= 1),
  changed_by  text,
  reason      text NOT NULL CHECK (char_length(reason) >= 10),
  created_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (key, version)
);

CREATE TABLE audit_log (
  id          bigserial PRIMARY KEY,
  at          timestamptz NOT NULL DEFAULT now(),
  actor_id    text,
  actor_role  text,
  tenant_id   text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  action      text NOT NULL,
  object_type text,
  object_id   text,
  request_id  text,
  ip_hash     text,
  before      jsonb,
  after       jsonb,
  canonical   text NOT NULL DEFAULT '',
  prev_hash   text NOT NULL DEFAULT '',
  row_hash    text NOT NULL DEFAULT ''
);
CREATE INDEX ix_audit_log_at ON audit_log (at);

CREATE TABLE jobs_log (
  id          bigserial PRIMARY KEY,
  job_name    text NOT NULL,
  job_id      text,
  status      text NOT NULL CHECK (status IN ('queued','running','succeeded','failed')),
  started_at  timestamptz,
  finished_at timestamptz,
  error_code  text,
  attempts    integer NOT NULL DEFAULT 0
);

CREATE TABLE idempotency_keys (
  id            bigserial PRIMARY KEY,
  user_id       text NOT NULL,
  tenant_id     text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  key           text NOT NULL CHECK (char_length(key) BETWEEN 8 AND 128),
  request_hash  text NOT NULL,
  response_code integer,
  response_body jsonb,
  created_at    timestamptz NOT NULL DEFAULT now(),
  expires_at    timestamptz NOT NULL DEFAULT now() + interval '24 hours',
  UNIQUE (user_id, key)
);

CREATE TABLE client_errors (
  id           bigserial PRIMARY KEY,
  at           timestamptz NOT NULL DEFAULT now(),
  route        text,
  message_hash text NOT NULL,
  sample       jsonb,
  count        integer NOT NULL DEFAULT 1
);
"""

AUDIT_SQL = """
-- Serialised hash chain computed server-side so the application can never forge or skip a link.
CREATE OR REPLACE FUNCTION audit_log_chain() RETURNS trigger LANGUAGE plpgsql
  SET search_path = pg_catalog, public AS $$
DECLARE
  prev text;
BEGIN
  PERFORM pg_advisory_xact_lock(7001);
  SELECT row_hash INTO prev FROM audit_log ORDER BY id DESC LIMIT 1;
  NEW.prev_hash := COALESCE(prev, repeat('0', 64));
  NEW.canonical := jsonb_build_object(
    'at', to_char(NEW.at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
    'actor_id', NEW.actor_id, 'actor_role', NEW.actor_role, 'tenant_id', NEW.tenant_id,
    'action', NEW.action, 'object_type', NEW.object_type, 'object_id', NEW.object_id,
    'request_id', NEW.request_id, 'ip_hash', NEW.ip_hash, 'before', NEW.before, 'after', NEW.after
  )::text;
  NEW.row_hash := encode(sha256(convert_to(NEW.prev_hash || '|' || NEW.canonical, 'UTF8')), 'hex');
  RETURN NEW;
END $$;

CREATE TRIGGER trg_audit_log_chain BEFORE INSERT ON audit_log
  FOR EACH ROW EXECUTE FUNCTION audit_log_chain();
CREATE TRIGGER trg_audit_log_no_update BEFORE UPDATE OR DELETE ON audit_log
  FOR EACH ROW EXECUTE FUNCTION reject_mutation();
CREATE TRIGGER trg_audit_log_no_truncate BEFORE TRUNCATE ON audit_log
  FOR EACH STATEMENT EXECUTE FUNCTION reject_mutation();
CREATE TRIGGER trg_platform_settings_no_update BEFORE UPDATE OR DELETE ON platform_settings
  FOR EACH ROW EXECUTE FUNCTION reject_mutation();
CREATE TRIGGER trg_platform_settings_no_truncate BEFORE TRUNCATE ON platform_settings
  FOR EACH STATEMENT EXECUTE FUNCTION reject_mutation();

CREATE OR REPLACE FUNCTION audit_verify_chain() RETURNS bigint LANGUAGE plpgsql STABLE
  SET search_path = pg_catalog, public AS $$
DECLARE
  r record;
  prev text := repeat('0', 64);
BEGIN
  FOR r IN SELECT id, canonical, prev_hash, row_hash FROM audit_log ORDER BY id LOOP
    IF r.prev_hash <> prev
       OR r.row_hash <> encode(sha256(convert_to(prev || '|' || r.canonical, 'UTF8')), 'hex') THEN
      RETURN r.id;  -- first broken row
    END IF;
    prev := r.row_hash;
  END LOOP;
  RETURN 0;  -- chain intact
END $$;
"""

RLS_SQL = """
ALTER TABLE platform_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_settings FORCE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log FORCE ROW LEVEL SECURITY;
ALTER TABLE jobs_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs_log FORCE ROW LEVEL SECURITY;
ALTER TABLE idempotency_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE idempotency_keys FORCE ROW LEVEL SECURITY;
ALTER TABLE client_errors ENABLE ROW LEVEL SECURITY;
ALTER TABLE client_errors FORCE ROW LEVEL SECURITY;

-- platform_settings: admin or SYSTEM read; admin or SYSTEM append
CREATE POLICY ps_select ON platform_settings FOR SELECT TO cg_app, cg_worker, cg_readonly
  USING (is_admin() OR is_system());
CREATE POLICY ps_insert ON platform_settings FOR INSERT TO cg_app, cg_worker
  WITH CHECK (is_admin() OR is_system());

-- audit_log: admin reads within tenant; any request may append inside its own tenant
CREATE POLICY al_select ON audit_log FOR SELECT TO cg_app, cg_worker, cg_readonly
  USING (is_admin() AND tenant_id = app_tenant());
CREATE POLICY al_insert ON audit_log FOR INSERT TO cg_app, cg_worker
  WITH CHECK (tenant_id = app_tenant());

-- jobs_log: SYSTEM / worker writes; admin reads
CREATE POLICY jl_select ON jobs_log FOR SELECT TO cg_app, cg_worker, cg_readonly
  USING (is_admin() OR is_system());
CREATE POLICY jl_write ON jobs_log FOR ALL TO cg_app, cg_worker
  USING (is_system()) WITH CHECK (is_system());

-- idempotency_keys: own rows inside own tenant (missing context matches nothing)
CREATE POLICY ik_own ON idempotency_keys FOR ALL TO cg_app, cg_worker
  USING (user_id = app_uid() AND tenant_id = app_tenant())
  WITH CHECK (user_id = app_uid() AND tenant_id = app_tenant());

-- client_errors: any app request may report; admin reads
CREATE POLICY ce_select ON client_errors FOR SELECT TO cg_app, cg_worker, cg_readonly
  USING (is_admin());
CREATE POLICY ce_insert ON client_errors FOR INSERT TO cg_app, cg_worker WITH CHECK (true);
"""

GRANTS_SQL = """
-- Least privilege: no UPDATE/DELETE on append-only tables (triggers are the second wall).
GRANT SELECT, INSERT ON platform_settings, audit_log TO cg_app, cg_worker;
GRANT SELECT ON platform_settings, audit_log, jobs_log, client_errors TO cg_readonly;
GRANT SELECT, INSERT, UPDATE ON jobs_log TO cg_app, cg_worker;
GRANT SELECT, INSERT, UPDATE, DELETE ON idempotency_keys TO cg_app, cg_worker;
GRANT SELECT, INSERT ON client_errors TO cg_app, cg_worker;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO cg_app, cg_worker;
GRANT EXECUTE ON FUNCTION audit_verify_chain() TO cg_app, cg_worker, cg_readonly;

-- Supabase exposes `public` through PostgREST as anon/authenticated: shut that door.
DO $$
DECLARE r text;
BEGIN
  FOREACH r IN ARRAY ARRAY['anon', 'authenticated'] LOOP
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
      EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA public FROM %I', r);
      EXECUTE format('REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM %I', r);
      EXECUTE format('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM %I', r);
    END IF;
  END LOOP;
END $$;
"""


def upgrade() -> None:
    from app.core.platform_settings import defaults, validate_all

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    for block in (ROLES_SQL, HELPERS_SQL, TABLES_SQL, AUDIT_SQL):
        op.execute(block)

    # Seed BEFORE enabling FORCE RLS: the owner is subject to policies once they are forced.
    seed = validate_all(defaults())  # refuse to seed an invalid default set
    for key, value in sorted(seed.items()):
        op.execute(
            "INSERT INTO platform_settings (key, value, version, changed_by, reason) VALUES "
            f"('{key}', '{json.dumps(value)}'::jsonb, 1, 'system', 'initial default (migration 0001)')"
        )

    for block in (RLS_SQL, GRANTS_SQL):
        op.execute(block)


def downgrade() -> None:
    for stmt in (
        "DROP TABLE IF EXISTS client_errors, idempotency_keys, jobs_log, audit_log, platform_settings CASCADE",
        "DROP FUNCTION IF EXISTS audit_verify_chain()",
        "DROP FUNCTION IF EXISTS audit_log_chain()",
        "DROP FUNCTION IF EXISTS reject_mutation()",
        "DROP FUNCTION IF EXISTS in_region(text)",
        "DROP FUNCTION IF EXISTS is_system()",
        "DROP FUNCTION IF EXISTS is_admin()",
        "DROP FUNCTION IF EXISTS app_tenant()",
        "DROP FUNCTION IF EXISTS app_role()",
        "DROP FUNCTION IF EXISTS app_uid()",
    ):
        op.execute(stmt)
    # Roles and the vector extension are shared cluster objects and are intentionally kept.
