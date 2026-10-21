"""Platform settings: defaults and bounds (spec 6.2). Pure validation, no database access.

Bounds are enforced here and by the migration seed; rule: min_reports <= high_reports.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class SettingsValidationError(ValueError):
    """A platform setting is unknown, out of bounds, or inconsistent."""


@dataclass(frozen=True)
class Spec:
    default: Any
    low: float | None = None
    high: float | None = None


SPECS: dict[str, Spec] = {
    "abstain.tau": Spec(None, 0.50, 0.99),  # from active model version
    "abstain.energy_threshold": Spec(None),
    "leaf_gate.threshold": Spec(None, 0.30, 0.95),
    "quality.min_side_px": Spec(224, 128, 512),
    "quality.blur_min_var": Spec(60, 10, 300),
    "quality.brightness_range": Spec([40, 220]),
    "outbreak.radius_km": Spec(5, 1, 25),
    "outbreak.window_days": Spec(7, 3, 21),
    "outbreak.min_reports": Spec(3, 2, 20),
    "outbreak.high_reports": Spec(6, 3, 50),
    "map.k_anonymity": Spec(3, 2, 10),
    "advice.max_followups_per_scan": Spec(1, 0, 3),
    "advice.rag_min_score": Spec(0.45, 0.2, 0.9),
    "advice.cache_ttl_days": Spec(30, 1, 180),
    "retention.original_days": Spec(90, 30, 365),
    "demo.session_minutes": Spec(60, 15, 180),
}


def defaults() -> dict[str, Any]:
    return {k: s.default for k, s in SPECS.items() if s.default is not None}


def validate_value(key: str, value: Any) -> Any:
    spec = SPECS.get(key)
    if spec is None:
        raise SettingsValidationError(f"unknown setting: {key}")
    if key == "quality.brightness_range":
        if (
            not isinstance(value, list | tuple)
            or len(value) != 2
            or not all(isinstance(v, int | float) and not isinstance(v, bool) for v in value)
            or not (0 <= value[0] < value[1] <= 255)
        ):
            raise SettingsValidationError("quality.brightness_range must be [lo, hi] within 0..255")
        return [value[0], value[1]]
    if spec.low is None:
        return value
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise SettingsValidationError(f"{key} must be a number")
    if not (spec.low <= value <= spec.high):
        raise SettingsValidationError(f"{key} must be within [{spec.low}, {spec.high}]")
    return value


def validate_all(values: dict[str, Any]) -> dict[str, Any]:
    cleaned = {k: validate_value(k, v) for k, v in values.items()}
    merged = {**defaults(), **cleaned}
    if merged["outbreak.min_reports"] > merged["outbreak.high_reports"]:
        raise SettingsValidationError("outbreak.min_reports must be <= outbreak.high_reports")
    return cleaned
