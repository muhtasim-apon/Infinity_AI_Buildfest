"""Security: T18 excessive agency (LLM06) — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_agent_has_no_send_tool():
    """tool registry contains only read tools + create_alert_draft."""

def test_alert_draft_requires_approval():
    """agent-created alert has status draft; n8n not called."""

def test_tool_call_cap():
    """fake LLM requests 5 tool calls → loop stops at 4, fallback returned."""
