"""Honesty scanner (spec 19.8, 0.2.6). Exit 1 on violation.

Fails when metric-looking numbers appear in docs/ or frontend/src outside allowed sources, or a
statistic in docs lacks a [S#]/[D#]/[R#] reference. Phase 0 scope: scans the files that exist;
frontend/ml checks tighten automatically as those directories fill up.

Allowed: values loaded from ml/reports/**, kb/golden results or k6 outputs (never typed by hand),
spec/plan documents (they state *targets*, labelled as such), and lines tagged `honesty-ok: reason`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METRIC_WORDS = r"(accuracy|f1|recall|precision|auroc|auc|sensitivity|specificity)"
METRIC_NEAR_NUMBER = re.compile(
    rf"\b{METRIC_WORDS}\b[^.\n]{{0,25}}?(\b0\.\d{{2,}}\b|\b\d{{1,3}}(\.\d+)?\s?%)", re.IGNORECASE
)
NUMBER_THEN_METRIC = re.compile(
    rf"(\b0\.\d{{2,}}\b|\b\d{{1,3}}(\.\d+)?\s?%)[^.\n]{{0,25}}?\b{METRIC_WORDS}\b", re.IGNORECASE
)
REF = re.compile(r"(?<![A-Za-z])[SDRP][0-9]+(?![0-9])")  # [S11], S11, P1 ...
EXEMPT_DIR_PARTS = {"plan", "plans", "congress", "research", "security-reviews", "report"}
EXEMPT_FILES = {
    "threat-model.md",
    "eval-plan.md",
    "statistics.md",
    "prd.md",
    "CROP_GUARDIAN_BUILD_SPEC.md",
}
TARGET_SIGNS = re.compile(r"[≥≤]|95\s?%\s?CI")  # targets / CI levels are not measured values
TARGET_WORDS = re.compile(
    r"\b(target|targets|threshold|gate|must|should|example|placeholder)\b", re.I
)


def scan() -> list[str]:
    problems: list[str] = []
    roots = [ROOT / "docs", ROOT / "frontend" / "src"]
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.suffix not in {".md", ".ts", ".tsx", ".json"} or not path.is_file():
                continue
            if "node_modules" in path.parts or path.name in EXEMPT_FILES:
                continue
            if EXEMPT_DIR_PARTS & set(path.parts):
                continue
            rel = path.relative_to(ROOT).as_posix()
            all_lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            for n, line in enumerate(all_lines, 1):
                nxt = all_lines[n] if n < len(all_lines) else ""
                if "honesty-ok:" in line or TARGET_WORDS.search(line) or TARGET_SIGNS.search(line):
                    continue
                if (
                    METRIC_NEAR_NUMBER.search(line) or NUMBER_THEN_METRIC.search(line)
                ) and not REF.search(line + " " + nxt):
                    problems.append(f"{rel}:{n}: metric-like number without a source reference")
    return problems


def main() -> int:
    problems = scan()
    for p in problems:
        sys.stderr.write(f"HONESTY {p}\n")
    sys.stdout.write(f"check_honesty: {len(problems)} violations\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
