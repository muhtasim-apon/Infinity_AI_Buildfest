"""Outbreak rules v1 (model card: docs/ai/model-cards/outbreak-risk.md).

Counts non-abstained diagnoses (or agronomist-confirmed) of a notifiable disease within
``OUTBREAK_RADIUS_KM`` (haversine on coarse points) and ``OUTBREAK_WINDOW_DAYS``. At
``OUTBREAK_MIN_REPORTS`` creates/updates ONE draft alert per (disease, area) — never sends.
Weather (Open-Meteo, cached 1 h, 3 s timeout; failure → weather unknown → risk not raised).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID


@dataclass(frozen=True)
class OutbreakResult:
    alert_id: UUID | None
    report_count: int
    risk: Literal["low", "medium", "high"] | None


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    raise NotImplementedError


def risk_level(report_count: int, weather_favourable: bool | None) -> Literal["low", "medium", "high"]:
    """high if count ≥ 2×min and weather favourable; medium if favourable; else low.
    Unknown weather (None) never raises risk above low."""
    raise NotImplementedError


async def check(disease_code: str, lat: float | None, lon: float | None) -> OutbreakResult:
    raise NotImplementedError
