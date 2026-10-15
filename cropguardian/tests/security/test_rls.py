"""Security: T7, T9 RLS with the anon key (A01) — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_anon_cannot_read_other_scans():
    """supabase-js as farmer A selects scans of farmer B → 0 rows."""

def test_role_self_escalation_blocked():
    """farmer updates own profile role → admin: rejected by WITH CHECK."""

def test_agronomist_sees_only_own_upazila():
    """agronomist in Savar cannot read Sylhet review cases."""

def test_every_table_has_rls():
    """pg_class.relrowsecurity true for every table in public schema."""

def test_audit_log_not_updatable():
    """UPDATE/DELETE on audit_log as authenticated → permission denied."""
