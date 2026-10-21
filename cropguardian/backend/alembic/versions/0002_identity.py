"""identity: users, sessions, otp, email tokens, totp, recovery codes, consents, push, invites,
notifications, email outbox + RLS (spec 7.1, 16.4, 16.10)

Revision ID: 0002
Revises: 0001

Design notes
- Every user-data table has `tenant_id` ('real'|'demo') and an ownership column; ENABLE + FORCE RLS.
- Three kinds of access, all enforced by policies (not by application code alone):
    own rows     tenant_id = app_tenant() AND owner = app_uid()
    admin        is_admin() inside the admin's tenant
    SYSTEM       is_system(): set ONLY by server code (pre-auth lookups, session rotation, cleanup),
                 never derived from request data
- Missing context (no app.user_id / app.tenant) matches nothing: the helper functions return NULL and
  `x = NULL` is never true.
- `users_guard` trigger: anything that is not SYSTEM/admin may only change display_name/locale, so a
  mass-assignment bug (role, tenant_id, status...) is stopped in the database too.
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

OWN = "tenant_id = app_tenant() AND user_id::text = app_uid()"
HEX64 = "'^[0-9a-f]{64}$'"

TABLES_SQL = f"""
CREATE TABLE users (
  id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id         text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  role              text NOT NULL CHECK (role IN
                      ('FARMER','REVIEWER','ADMIN','DEMO_FARMER','DEMO_REVIEWER','DEMO_ADMIN')),
  phone_e164        text UNIQUE CHECK (phone_e164 ~ '^\\+[1-9][0-9]{{7,14}}$'),
  email             text CHECK (char_length(email) BETWEEN 3 AND 254),
  display_name      text NOT NULL CHECK (char_length(display_name) BETWEEN 1 AND 80),
  locale            text NOT NULL DEFAULT 'bn' CHECK (locale IN ('bn','en')),
  password_hash     text CHECK (password_hash IS NULL OR password_hash LIKE '$argon2id$%'),
  status            text NOT NULL DEFAULT 'PENDING'
                      CHECK (status IN ('PENDING','ACTIVE','SUSPENDED','DELETED')),
  region_codes      text[] NOT NULL DEFAULT '{{}}',
  failed_logins     integer NOT NULL DEFAULT 0 CHECK (failed_logins >= 0),
  last_failed_at    timestamptz,
  locked_until      timestamptz,
  phone_verified_at timestamptz,
  email_verified_at timestamptz,
  created_at        timestamptz NOT NULL DEFAULT now(),
  updated_at        timestamptz NOT NULL DEFAULT now(),
  -- demo roles live only in the demo tenant, and the demo tenant holds only demo roles
  CONSTRAINT ck_users_demo_tenant CHECK (
    (tenant_id = 'demo') = (role IN ('DEMO_FARMER','DEMO_REVIEWER','DEMO_ADMIN'))),
  -- farmers sign in by phone; staff by email
  CONSTRAINT ck_users_farmer_phone CHECK (role <> 'FARMER' OR phone_e164 IS NOT NULL),
  CONSTRAINT ck_users_staff_email CHECK (role NOT IN ('REVIEWER','ADMIN') OR email IS NOT NULL)
);
CREATE UNIQUE INDEX uq_users_email_lower ON users (lower(email)) WHERE email IS NOT NULL;
CREATE INDEX ix_users_tenant_role ON users (tenant_id, role);

CREATE TABLE sessions (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id            text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  user_id              uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash           text NOT NULL UNIQUE CHECK (token_hash ~ {HEX64}),
  csrf_secret          text NOT NULL CHECK (char_length(csrf_secret) BETWEEN 32 AND 128),
  keep_signed_in       boolean NOT NULL DEFAULT false,
  created_at           timestamptz NOT NULL DEFAULT now(),
  last_seen_at         timestamptz NOT NULL DEFAULT now(),
  rotated_from         uuid REFERENCES sessions(id) ON DELETE SET NULL,
  expires_at           timestamptz NOT NULL,
  absolute_expires_at  timestamptz NOT NULL,
  ip_hash              text,
  user_agent           text CHECK (char_length(user_agent) <= 255),
  totp_verified_at     timestamptz,
  step_up_at           timestamptz,
  revoked_at           timestamptz,
  CONSTRAINT ck_sessions_expiry CHECK (expires_at <= absolute_expires_at + interval '1 minute')
);
CREATE INDEX ix_sessions_user_active ON sessions (user_id) WHERE revoked_at IS NULL;

