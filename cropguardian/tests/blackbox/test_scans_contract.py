"""Blackbox: /v1/scans behaviour from the outside only (equivalence classes + boundaries).

Table: docs/testing/test-strategy.md §3. No knowledge of internals is used here.
"""

import pytest

pytestmark = pytest.mark.skip("stub — needs running API + test DB")


@pytest.mark.parametrize(
    "lat, lon, expected",
    [(23.85, 90.26, 201), (20.00, 88.00, 201), (27.00, 93.00, 201),   # inside + boundaries
     (19.99, 90.26, 422), (23.85, 93.01, 422), (23.851, 90.26, 422)],  # outside + too precise
)
def test_coarse_location_validation(lat, lon, expected): ...


@pytest.mark.parametrize("crop, expected", [("rice", 201), ("jute", 422), ("", 422)])
def test_crop_validation(crop, expected): ...


@pytest.mark.parametrize("sha, expected", [("a" * 64, 201), ("a" * 63, 422), ("g" * 64, 422)])
def test_sha256_validation(sha, expected): ...


def test_same_sha_twice_returns_same_scan_with_200(): ...


@pytest.mark.parametrize("limit, expected", [(1, 200), (50, 200), (0, 422), (51, 422), (-1, 422)])
def test_history_limit_boundaries(limit, expected): ...


@pytest.mark.parametrize(
    "auth, expected",
    [("valid_farmer", 201), ("missing", 401), ("expired", 401), ("wrong_audience", 401), ("tampered", 401)],
)
def test_auth_classes(auth, expected): ...


def test_farmer_cannot_call_admin_routes(): """GET /v1/admin/settings with farmer token → 403."""


def test_errors_are_problem_json(): """every 4xx has content-type application/problem+json and a 'code'."""
