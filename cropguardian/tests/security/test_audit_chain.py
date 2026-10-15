"""Security: T8 repudiation — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_chain_verifies():
    """after N appends verify_chain() → (True, None)."""

def test_tampered_row_detected():
    """manually alter detail of row k (superuser) → (False, k)."""
