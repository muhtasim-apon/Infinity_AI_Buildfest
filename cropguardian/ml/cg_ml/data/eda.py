"""EDA figures from the per-file records (spec 9.4 step 6). Figures are generated, never hand-drawn.

Every number on a figure comes from `files_*.csv`; the title carries the commit-independent source
("recomputed from files.csv"), so no figure can show a value a script did not produce.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

PALETTE = ["#E69F00", "#56B4E9", "#009E73", "#D55E00", "#0072B2", "#CC79A7", "#8C7B00"]


def read_records(paths: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for p in paths:
        with p.open(encoding="utf-8", newline="") as fh:
            rows.extend(csv.DictReader(fh))
    return rows


def make_figures(rows: list[dict[str, str]], out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    ok = [r for r in rows if r["status"] == "ok"]
    written: list[Path] = []
    if not ok:
        return written

    # 1. usable images per unified class, stacked by source dataset
    classes = sorted({r["class_code"] for r in ok})
    sources = sorted({r["dataset"] for r in ok})
    counts = {(c, s): 0 for c in classes for s in sources}
    for r in ok:
        counts[(r["class_code"], r["dataset"])] += 1
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bottom: list[float] = [0.0] * len(classes)
    for i, s in enumerate(sources):
        vals = [counts[(c, s)] for c in classes]
        ax.bar(classes, vals, bottom=bottom, label=s, color=PALETTE[i % len(PALETTE)])
        bottom = [b + v for b, v in zip(bottom, vals, strict=True)]
    ax.set_ylabel("usable images")
    ax.set_title("Usable images per class and source (recomputed from files.csv)")
    ax.legend(title="source")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()
    p1 = out_dir / "class_counts_by_source.png"
    fig.savefig(p1, dpi=110)
    plt.close(fig)
    written.append(p1)

    # 2. brightness and blur distributions per source (confound check input, spec 9.6)
    for key, label, name in (
        ("brightness_mean", "mean brightness (0-255)", "brightness_by_source.png"),
        ("laplacian_var", "Laplacian variance (blur; low = blurrier)", "blur_by_source.png"),
    ):
        fig, ax = plt.subplots(figsize=(8, 4))
        for i, s in enumerate(sources):
            series = [float(r[key]) for r in ok if r["dataset"] == s]
            ax.hist(series, bins=40, alpha=0.6, label=f"{s} (n={len(series)})", color=PALETTE[i % 7])
        ax.set_xlabel(label)
        ax.set_ylabel("images")
        ax.set_title(f"{label} by source (recomputed from files.csv)")
        ax.legend()
        fig.tight_layout()
        path = out_dir / name
        fig.savefig(path, dpi=110)
        plt.close(fig)
        written.append(path)

    # 3. image size scatter
    fig, ax = plt.subplots(figsize=(6, 5))
    for i, s in enumerate(sources):
        pts = [(int(r["width"]), int(r["height"])) for r in ok if r["dataset"] == s]
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=6, alpha=0.5, label=s, color=PALETTE[i % 7])
    ax.set_xlabel("width (px)")
    ax.set_ylabel("height (px)")
    ax.set_title("Image dimensions after EXIF transpose (recomputed from files.csv)")
    ax.legend()
    fig.tight_layout()
    p4 = out_dir / "image_sizes.png"
    fig.savefig(p4, dpi=110)
    plt.close(fig)
    written.append(p4)

    # 4. per-class mean brightness and blur per source: the structural confound is visible here
    per: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in ok:
        per[(r["class_code"], r["dataset"])].append(float(r["brightness_mean"]))
    fig, ax = plt.subplots(figsize=(9, 4.5))
    labels = [f"{c}\n{s}" for (c, s) in sorted(per)]
    ax.bar(labels, [sum(v) / len(v) for _, v in sorted(per.items())], color="#009E73")
    ax.set_ylabel("mean brightness")
    ax.set_title("Mean brightness per class and source (recomputed from files.csv)")
    plt.setp(ax.get_xticklabels(), rotation=60, ha="right", fontsize=7)
    fig.tight_layout()
    p5 = out_dir / "brightness_per_class_source.png"
    fig.savefig(p5, dpi=110)
    plt.close(fig)
    written.append(p5)
    return written


def status_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    return dict(Counter(r["status"] for r in rows))
