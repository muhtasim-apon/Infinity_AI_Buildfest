"""CLI: `python -m cg_ml data download|verify|prepare|eda [--dataset D1] [--limit N]`.

Paths default to the repo layout (run from anywhere); heavy data lives in gitignored ml/data/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from cg_ml.data import download as dl
from cg_ml.data import eda, extract, manifest, prepare
from cg_ml.data.taxonomy import Taxonomy, load_labels

ML = Path(__file__).resolve().parents[1]
CONFIGS = ML / "configs"
RAW = ML / "data" / "raw"
EXTRACTED = ML / "data" / "extracted"
PROCESSED = ML / "data" / "processed"
EDA_DIR = ML / "reports" / "eda"
LOCK = CONFIGS / "data_lock.json"


def _selected(m: dict[str, Any], dataset: str | None) -> list[manifest.Archive]:
    items = manifest.archives(m, dataset)
    if not items:
        raise SystemExit(f"no archives for dataset {dataset!r}")
    return items


def cmd_download(args: argparse.Namespace) -> int:
    m = manifest.load_manifest(CONFIGS / "data_manifest.yaml")
    for a in _selected(m, args.dataset):
        if not a.url:
            sys.stdout.write(f"skip {a.dataset}/{a.filename}: no URL (pending)\n")
            continue
        path = dl.download(a, RAW)
        sys.stdout.write(f"downloaded {path.name} ({path.stat().st_size} bytes)\n")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    m = manifest.load_manifest(CONFIGS / "data_manifest.yaml")
    report: dict[str, Any] = {}
    status = 0
    for a in _selected(m, args.dataset):
        path = RAW / a.filename
        if not path.exists():
            sys.stdout.write(f"MISSING {a.dataset}/{a.filename}\n")
            status = 1
            continue
        try:
            digest = manifest.verify_archive(path, a, LOCK)
        except manifest.ChecksumMismatchError as exc:
            sys.stdout.write(f"MISMATCH {exc}\n")
            status = 2
            continue
        report[f"{a.dataset}/{a.filename}"] = {
            "sha256": digest, "size_bytes": path.stat().st_size,
            "matches_published": a.sha256_published == digest,
        }  # fmt: skip
        sys.stdout.write(f"OK {a.dataset}/{a.filename} {digest[:16]}...\n")
    out = ML / "reports" / "data_verify.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return status


def cmd_prepare(args: argparse.Namespace) -> int:
    m = manifest.load_manifest(CONFIGS / "data_manifest.yaml")
    taxonomy = Taxonomy(load_labels(CONFIGS / "labels.yaml"))
    datasets = [args.dataset] if args.dataset else [
        k for k, v in m["datasets"].items() if v["status"] == "training_source"
    ]  # fmt: skip
    all_records: list[prepare.FileRecord] = []
    for ds in datasets:
        for a in manifest.archives(m, ds):
            path = RAW / a.filename
            if not path.exists():
                raise SystemExit(f"{path} missing: run `data download` first")
            manifest.verify_archive(path, a, LOCK)  # abort on mismatch (spec 9.4 step 1)
            dest = EXTRACTED / ds
            if not dest.exists() or not any(dest.rglob("*")):
                n = extract.extract(path, dest)
                sys.stdout.write(f"extracted {n} files to {dest}\n")
        records = prepare.prepare_dataset(
            ds, EXTRACTED / ds, PROCESSED / ds, taxonomy, limit=args.limit
        )
        prepare.write_records(records, EDA_DIR / f"files_{ds}.csv")
        claimed = m["datasets"][ds].get("classes_claimed_by_page")
        summary = prepare.summarise(records, claimed, taxonomy, ds)
        prepare.write_summary(summary, EDA_DIR / f"summary_{ds}.json")
        sys.stdout.write(f"{ds}: {json.dumps(summary['by_status'])}\n")
        all_records.extend(records)
    return 0


def cmd_eda(_args: argparse.Namespace) -> int:
    files = sorted(EDA_DIR.glob("files_*.csv"))
    if not files:
        raise SystemExit("no files_*.csv: run `data prepare` first")
    written = eda.make_figures(eda.read_records(files), EDA_DIR)
    for p in written:
        sys.stdout.write(f"wrote {p.relative_to(ML.parent)}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cg_ml")
    sub = parser.add_subparsers(dest="group", required=True)
    data = sub.add_parser("data").add_subparsers(dest="cmd", required=True)
    commands = {
        "download": cmd_download,
        "verify": cmd_verify,
        "prepare": cmd_prepare,
        "eda": cmd_eda,
    }
    for name, fn in commands.items():
        p = data.add_parser(name)
        p.add_argument("--dataset", default=None)
        p.add_argument("--limit", type=int, default=None)
        p.set_defaults(fn=fn)
    args = parser.parse_args(argv)
    return int(args.fn(args))


if __name__ == "__main__":
    sys.exit(main())
