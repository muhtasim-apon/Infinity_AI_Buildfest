"""Outbreak rule v1 (Gantt P3, Apon step 5). Pure logic: no DB, no clock (now is passed in).

N diagnosed scans of the same disease in the same division inside a rolling window => one DRAFT
alert. A draft is only a suggestion: a reviewer must approve it before any farmer sees it, and the
farmer-facing text always says "possible outbreak, unverified".
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta

MIN_CASES = 3
WINDOW = timedelta(days=7)
DIVISIONS = {
    "BD-A": ("বরিশাল", "Barishal"),
    "BD-B": ("চট্টগ্রাম", "Chattogram"),
    "BD-C": ("ঢাকা", "Dhaka"),
    "BD-D": ("খুলনা", "Khulna"),
    "BD-E": ("রাজশাহী", "Rajshahi"),
    "BD-F": ("রংপুর", "Rangpur"),
    "BD-G": ("সিলেট", "Sylhet"),
    "BD-H": ("ময়মনসিংহ", "Mymensingh"),
}


@dataclass(frozen=True)
class Case:
    disease: str
    region_code: str
    at: datetime


@dataclass(frozen=True)
class Cluster:
    disease: str
    region_code: str
    count: int
    first: datetime
    last: datetime


def clusters(
    cases: Iterable[Case],
    now: datetime,
    *,
    min_cases: int = MIN_CASES,
    window: timedelta = WINDOW,
) -> list[Cluster]:
    """Group in-window cases by (disease, division); return groups with >= min_cases.

    Window edges: a case exactly `window` old is INCLUDED; a case in the future is ignored
    (clock skew must never manufacture an outbreak)."""
    if min_cases < 1:
        raise ValueError("min_cases must be >= 1")
    start = now - window
    groups: dict[tuple[str, str], list[datetime]] = {}
    for case in cases:
        if case.region_code not in DIVISIONS or not case.disease:
            continue
        if case.at < start or case.at > now:
            continue
        groups.setdefault((case.disease, case.region_code), []).append(case.at)
    out = [
        Cluster(disease=d, region_code=r, count=len(ts), first=min(ts), last=max(ts))
        for (d, r), ts in groups.items()
        if len(ts) >= min_cases
    ]
    out.sort(key=lambda c: (-c.count, c.disease, c.region_code))
    return out
