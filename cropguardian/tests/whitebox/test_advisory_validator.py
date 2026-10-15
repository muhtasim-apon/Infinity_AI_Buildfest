"""Whitebox: app/rag/validator.py — rules V1–V6, 100 % branch coverage (ADR 0006)."""

import pytest

pytestmark = pytest.mark.skip("stub — implement with app.rag.validator")


@pytest.mark.parametrize(
    "case, expected_failed",
    [
        ("valid_cultural_only", ()),
        ("valid_with_chemical_dose_verbatim", ()),
        ("invalid_json", ("V1",)),
        ("no_citations", ("V2",)),
        ("citation_not_in_retrieved_set", ("V3",)),
        ("dose_not_in_any_cited_chunk", ("V4",)),
        ("dose_matches_after_nfc_and_whitespace_normalisation", ()),
        ("banned_ingredient_english_name", ("V5",)),
        ("banned_ingredient_bangla_name", ("V5",)),
        ("banned_ingredient_mixed_case", ("V5",)),
        ("chemical_without_safety_line", ("V6",)),
        ("multiple_failures_reported_together", ("V2", "V5")),
    ],
)
def test_validator_rules(case, expected_failed):
    """Load fixture tests/fixtures/advisory/<case>.json + its retrieved chunks; assert result.failed."""
