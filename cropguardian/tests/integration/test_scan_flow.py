"""Integration: full scan flow against real Postgres+pgvector (testcontainers) and a local Storage
emulator, with fake LLM and a tiny test ONNX model."""

import pytest

pytestmark = pytest.mark.skip("stub — needs integration environment")


def test_happy_path_persists_everything():
    """create → upload → analyze → rows in scans, diagnoses, advisories, citations, audit_log; status diagnosed."""


def test_abstain_path_enqueues_review():
    """non-leaf fixture → needs_review; appears in agronomist queue for that upazila."""


def test_stateless_restart_between_upload_and_analyze():
    """(Render A3/A6) recreate the app between upload and analyze → analyze still succeeds."""


def test_outbreak_draft_after_three_reports():
    """3 blast diagnoses within 5 km/7 days → one draft alert."""


def test_review_creates_feedback_label_only_with_consent():
    """consent training_use false → no feedback_labels row."""
