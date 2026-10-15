"""Whitebox: app/security/hmac.py (threat T2)."""

import pytest

pytestmark = pytest.mark.skip("stub — implement with app.security.hmac")


def test_valid_signature_accepted(): """correct HMAC over '{ts}.{body}', ts = now → True."""
def test_wrong_signature_rejected(): """one hex char changed → False."""
def test_stale_timestamp_rejected(): """ts = now − 301 s → False; now − 300 s → True (boundary)."""
def test_future_timestamp_rejected(): """ts = now + 301 s → False."""
def test_replay_rejected(): """same (ts, signature) twice within window → second False (router nonce cache)."""
def test_constant_time_compare_used(): """monkeypatch hmac.compare_digest is called."""
