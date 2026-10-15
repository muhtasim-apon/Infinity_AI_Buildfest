"""Agronomist review schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class ReviewIn(BaseModel):
    verdict: Literal["confirm", "correct", "unclear"]
    corrected_code: str | None = None
    note: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def correct_needs_code(self) -> "ReviewIn":
        if self.verdict == "correct" and not self.corrected_code:
            raise ValueError("corrected_code is required when verdict is 'correct'")
        return self


class ReviewItem(BaseModel):
    scan_id: UUID
    image_url: str          # short-lived signed URL
    top3: list[dict[str, object]]
    crop: str
    variety: str | None
    created_at: datetime


class ReviewQueue(BaseModel):
    items: list[ReviewItem]
