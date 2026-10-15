"""One-click demo access — ``/demo-user`` and ``/demo-admin`` in the web app call this.

Issues a short-lived (30 min) JWT for a seeded **synthetic** account. Demo sessions are
sandboxed: writes are allowed only into demo-owned rows, which n8n resets nightly (threat T3).
Rate limit: 10/min/IP.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1/demo", tags=["demo"])


class DemoSessionIn(BaseModel):
    role: Literal["user", "admin"]


class DemoSessionOut(BaseModel):
    access_token: str
    expires_in: int
    role: str


@router.post("/session", response_model=DemoSessionOut)
async def create_demo_session(body: DemoSessionIn) -> DemoSessionOut:
    raise NotImplementedError
