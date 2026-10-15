"""Security: T19 XSS via LLM/KB text (A03) — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_api_returns_text_not_html():
    """advisory fields are plain strings; '<script>' in KB chunk returned escaped in JSON."""

def test_csp_header_present_on_static_site():
    """Content-Security-Policy header on / and /admin (staging)."""
