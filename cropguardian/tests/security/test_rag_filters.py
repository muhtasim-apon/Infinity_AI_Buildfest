"""Security: LLM08 vector store weaknesses — see docs/security/threat-model.md and owasp-mapping.md."""

import pytest

pytestmark = pytest.mark.skip("stub")


def test_retired_documents_never_retrieved():
    """retire doc → its chunks absent from retrieve()."""

def test_metadata_filter_by_disease():
    """query for blast never returns tungro-only chunks above rank k."""
