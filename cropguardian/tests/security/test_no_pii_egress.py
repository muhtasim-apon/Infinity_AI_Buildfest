"""Security: T11 PII to LLM or logs (LLM02) — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_prompt_contains_no_pii():
    """capture LLM request body via respx → no phone pattern +8801…, no display_name, no lat/lon beyond 2 decimals."""

def test_logs_contain_no_pii():
    """run flow with caplog → no phone, email or coordinates in any record."""
