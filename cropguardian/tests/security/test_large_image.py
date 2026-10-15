"""Security: T15 memory exhaustion — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_pixel_bomb_rejected_without_oom():
    """50k×50k PNG header → 422 quickly; process RSS growth < 50 MB."""
