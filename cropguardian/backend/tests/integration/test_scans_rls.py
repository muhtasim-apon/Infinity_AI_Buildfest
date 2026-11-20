"""Real-Postgres tests for migration 0004 (scans + outbreak_alerts RLS)."""

import os
import uuid

import psycopg
import pytest

from tests.integration.test_identity_rls import ctx, make_user, system

OWNER = os.environ.get("TEST_SUPER_DATABASE_URL")
API = os.environ.get("TEST_API_DATABASE_URL")
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not (OWNER and API), reason="database URLs not set"),
]
SHA = "a" * 64


@pytest.fixture
def api():
    with psycopg.connect(API, autocommit=False) as conn:
        yield conn
        conn.rollback()


def add_scan(cur, uid, tenant="real", disease="tungro", region="BD-C"):
    cur.execute(
        "INSERT INTO scans (tenant_id, user_id, idempotency_key, image_sha256, region_code, status,"
        " disease) VALUES (%s,%s,%s,%s,%s,'diagnosed',%s) RETURNING id",
        (tenant, uid, uuid.uuid4().hex, SHA, region, disease),
    )
    return cur.fetchone()[0]


def test_new_tables_force_rls_and_api_roles_have_no_grants():
    with psycopg.connect(OWNER) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT relname, relrowsecurity, relforcerowsecurity FROM pg_class "
            "WHERE relname IN ('scans','outbreak_alerts') ORDER BY relname"
        )
        assert cur.fetchall() == [("outbreak_alerts", True, True), ("scans", True, True)]


def test_farmer_sees_only_own_scans(api):
    with api.cursor() as cur:
        system(cur)
        a = make_user(cur)
        b = make_user(cur)
        add_scan(cur, a)
        add_scan(cur, b)
        ctx(cur, uid=a, role="farmer", tenant="real")
        cur.execute("SELECT user_id::text FROM scans")
        assert {r[0] for r in cur.fetchall()} == {a}


def test_farmer_cannot_insert_for_someone_else_or_other_tenant(api):
    with api.cursor() as cur:
        system(cur)
        a = make_user(cur)
        b = make_user(cur)
        ctx(cur, uid=a, role="farmer", tenant="real")
        cur.execute("SAVEPOINT s")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            add_scan(cur, b)
        cur.execute("ROLLBACK TO SAVEPOINT s")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            add_scan(cur, a, tenant="demo")


def test_farmer_cannot_update_or_delete_scans(api):
    with api.cursor() as cur:
        system(cur)
        a = make_user(cur)
        sid = add_scan(cur, a)
        ctx(cur, uid=a, role="farmer", tenant="real")
        cur.execute("UPDATE scans SET status='healthy' WHERE id=%s", (sid,))
        assert cur.rowcount == 0
        cur.execute("DELETE FROM scans WHERE id=%s", (sid,))
        assert cur.rowcount == 0


def test_bad_values_rejected_by_checks(api):
    with api.cursor() as cur:
        system(cur)
        a = make_user(cur)
        with pytest.raises(psycopg.errors.CheckViolation):
            add_scan(cur, a, region="23.81,90.41")  # exact coordinates can never be stored


def alert(cur, tenant="real", status="draft"):
    cur.execute(
        "INSERT INTO outbreak_alerts (tenant_id, disease, region_code, case_count, window_start,"
        " window_end, status, decided_at) VALUES (%s,'tungro','BD-C',3,now(),now(),%s,"
        " CASE WHEN %s='draft' THEN NULL ELSE now() END) RETURNING id",
        (tenant, status, status),
    )
    return cur.fetchone()[0]


def test_farmers_see_only_approved_alerts_staff_see_drafts(api):
    with api.cursor() as cur:
        system(cur)
        alert(cur, status="draft")
        approved = alert(cur, status="approved")
        a = make_user(cur)
        ctx(cur, uid=a, role="farmer", tenant="real")
        cur.execute("SELECT id FROM outbreak_alerts")
        assert [r[0] for r in cur.fetchall()] == [approved]
        ctx(cur, uid=str(uuid.uuid4()), role="reviewer", tenant="real")
        cur.execute("SELECT count(*) FROM outbreak_alerts")
        assert cur.fetchone()[0] == 2


def test_only_staff_can_decide_and_only_in_their_tenant(api):
    with api.cursor() as cur:
        system(cur)
        real = alert(cur)
        a = make_user(cur)
        ctx(cur, uid=a, role="farmer", tenant="real")
        cur.execute(
            "UPDATE outbreak_alerts SET status='approved', decided_at=now() WHERE id=%s", (real,)
        )
        assert cur.rowcount == 0
        ctx(cur, uid=str(uuid.uuid4()), role="reviewer", tenant="demo")
        cur.execute(
            "UPDATE outbreak_alerts SET status='approved', decided_at=now() WHERE id=%s", (real,)
        )
        assert cur.rowcount == 0
        ctx(cur, uid=str(uuid.uuid4()), role="reviewer", tenant="real")
        cur.execute(
            "UPDATE outbreak_alerts SET status='approved', decided_at=now() WHERE id=%s", (real,)
        )
        assert cur.rowcount == 1


def test_one_open_draft_per_disease_and_division(api):
    with api.cursor() as cur:
        system(cur)
        alert(cur)
        with pytest.raises(psycopg.errors.UniqueViolation):
            alert(cur)


def test_staff_cannot_create_alerts_directly(api):
    with api.cursor() as cur:
        ctx(cur, uid=str(uuid.uuid4()), role="reviewer", tenant="real")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            alert(cur)
