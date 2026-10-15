"""Security: T1 spoofed/forged JWT (A07) — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_missing_token_401():
    """no Authorization header → 401 problem+json."""

def test_expired_token_401():
    """exp in the past (1 s) → 401."""

def test_wrong_audience_401():
    """aud != authenticated → 401."""

def test_alg_none_rejected():
    """header alg=none → 401."""

def test_role_taken_from_db_not_claims():
    """token claims role=admin, profiles.role=farmer → farmer permissions."""
