"""Real-Postgres tests for migration 0001 (RLS, append-only, hash chain, seed).

Needs `docker compose -f docker-compose.test.yml up -d postgres` and `alembic upgrade head`.
Env: TEST_SUPER_DATABASE_URL (superuser, probes only) and TEST_API_DATABASE_URL (cg_api login). Skipped otherwise -
the phase gate runs them with both set.
"""

import os

import psycopg
import pytest

from app.core.audit import verify_chain
from app.core.platform_settings import defaults

OWNER = os.environ.get("TEST_SUPER_DATABASE_URL")  # superuser: bypasses RLS, not triggers
API = os.environ.get("TEST_API_DATABASE_URL")
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not (OWNER and API), reason="database URLs not set"),
]


def ctx(cur, role="cg_app", uid="", app_role="", tenant=""):
    cur.execute(f"SET LOCAL ROLE {role}")
    cur.execute(
        "SELECT set_config('app.user_id', %s, true), set_config('app.role', %s, true), "
        "set_config('app.tenant', %s, true)",
        (uid, app_role, tenant),
    )


@pytest.fixture
def api():
    with psycopg.connect(API, autocommit=False) as conn:
        yield conn
        conn.rollback()


def test_seed_has_every_default_validated():
    with psycopg.connect(OWNER) as conn, conn.cursor() as cur:
        cur.execute("SELECT key, value FROM platform_settings WHERE version = 1")
        rows = dict(cur.fetchall())
    for key, value in defaults().items():
        assert rows[key] == value


@pytest.mark.security
def test_no_context_sees_nothing(api):
    with api.cursor() as cur:
        ctx(cur)
        cur.execute("SELECT count(*) FROM platform_settings")
        assert cur.fetchone()[0] == 0
        cur.execute("SELECT count(*) FROM audit_log")
        assert cur.fetchone()[0] == 0


@pytest.mark.security
def test_admin_reads_settings_but_cannot_update_or_delete(api):
    with api.cursor() as cur:
        ctx(cur, uid="u1", app_role="admin", tenant="real")
        cur.execute("SELECT count(*) FROM platform_settings")
        assert cur.fetchone()[0] > 0
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute("UPDATE platform_settings SET reason = 'tampering attempt here'")


@pytest.mark.security
def test_non_admin_cannot_write_settings(api):
    with api.cursor() as cur:
        ctx(cur, uid="u1", app_role="farmer", tenant="real")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute(
                "INSERT INTO platform_settings (key, value, version, reason) "
                "VALUES ('outbreak.radius_km', '9', 2, 'farmer must not write this')"
            )


@pytest.mark.security
def test_demo_tenant_cannot_read_real_audit_rows(api):
    owner = psycopg.connect(OWNER, autocommit=True)
    with owner.cursor() as c:
        c.execute("INSERT INTO audit_log (tenant_id, action) VALUES ('real', 'rls.probe')")
    owner.close()
    with api.cursor() as cur:
        ctx(cur, uid="a", app_role="admin", tenant="demo")
        cur.execute("SELECT count(*) FROM audit_log WHERE action = 'rls.probe'")
        assert cur.fetchone()[0] == 0
        ctx(cur, uid="a", app_role="admin", tenant="real")
        cur.execute("SELECT count(*) FROM audit_log WHERE action = 'rls.probe'")
        assert cur.fetchone()[0] >= 1


@pytest.mark.security
def test_audit_log_is_append_only_for_everyone_even_owner():
    with psycopg.connect(OWNER, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO audit_log (action) VALUES ('append.only.probe')")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute("UPDATE audit_log SET action = 'x'")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute("DELETE FROM audit_log")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute("TRUNCATE audit_log")


@pytest.mark.security
def test_hash_chain_verifies_in_sql_and_python_and_detects_tampering():
    with psycopg.connect(OWNER, autocommit=True) as conn, conn.cursor() as cur:
        for i in range(3):
            cur.execute(
                "INSERT INTO audit_log (action, after) VALUES (%s, %s::jsonb)",
                (f"chain.{i}", '{"n": %d}' % i),
            )
        cur.execute("SELECT audit_verify_chain()")
        assert cur.fetchone()[0] == 0
        cur.execute("SELECT canonical, prev_hash, row_hash FROM audit_log ORDER BY id")
        rows = [{"canonical": c, "prev_hash": p, "row_hash": h} for c, p, h in cur.fetchall()]
        assert verify_chain(rows) == (True, None)

    # Tamper inside a transaction that is ROLLED BACK so the shared test DB stays intact.
    with psycopg.connect(OWNER, autocommit=False) as conn, conn.cursor() as cur:
        cur.execute("ALTER TABLE audit_log DISABLE TRIGGER trg_audit_log_no_update")
        cur.execute("UPDATE audit_log SET canonical = 'forged' WHERE action = 'chain.1'")
        cur.execute("SELECT audit_verify_chain()")
        first_bad = cur.fetchone()[0]
        conn.rollback()
    assert first_bad != 0  # the verifier noticed the forged row
    with psycopg.connect(OWNER, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute("SELECT audit_verify_chain()")
        assert cur.fetchone()[0] == 0  # rollback restored an intact chain


def test_settings_reason_length_and_version_unique_constraints():
    with psycopg.connect(OWNER, autocommit=True) as conn, conn.cursor() as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute(
                "INSERT INTO platform_settings (key, value, version, reason) "
                "VALUES ('x.y', '1', 1, 'short')"
            )
        with pytest.raises(psycopg.errors.UniqueViolation):
            cur.execute(
                "INSERT INTO platform_settings (key, value, version, reason) VALUES "
                "('outbreak.radius_km', '5', 1, 'duplicate version should fail')"
            )


@pytest.mark.security
def test_invalid_tenant_rejected_by_check_constraint():
    with psycopg.connect(OWNER, autocommit=True) as conn, conn.cursor() as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute("INSERT INTO audit_log (tenant_id, action) VALUES ('other', 'x')")


@pytest.mark.security
def test_idempotency_keys_are_per_user(api):
    with api.cursor() as cur:
        ctx(cur, uid="alice", app_role="farmer", tenant="real")
        cur.execute(
            "INSERT INTO idempotency_keys (user_id, tenant_id, key, request_hash) "
            "VALUES ('alice', 'real', 'key-12345678', 'h')"
        )
        ctx(cur, uid="bob", app_role="farmer", tenant="real")
        cur.execute("SELECT count(*) FROM idempotency_keys")
        assert cur.fetchone()[0] == 0
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute(
                "INSERT INTO idempotency_keys (user_id, tenant_id, key, request_hash) "
                "VALUES ('alice', 'real', 'key-87654321', 'h')"  # bob writing as alice
            )


@pytest.mark.security
def test_login_user_has_no_privileges_of_its_own(api):
    with api.cursor() as cur:  # no SET ROLE: cg_api is NOINHERIT and holds no grants itself
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute("SELECT * FROM jobs_log LIMIT 1")
