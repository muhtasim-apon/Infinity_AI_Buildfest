"""Unified 7-class taxonomy and raw-folder-name mapping (spec 9.3).

Mapping is explicit and fails closed: an unknown folder name is reported, never guessed.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


class UnknownClassError(KeyError):
    """A raw class folder name has no mapping in labels.yaml."""


def normalise_name(raw: str) -> str:
    return _NON_ALNUM.sub("", raw.lower())


def load_labels(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8"))
    if "classes" not in data or "mapping" not in data:
        raise ValueError("labels.yaml needs 'classes' and 'mapping'")
    codes = {c["code"] for c in data["classes"]}
    for ds, mapping in data["mapping"].items():
        for raw, code in mapping.items():
            if code not in codes:
                raise ValueError(f"{ds}: '{raw}' maps to unknown class '{code}'")
    return data


class Taxonomy:
    def __init__(self, labels: dict[str, Any]) -> None:
        self.codes: list[str] = [c["code"] for c in labels["classes"]]
        self.notifiable = {c["code"]: bool(c["notifiable"]) for c in labels["classes"]}
        self._maps: dict[str, dict[str, str]] = {
            ds: {normalise_name(raw): code for raw, code in m.items()}
            for ds, m in labels["mapping"].items()
        }

    def map_label(self, dataset: str, raw: str) -> str:
        try:
            return self._maps[dataset][normalise_name(raw)]
        except KeyError as exc:
            raise UnknownClassError(f"{dataset}: no mapping for class folder {raw!r}") from exc

    def knows(self, dataset: str, raw: str) -> bool:
        return normalise_name(raw) in self._maps.get(dataset, {})
