"""Concurrency — docs/testing/test-strategy.md §5. Uses asyncio.gather against the ASGI app with a
real Postgres (integration DB)."""

import pytest

pytestmark = pytest.mark.skip("stub — needs integration DB")


def test_duplicate_upload_race_creates_one_scan():
    """20 parallel POST /v1/scans with the same sha256 → 1 row; all responses carry the same scan_id."""


def test_idempotency_key_replay_single_side_effect():
    """10 parallel analyze calls with same Idempotency-Key → one diagnosis row, one audit row."""


def test_inference_semaphore_caps_parallelism():
    """50 parallel analyze → fake session records max concurrent calls == 2; queue overflow → 429."""


def test_audit_chain_parallel_appends_stay_linear():
    """20 parallel audit_append → verify_chain() ok, ids contiguous, each prev_hash == previous row_hash."""


def test_two_agronomists_review_same_scan():
    """confirm vs correct concurrently → both expert_reviews stored; feedback label resolves to 'unclear'."""


def test_alert_approve_race_single_winner():
    """2 parallel approvals → exactly one 200 and one 409; n8n webhook called once."""
