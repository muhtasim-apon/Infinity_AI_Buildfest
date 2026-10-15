"""Security: T10 location leak through EXIF — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_stored_object_has_no_exif():
    """upload fixture with GPS EXIF via full flow → object in Storage has no EXIF."""
