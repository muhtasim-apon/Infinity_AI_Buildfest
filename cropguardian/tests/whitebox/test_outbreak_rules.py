"""Whitebox: app/services/outbreak.py — rules v1 branches."""

import pytest

pytestmark = pytest.mark.skip("stub — implement with app.services.outbreak")


def test_below_min_reports_creates_no_alert(): """2 reports, min 3 → alert_id None."""
def test_at_min_reports_creates_draft(): """3 reports → one draft alert."""
def test_existing_draft_is_updated_not_duplicated(): """4th report in same area → same alert id, count 4."""
def test_abstained_diagnoses_are_excluded(): """abstained rows never counted."""
def test_point_on_radius_edge(): """haversine distance == radius → included (inclusive)."""
def test_outside_window_excluded(): """report 8 days old with window 7 → excluded."""
def test_risk_high_requires_double_min_and_favourable_weather(): """count 6, favourable → high."""
def test_unknown_weather_never_raises_risk(): """weather None → low."""
def test_non_notifiable_disease_ignored(): """brown_spot → no alert."""
def test_haversine_known_distance(): """Dhaka–Savar coarse points → within 0.5 km of reference value."""
