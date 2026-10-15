"""Scan orchestration for ``POST /v1/scans/{id}/analyze``.

    load scan (owner check) → status must be 'uploaded' (else 409)
    → download from Storage → security.upload.sanitise
    → ml.preprocess.to_tensor → ml.inference.predict_logits (timeout)
    → ml.decision.decide
    → if not abstained: services.advisory.advise
    → one DB transaction: diagnoses + advisories + citations + scans.status + audit_append
    → services.outbreak.check (after commit; failure here never fails the request)

Idempotent: if a diagnosis already exists for the scan, return it unchanged.
"""

from __future__ import annotations

from uuid import UUID

from app.schemas.scan import AnalyzeOut


async def analyze(scan_id: UUID, user_id: UUID) -> AnalyzeOut:
    raise NotImplementedError