CREATE TABLE otp_codes (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  purpose         text NOT NULL CHECK (purpose IN ('register','login','reset')),
  code_hmac       text NOT NULL CHECK (code_hmac ~ {HEX64}),
  expires_at      timestamptz NOT NULL,
  attempts        integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  sent_count_hour integer NOT NULL DEFAULT 1 CHECK (sent_count_hour >= 0),
  created_at      timestamptz NOT NULL DEFAULT now(),
  consumed_at     timestamptz
);
CREATE INDEX ix_otp_user_purpose ON otp_codes (user_id, purpose, created_at DESC);

CREATE TABLE email_tokens (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  purpose     text NOT NULL CHECK (purpose IN ('verify','reset')),
  token_hash  text NOT NULL UNIQUE CHECK (token_hash ~ {HEX64}),
  expires_at  timestamptz NOT NULL,
  consumed_at timestamptz,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE totp_credentials (
  user_id        uuid PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  tenant_id      text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  secret_enc     text NOT NULL,
  confirmed_at   timestamptz,
  last_used_step bigint,
  created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE recovery_codes (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  user_id    uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  code_hash  text NOT NULL CHECK (code_hash LIKE '$argon2id$%'),
  used_at    timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_recovery_user ON recovery_codes (user_id) WHERE used_at IS NULL;

CREATE TABLE consents (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id    text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  user_id      uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  purpose      text NOT NULL CHECK (purpose IN ('service','training_use','push_alerts')),
  granted      boolean NOT NULL,
  text_version text NOT NULL CHECK (char_length(text_version) BETWEEN 1 AND 40),
  granted_at   timestamptz,
  withdrawn_at timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, purpose, text_version)
);

CREATE TABLE push_subscriptions (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id       text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  endpoint_hash   text NOT NULL UNIQUE CHECK (endpoint_hash ~ {HEX64}),
  endpoint_enc    text NOT NULL,
  keys_enc        text NOT NULL,
  created_at      timestamptz NOT NULL DEFAULT now(),
  last_success_at timestamptz,
  failures        integer NOT NULL DEFAULT 0 CHECK (failures >= 0)
);

CREATE TABLE invites (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id   text NOT NULL DEFAULT 'real' CHECK (tenant_id = 'real'),
  user_id     uuid NOT NULL REFERENCES users(id),   -- the inviting admin (ownership column)
  email       text NOT NULL CHECK (char_length(email) BETWEEN 3 AND 254),
  role        text NOT NULL CHECK (role IN ('REVIEWER','ADMIN')),
  region_codes text[] NOT NULL DEFAULT '{{}}',
  token_hash  text NOT NULL UNIQUE CHECK (token_hash ~ {HEX64}),
  expires_at  timestamptz NOT NULL,
  consumed_at timestamptz,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE notifications (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  user_id    uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  kind       text NOT NULL CHECK (char_length(kind) BETWEEN 1 AND 40),
  payload    jsonb NOT NULL DEFAULT '{{}}',
  -- spec 14: every notification link is a validated in-app path (never // or a scheme or a backslash)
  link_path  text CHECK (link_path IS NULL OR (link_path ~ '^/([^/:][^:]*)?$' AND strpos(link_path, chr(92)) = 0)),
  security   boolean NOT NULL DEFAULT false,        -- security notices ignore user preferences
  read_at    timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_notifications_user ON notifications (user_id, created_at DESC);

CREATE TABLE email_outbox (
  id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  text NOT NULL DEFAULT 'real' CHECK (tenant_id IN ('real','demo')),
  user_id    uuid REFERENCES users(id) ON DELETE SET NULL,
  to_email   text NOT NULL CHECK (char_length(to_email) BETWEEN 3 AND 254),
  kind       text NOT NULL CHECK (kind IN ('verify','reset','invite','new_device')),
  subject    text NOT NULL,
  body_text  text NOT NULL,
  body_html  text NOT NULL,
  dedupe_key text UNIQUE,                            -- never send the same message twice
  status     text NOT NULL DEFAULT 'queued' CHECK (status IN ('queued','sent','failed','suppressed')),
  attempts   integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  last_error text,
  created_at timestamptz NOT NULL DEFAULT now(),
  sent_at    timestamptz
);
CREATE INDEX ix_email_outbox_queued ON email_outbox (created_at) WHERE status = 'queued';

ALTER TABLE idempotency_keys ADD COLUMN route text NOT NULL DEFAULT '';
"""

FUNCTIONS_SQL = """
CREATE OR REPLACE FUNCTION touch_updated_at() RETURNS trigger LANGUAGE plpgsql
  SET search_path = pg_catalog, public AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END $$;

-- Defence in depth against mass assignment: outside SYSTEM, only display_name/locale may change; an
-- admin may also change status/role/region (the service demands step-up) but never id or tenant.
CREATE OR REPLACE FUNCTION users_guard() RETURNS trigger LANGUAGE plpgsql
  SET search_path = pg_catalog, public AS $$
BEGIN
  IF is_system() THEN
    RETURN NEW;
  END IF;
  IF NEW.id IS DISTINCT FROM OLD.id OR NEW.tenant_id IS DISTINCT FROM OLD.tenant_id THEN
    RAISE EXCEPTION 'users.id and users.tenant_id are immutable' USING ERRCODE = 'insufficient_privilege';
  END IF;
  IF is_admin() THEN
    IF NEW.password_hash IS DISTINCT FROM OLD.password_hash
       OR NEW.phone_e164 IS DISTINCT FROM OLD.phone_e164
       OR NEW.email IS DISTINCT FROM OLD.email
       OR NEW.failed_logins IS DISTINCT FROM OLD.failed_logins THEN
      RAISE EXCEPTION 'admins cannot change credentials or contact details'
        USING ERRCODE = 'insufficient_privilege';
    END IF;
    RETURN NEW;
  END IF;
  IF NEW.role IS DISTINCT FROM OLD.role
     OR NEW.status IS DISTINCT FROM OLD.status
     OR NEW.region_codes IS DISTINCT FROM OLD.region_codes
     OR NEW.password_hash IS DISTINCT FROM OLD.password_hash
     OR NEW.phone_e164 IS DISTINCT FROM OLD.phone_e164
     OR NEW.email IS DISTINCT FROM OLD.email
     OR NEW.failed_logins IS DISTINCT FROM OLD.failed_logins
     OR NEW.locked_until IS DISTINCT FROM OLD.locked_until
     OR NEW.last_failed_at IS DISTINCT FROM OLD.last_failed_at
     OR NEW.phone_verified_at IS DISTINCT FROM OLD.phone_verified_at
     OR NEW.email_verified_at IS DISTINCT FROM OLD.email_verified_at
     OR NEW.created_at IS DISTINCT FROM OLD.created_at THEN
    RAISE EXCEPTION 'only display_name and locale may be changed here'
      USING ERRCODE = 'insufficient_privilege';
  END IF;
  RETURN NEW;
END $$;

CREATE TRIGGER trg_users_touch BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION touch_updated_at();
CREATE TRIGGER trg_users_guard BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION users_guard();
"""

ALL_TABLES = (
    "users", "sessions", "otp_codes", "email_tokens", "totp_credentials", "recovery_codes",
    "consents", "push_subscriptions", "invites", "notifications", "email_outbox",
)  # fmt: skip

RLS_SQL = (
    "\n".join(
        f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY;\nALTER TABLE {t} FORCE ROW LEVEL SECURITY;"
        for t in ALL_TABLES
    )
    + f"""

-- users: own row or admin (within the tenant); SYSTEM for registration and credential updates
CREATE POLICY users_select ON users FOR SELECT TO cg_app, cg_worker
  USING (is_system() OR (tenant_id = app_tenant() AND (id::text = app_uid() OR is_admin())));
CREATE POLICY users_insert ON users FOR INSERT TO cg_app, cg_worker WITH CHECK (is_system());
CREATE POLICY users_update ON users FOR UPDATE TO cg_app, cg_worker
  USING (is_system() OR (tenant_id = app_tenant() AND (id::text = app_uid() OR is_admin())))
  WITH CHECK (is_system() OR (tenant_id = app_tenant() AND (id::text = app_uid() OR is_admin())));
CREATE POLICY users_delete ON users FOR DELETE TO cg_app, cg_worker USING (is_system());

-- sessions: the owner can list their own; every write is SYSTEM (rotation, revoke, cleanup)
CREATE POLICY sessions_select ON sessions FOR SELECT TO cg_app, cg_worker
  USING (is_system() OR ({OWN}));
CREATE POLICY sessions_write ON sessions FOR ALL TO cg_app, cg_worker
  USING (is_system()) WITH CHECK (is_system());

-- credentials / one-time secrets: owner may read their own rows; writes are SYSTEM only
CREATE POLICY otp_select ON otp_codes FOR SELECT TO cg_app, cg_worker USING (is_system() OR ({OWN}));
CREATE POLICY otp_write ON otp_codes FOR ALL TO cg_app, cg_worker
  USING (is_system()) WITH CHECK (is_system());
CREATE POLICY etok_select ON email_tokens FOR SELECT TO cg_app, cg_worker
  USING (is_system() OR ({OWN}));
CREATE POLICY etok_write ON email_tokens FOR ALL TO cg_app, cg_worker
  USING (is_system()) WITH CHECK (is_system());
CREATE POLICY totp_select ON totp_credentials FOR SELECT TO cg_app, cg_worker
  USING (is_system() OR ({OWN}));
CREATE POLICY totp_write ON totp_credentials FOR ALL TO cg_app, cg_worker
  USING (is_system()) WITH CHECK (is_system());
CREATE POLICY rc_select ON recovery_codes FOR SELECT TO cg_app, cg_worker
  USING (is_system() OR ({OWN}));
CREATE POLICY rc_write ON recovery_codes FOR ALL TO cg_app, cg_worker
  USING (is_system()) WITH CHECK (is_system());

-- consents and push subscriptions: the owner manages their own rows
CREATE POLICY consents_own ON consents FOR ALL TO cg_app, cg_worker
  USING (is_system() OR ({OWN})) WITH CHECK (is_system() OR ({OWN}));
CREATE POLICY push_own ON push_subscriptions FOR ALL TO cg_app, cg_worker
  USING (is_system() OR ({OWN})) WITH CHECK (is_system() OR ({OWN}));

-- invites: SYSTEM writes; admins read their tenant's invites
CREATE POLICY invites_select ON invites FOR SELECT TO cg_app, cg_worker
  USING (is_system() OR (tenant_id = app_tenant() AND is_admin()));
CREATE POLICY invites_write ON invites FOR ALL TO cg_app, cg_worker
  USING (is_system()) WITH CHECK (is_system());

-- notifications: the owner reads and marks read; SYSTEM creates
CREATE POLICY notif_select ON notifications FOR SELECT TO cg_app, cg_worker
  USING (is_system() OR ({OWN}));
CREATE POLICY notif_update ON notifications FOR UPDATE TO cg_app, cg_worker
  USING (is_system() OR ({OWN})) WITH CHECK (is_system() OR ({OWN}));
CREATE POLICY notif_insert ON notifications FOR INSERT TO cg_app, cg_worker WITH CHECK (is_system());
CREATE POLICY notif_delete ON notifications FOR DELETE TO cg_app, cg_worker USING (is_system());

-- email outbox contains one-time links: SYSTEM only, nobody else can read it (not even admins)
CREATE POLICY outbox_system ON email_outbox FOR ALL TO cg_app, cg_worker
  USING (is_system()) WITH CHECK (is_system());

-- audit_log (0001) accepts SYSTEM inserts too, for events where the tenant is not known yet
CREATE POLICY al_insert_system ON audit_log FOR INSERT TO cg_app, cg_worker WITH CHECK (is_system());
"""
)

GRANTS_SQL = """
GRANT SELECT, INSERT, UPDATE ON users, consents, push_subscriptions, notifications TO cg_app, cg_worker;
GRANT SELECT, INSERT, UPDATE, DELETE ON sessions, otp_codes, email_tokens, totp_credentials,
  recovery_codes, invites, email_outbox TO cg_app, cg_worker;
GRANT DELETE ON users, consents, push_subscriptions, notifications TO cg_app, cg_worker;
-- cg_readonly gets NOTHING on identity tables (no secrets in reports).

-- Supabase grants new tables to anon/authenticated/service_role by default; take that away again.
DO $$
DECLARE r text;
BEGIN
  FOREACH r IN ARRAY ARRAY['anon', 'authenticated'] LOOP
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
      EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA public FROM %I', r);
      EXECUTE format('REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM %I', r);
    END IF;
  END LOOP;
END $$;
"""

# The audit chain trigger runs as the inserting role and must read the previous row's hash. Under
# FORCE RLS a non-admin cannot see audit rows, so every chain would silently restart at genesis.
# `audit_tail_hash()` is SECURITY DEFINER (runs as the migration owner, which gets a SELECT policy),
# and the trigger takes its lock BEFORE assigning the id, so id order == chain order under concurrency.
AUDIT_FIX_SQL = """
CREATE OR REPLACE FUNCTION audit_tail_hash() RETURNS text LANGUAGE sql STABLE SECURITY DEFINER
  SET search_path = pg_catalog, public
  AS $$ SELECT row_hash FROM audit_log ORDER BY id DESC LIMIT 1 $$;
REVOKE ALL ON FUNCTION audit_tail_hash() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION audit_tail_hash() TO cg_app, cg_worker;
CREATE POLICY al_chain_owner ON audit_log FOR SELECT TO CURRENT_USER USING (true);

CREATE OR REPLACE FUNCTION audit_log_chain() RETURNS trigger LANGUAGE plpgsql
  SET search_path = pg_catalog, public AS $$
BEGIN
  PERFORM pg_advisory_xact_lock(7001);
  NEW.id := nextval(pg_get_serial_sequence('audit_log', 'id'));
  NEW.prev_hash := COALESCE(audit_tail_hash(), repeat('0', 64));
  NEW.canonical := jsonb_build_object(
    'at', to_char(NEW.at AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'),
    'actor_id', NEW.actor_id, 'actor_role', NEW.actor_role, 'tenant_id', NEW.tenant_id,
    'action', NEW.action, 'object_type', NEW.object_type, 'object_id', NEW.object_id,
    'request_id', NEW.request_id, 'ip_hash', NEW.ip_hash, 'before', NEW.before, 'after', NEW.after
  )::text;
  NEW.row_hash := encode(sha256(convert_to(NEW.prev_hash || '|' || NEW.canonical, 'UTF8')), 'hex');
  RETURN NEW;
END $$;

-- Verification must see every row regardless of who asks (it returns only the first bad id or 0).
CREATE OR REPLACE FUNCTION audit_verify_chain() RETURNS bigint LANGUAGE plpgsql STABLE
  SECURITY DEFINER SET search_path = pg_catalog, public AS $$
DECLARE
  r record;
  prev text := repeat('0', 64);
BEGIN
  FOR r IN SELECT id, canonical, prev_hash, row_hash FROM audit_log ORDER BY id LOOP
    IF r.prev_hash <> prev
       OR r.row_hash <> encode(sha256(convert_to(prev || '|' || r.canonical, 'UTF8')), 'hex') THEN
      RETURN r.id;
    END IF;
    prev := r.row_hash;
  END LOOP;
  RETURN 0;
END $$;
REVOKE ALL ON FUNCTION audit_verify_chain() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION audit_verify_chain() TO cg_app, cg_worker, cg_readonly;
"""

AUDIT_FIX_DOWN_SQL = """
DROP POLICY IF EXISTS al_chain_owner ON audit_log;
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
CREATE OR REPLACE FUNCTION audit_verify_chain() RETURNS bigint LANGUAGE plpgsql STABLE
  SET search_path = pg_catalog, public AS $$
DECLARE
  r record;
  prev text := repeat('0', 64);
BEGIN
  FOR r IN SELECT id, canonical, prev_hash, row_hash FROM audit_log ORDER BY id LOOP
    IF r.prev_hash <> prev
       OR r.row_hash <> encode(sha256(convert_to(prev || '|' || r.canonical, 'UTF8')), 'hex') THEN
      RETURN r.id;
    END IF;
    prev := r.row_hash;
  END LOOP;
  RETURN 0;
END $$;
DROP FUNCTION IF EXISTS audit_tail_hash();
"""


def upgrade() -> None:
    for block in (TABLES_SQL, FUNCTIONS_SQL, RLS_SQL, GRANTS_SQL, AUDIT_FIX_SQL):
        op.execute(block)


def downgrade() -> None:
    op.execute(AUDIT_FIX_DOWN_SQL)
    op.execute("DROP POLICY IF EXISTS al_insert_system ON audit_log")
    op.execute(
        "DROP TABLE IF EXISTS email_outbox, notifications, invites, push_subscriptions, consents, "
        "recovery_codes, totp_credentials, email_tokens, otp_codes, sessions, users CASCADE"
    )
    op.execute("DROP FUNCTION IF EXISTS users_guard()")
    op.execute("DROP FUNCTION IF EXISTS touch_updated_at()")
    op.execute("ALTER TABLE idempotency_keys DROP COLUMN IF EXISTS route")
