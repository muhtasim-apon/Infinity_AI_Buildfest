import pytest

from app.core.audit import GENESIS_HASH, compute_row_hash, verify_chain
from app.core.platform_settings import (
    SettingsValidationError,
    defaults,
    validate_all,
    validate_value,
)


def build_chain(canon: list[str]):
    prev = GENESIS_HASH
    rows = []
    for c in canon:
        h = compute_row_hash(prev, c)
        rows.append({"canonical": c, "prev_hash": prev, "row_hash": h})
        prev = h
    return rows


def test_valid_chain_verifies():
    assert verify_chain(build_chain(["a", "b", "c"])) == (True, None)


def test_empty_chain_is_valid():
    assert verify_chain([]) == (True, None)


@pytest.mark.security
def test_edited_row_detected():
    rows = build_chain(["a", "b", "c"])
    rows[1]["canonical"] = "tampered"
    assert verify_chain(rows) == (False, 1)


@pytest.mark.security
def test_deleted_row_detected():
    rows = build_chain(["a", "b", "c"])
    del rows[1]
    assert verify_chain(rows) == (False, 1)


@pytest.mark.security
def test_first_row_must_link_to_genesis():
    rows = build_chain(["a", "b"])
    rows[0]["prev_hash"] = "f" * 64
    assert verify_chain(rows)[0] is False


def test_defaults_are_valid_and_in_bounds():
    assert validate_all(defaults())


@pytest.mark.parametrize(
    ("key", "bad"),
    [
        ("outbreak.radius_km", 0),
        ("outbreak.radius_km", 26),
        ("outbreak.min_reports", 1),
        ("quality.min_side_px", 64),
        ("advice.rag_min_score", 0.95),
        ("map.k_anonymity", 1),
        ("retention.original_days", 10),
        ("demo.session_minutes", "60"),
        ("outbreak.radius_km", True),
        ("abstain.tau", 0.4),
        ("quality.brightness_range", [220, 40]),
        ("quality.brightness_range", [0]),
        ("quality.brightness_range", [0, 300]),
        ("no.such.key", 1),
    ],
)
def test_out_of_bounds_rejected(key, bad):
    with pytest.raises(SettingsValidationError):
        validate_value(key, bad)


def test_boundaries_inclusive():
    assert validate_value("outbreak.radius_km", 1) == 1
    assert validate_value("outbreak.radius_km", 25) == 25


def test_min_reports_must_not_exceed_high_reports():
    with pytest.raises(SettingsValidationError):
        validate_all({"outbreak.min_reports": 10, "outbreak.high_reports": 5})
    assert validate_all({"outbreak.min_reports": 5, "outbreak.high_reports": 5})
