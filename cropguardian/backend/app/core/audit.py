"""Audit hash chain (spec 7.6, 16.x). Pure functions; the database enforces append-only.

The database trigger (`audit_log_chain`) computes, per row,
    canonical = jsonb_build_object(<event fields>)::text
    row_hash  = sha256(prev_hash || '|' || canonical)   (hex)
and stores `canonical`, `prev_hash` and `row_hash`. This module re-verifies an exported chain, so
any edit or deletion of a past row is detected from the exported rows alone.
"""

from __future__ import annotations

import hashlib
import hmac
from collections.abc import Iterable, Mapping
from typing import Any

GENESIS_HASH = "0" * 64


def compute_row_hash(prev_hash: str, canonical: str) -> str:
    return hashlib.sha256(f"{prev_hash}|{canonical}".encode()).hexdigest()


def verify_chain(rows: Iterable[Mapping[str, Any]]) -> tuple[bool, int | None]:
    """Rows in id order, each {"canonical": str, "prev_hash": str, "row_hash": str}.

    Returns (ok, index_of_first_bad_row). Constant-time comparison for hashes.
    """
    prev = GENESIS_HASH
    for i, row in enumerate(rows):
        if not hmac.compare_digest(str(row["prev_hash"]), prev):
            return False, i
        expected = compute_row_hash(prev, str(row["canonical"]))
        if not hmac.compare_digest(str(row["row_hash"]), expected):
            return False, i
        prev = expected
    return True, None
