"""Unit: Pydantic schemas in app/schemas — these can run as soon as dependencies are installed."""

import pytest

pytestmark = pytest.mark.skip("stub — enable after `pip install -r services/api/requirements.txt`")


def test_scan_create_rejects_precise_coordinates():
    """ScanCreateIn(lat_coarse=23.851) → ValidationError (multiple_of 0.01)."""


def test_review_correct_requires_code():
    """ReviewIn(verdict='correct') without corrected_code → ValidationError."""


def test_settings_reason_required():
    """SettingsIn without reason → ValidationError."""


def test_alert_message_length_bounds():
    """message_bn 9 chars → error; 10 → ok; 480 → ok; 481 → error."""
