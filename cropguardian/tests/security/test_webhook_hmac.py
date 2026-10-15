"""Security: T2 forged n8n webhook — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_unsigned_webhook_401():
    """POST /v1/hooks/n8n/heartbeat without signature → 401, no side effect."""

def test_replayed_webhook_401():
    """valid request replayed → second 401."""
