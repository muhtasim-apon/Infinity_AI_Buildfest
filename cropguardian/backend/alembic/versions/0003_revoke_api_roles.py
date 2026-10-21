"""close the PostgREST door for functions created after the 0001/0002 revoke blocks

Revision ID: 0003
Revises: 0002

Supabase grants EXECUTE on every new function directly to `anon` and `authenticated`, so
`REVOKE ... FROM PUBLIC` does not remove it. Migration 0002 revoked function access before it created
`audit_tail_hash()`, which left that SECURITY DEFINER function callable at /rest/v1/rpc/. This migration
revokes again and stops future functions created by the migrating role from being granted to them.
Plain Postgres (no such roles) is untouched.
"""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

REVOKE_SQL = """
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
"""


def upgrade() -> None:
    op.execute(REVOKE_SQL)


def downgrade() -> None:
    # Deliberately a no-op: re-granting API roles access would only weaken the schema.
    pass
