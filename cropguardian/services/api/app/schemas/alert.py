"""Alert schemas. No personal data — disease, area and risk only (data-sovereignty principle 4)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AlertOut(BaseModel):
    id: UUID
    disease_code: str
    disease_name_bn: str
    center_lat: float
    center_lon: float
    radius_km: float
    report_count: int
    risk: Literal["low", "medium", "high"]
    rule_version: str
    status: Literal["draft", "approved", "sent", "dismissed"]
    message_bn: str | None
    created_at: datetime


class AlertList(BaseModel):
    items: list[AlertOut]


class AlertApproveIn(BaseModel):
    message_bn: str = Field(min_length=10, max_length=480)
