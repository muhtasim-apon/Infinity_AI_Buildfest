"""Timeout behaviour — docs/testing/test-strategy.md §4. Slow dependencies simulated with respx
(HTTP) and a fake ONNX session that sleeps; network faults with Toxiproxy in integration runs."""

import pytest

pytestmark = pytest.mark.skip("stub — needs app + fakes")


def test_inference_over_budget_returns_503_with_retry_after():
    """fake session sleeps 5 s, budget 4 s → 503 problem+json, Retry-After set, scan stays 'uploaded'."""


def test_llm_slow_returns_diagnosis_with_fallback_advice():
    """respx delays LLM 25 s, budget 20 s → 200, advisory.status 'fallback', no 5xx."""


@pytest.mark.parametrize("llm_status", [429, 500, 503])
def test_llm_errors_fall_back(llm_status):
    """→ 200 with fallback advice; error logged; no PII in log."""


def test_healthz_fast_even_when_db_slow():
    """Toxiproxy adds 3 s to Postgres → /healthz < 200 ms; /readyz reports degraded."""


def test_signed_url_expiry_handled():
    """upload after 5 min → Storage 403 → client contract: request new URL (covered in e2e)."""


def test_open_meteo_timeout_does_not_block_analyze():
    """weather call times out at 3 s → analyze still succeeds; outbreak risk not raised."""
