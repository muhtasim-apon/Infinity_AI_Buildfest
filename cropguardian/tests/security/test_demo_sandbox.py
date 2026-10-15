"""Security: T3 demo account abuse — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_demo_cannot_read_real_users():
    """demo token → only demo-owned rows visible."""

def test_demo_rate_limited():
    """11th demo session in a minute from one IP → 429."""

def test_demo_cannot_change_settings():
    """demo → PUT /v1/admin/settings → 403."""
