-- Compose-only bootstrap (spec 16.10). Supabase gets the same roles from Alembic migration 0001.
-- cg_migrator owns the schema. cg_app / cg_worker / cg_readonly are NOLOGIN roles the API reaches via
-- SET LOCAL ROLE. The API login user `cg_api` is a NOINHERIT member of those roles: it holds no
-- privileges of its own, cannot bypass RLS, and is not an owner.
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cg_migrator') THEN
    CREATE ROLE cg_migrator LOGIN PASSWORD 'dev-migrator-pw' CREATEROLE;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'cg_api') THEN
    CREATE ROLE cg_api LOGIN PASSWORD 'dev-api-pw' NOINHERIT NOBYPASSRLS;
  END IF;
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

GRANT cg_app, cg_worker, cg_readonly TO cg_api;
GRANT cg_app, cg_worker, cg_readonly TO cg_migrator;
CREATE EXTENSION IF NOT EXISTS vector;
GRANT ALL ON DATABASE cropguardian TO cg_migrator;
GRANT CONNECT ON DATABASE cropguardian TO cg_api;
ALTER SCHEMA public OWNER TO cg_migrator;
