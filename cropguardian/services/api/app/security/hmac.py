"""HMAC verification for n8n webhooks (threat T2).

Signature: ``X-CG-Signature: sha256=hex(HMAC_SHA256(secret, f"{timestamp}.{raw_body}"))``,
``X-CG-Timestamp`` unix seconds. Reject if |now − ts| > 300 s, if the signature mismatches
(compare with ``hmac.compare_digest``), or if ``(ts, signature)`` was seen in the last 5 min (replay).
"""

from __future__ import annotations

REPLAY_WINDOW_S = 300


def verify(secret: bytes, timestamp: str, signature: str, raw_body: bytes, now: float) -> bool:
    """Pure function for whitebox testing; the router supplies ``now`` and the nonce cache."""
    raise NotImplementedError
