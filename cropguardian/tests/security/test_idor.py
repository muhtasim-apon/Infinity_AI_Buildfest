"""Security: T9 IDOR on every {id} route (A01) — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_get_other_users_scan_404():
    """farmer B GET /v1/scans/{A's id} → 404 (not 403, to avoid id probing)."""

def test_analyze_other_users_scan_404():
    """POST /v1/scans/{A's id}/analyze as B → 404."""

def test_review_requires_agronomist():
    """farmer POST /v1/review/{id} → 403."""
