"""`cg_ml data prepare` (spec 9.4 steps 2, 3, 5-partial, 6).

Day-1 scope (17 Oct): extract -> integrity -> normalise (EXIF transpose, RGB, strip metadata) ->
taxonomy mapping -> per-image statistics. pHash grouping and `split_v1.csv` follow on 18 Oct.
Nothing here writes to the raw archives; processed images go to the gitignored `ml/data/`.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from cg_ml.data.integrity import IMAGE_SUFFIXES, check_image, image_stats, normalise_image
from cg_ml.data.taxonomy import Taxonomy

FILE_FIELDS = [
    "dataset", "source_rel_path", "class_raw", "class_code", "status",
    "width", "height", "brightness_mean", "laplacian_var", "processed_rel_path",
]  # fmt: skip


@dataclass
class FileRecord:
    dataset: str
    source_rel_path: str
    class_raw: str
    class_code: str
    status: str  # ok | corrupt | too_small | unknown_class
    width: int = 0
    height: int = 0
    brightness_mean: float = 0.0
    laplacian_var: float = 0.0
    processed_rel_path: str = ""


def raw_class_of(rel: Path, dataset: str, taxonomy: Taxonomy) -> str | None:
    """Nearest ancestor folder (deepest first) whose name maps in the taxonomy; else None."""
    for part in reversed(rel.parts[:-1]):
        if taxonomy.knows(dataset, part):
            return part
    return None


def prepare_dataset(
    dataset: str,
    extracted_root: Path,
    processed_root: Path,
    taxonomy: Taxonomy,
    *,
    min_side: int = 128,
    limit: int | None = None,
) -> list[FileRecord]:
    records: list[FileRecord] = []
    files = sorted(
        p for p in extracted_root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )
    if limit is not None:
        files = files[:limit]
    for path in files:
        rel = path.relative_to(extracted_root)
        raw = raw_class_of(rel, dataset, taxonomy)
        if raw is None:
            records.append(FileRecord(dataset, rel.as_posix(), rel.parent.name, "", "unknown_class"))
            continue
        code = taxonomy.map_label(dataset, raw)
        check = check_image(path, min_side)
        if not check.ok:
            records.append(
                FileRecord(dataset, rel.as_posix(), raw, code, check.reason, check.width, check.height)
            )
            continue
        image = normalise_image(path)
        stats = image_stats(image)
        out_rel = Path(code) / f"{dataset}_{len(records):05d}.jpg"
        out_path = processed_root / out_rel
        out_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(out_path, "JPEG", quality=95, subsampling=0)  # no EXIF is written
        records.append(
            FileRecord(
                dataset, rel.as_posix(), raw, code, "ok", image.size[0], image.size[1],
                round(stats["brightness_mean"], 3), round(stats["laplacian_var"], 3),
                out_rel.as_posix(),
            )
        )  # fmt: skip
    return records


def write_records(records: list[FileRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FILE_FIELDS)
        writer.writeheader()
        for r in records:
            writer.writerow(asdict(r))


def summarise(
    records: list[FileRecord],
    claimed: dict[str, int] | None,
    taxonomy: Taxonomy | None = None,
    dataset: str = "",
) -> dict[str, Any]:
    """Counts per unified class vs the dataset page's claims, plus drop reasons.

    Page claims use the page's own class names; they are mapped through the taxonomy so
    'Healthy' (page) and 'Healthy Leaf' (folder) compare as the same class.
    """
    by_status = Counter(r.status for r in records)
    ok_by_class = Counter(r.class_code for r in records if r.status == "ok")
    found_by_code = Counter(r.class_code for r in records if r.status != "unknown_class")
    comparison: dict[str, Any] = {}
    for name, claim in (claimed or {}).items():
        if taxonomy is not None and taxonomy.knows(dataset, name):
            code = taxonomy.map_label(dataset, name)
        else:
            code = name
        comparison[name] = {
            "unified_class": code,
            "page_claim": claim,
            "files_found": found_by_code.get(code, 0),
            "difference": found_by_code.get(code, 0) - claim,
        }
    return {
        "total_files": len(records),
        "by_status": dict(by_status),
        "usable_by_class": dict(ok_by_class),
        "page_vs_found": comparison,
        "unknown_class_folders": sorted({r.class_raw for r in records if r.status == "unknown_class"}),
    }


def write_summary(summary: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
