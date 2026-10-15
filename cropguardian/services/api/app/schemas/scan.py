"""Scan, diagnosis and advisory schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ScanCreateIn(BaseModel):
    crop: Literal["rice"]
    field_id: UUID | None = None
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    # coarse only (2 decimals ≈ 1 km), Bangladesh bounding box — exact GPS is never accepted
    lat_coarse: float | None = Field(default=None, ge=20.0, le=27.0, multiple_of=0.01)
    lon_coarse: float | None = Field(default=None, ge=88.0, le=93.0, multiple_of=0.01)
    captured_at: datetime | None = None
    client_quality_flag: Literal["dark", "blurry"] | None = None


class ScanCreateOut(BaseModel):
    scan_id: UUID
    upload_url: str
    upload_expires_at: datetime


class Prediction(BaseModel):
    code: str
    name_bn: str
    name_en: str
    prob: float = Field(ge=0, le=1)


class DiagnosisOut(BaseModel):
    model_version: str
    top3: list[Prediction]
    abstained: bool
    confidence_band: Literal["high", "medium", "low"]


class CitationOut(BaseModel):
    title: str
    publisher: str
    page: int | None
    url: str


class ChemicalOut(BaseModel):
    active_ingredient: str
    dose: str            # verbatim from the cited source (ADR 0006)
    interval: str | None
    phi_days: int | None  # pre-harvest interval


class AdvisoryOut(BaseModel):
    status: Literal["ok", "fallback", "blocked"]
    summary_bn: str
    steps_bn: list[str]
    chemical: ChemicalOut | None
    safety_bn: str
    citations: list[CitationOut]


class AnalyzeOut(BaseModel):
    scan_id: UUID
    status: Literal["diagnosed", "needs_review"]
    diagnosis: DiagnosisOut
    advisory: AdvisoryOut | None


class ScanSummary(BaseModel):
    scan_id: UUID
    created_at: datetime
    status: str
    top1_name_bn: str | None


class ScanPage(BaseModel):
    items: list[ScanSummary]
    next_cursor: str | None
