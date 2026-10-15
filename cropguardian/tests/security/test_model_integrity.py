"""Security: T6 model file swapped (A08) — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_hash_mismatch_not_ready():
    """ONNX bytes differ from model_versions.onnx_sha256 → /readyz 503, analyze 503."""
