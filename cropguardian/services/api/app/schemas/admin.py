"""Admin settings schemas. Every change carries a reason for the audit chain."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SettingsOut(BaseModel):
    confidence_threshold: float
    outbreak_radius_km: float
    outbreak_min_reports: int
    outbreak_window_days: int


class SettingsIn(SettingsOut):
    confidence_threshold: float = Field(gt=0, lt=1)
    outbreak_radius_km: float = Field(gt=0, le=50)
    outbreak_min_reports: int = Field(ge=2, le=50)
    outbreak_window_days: int = Field(ge=1, le=30)
    reason: str = Field(min_length=5, max_length=500)
