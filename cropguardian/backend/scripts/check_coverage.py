"""Per-file coverage floors from a coverage.py JSON report (spec 19.6).

    python scripts/check_coverage.py runs/gates/coverage-p1.json

Security-critical modules must have 100% line AND branch coverage; the backend as a whole must stay
above the project floor. Gaps are listed, never silenced with `pragma: no cover` in these files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

FULL_COVERAGE = (
    "app/core/security.py",
    "app/core/sessions.py",
    "app/core/csrf.py",
    "app/core/authz.py",
    "app/core/ratelimit.py",
    "app/core/redirects.py",
)
TOTAL_FLOOR = 80.0


def main(path: str) -> int:
    report = json.loads(Path(path).read_text(encoding="utf-8"))
    files = {k.replace("\\", "/"): v for k, v in report["files"].items()}
    problems: list[str] = []
    for name in FULL_COVERAGE:
        entry = files.get(name)
        if entry is None:
            problems.append(f"{name}: not measured")
            continue
        missing_lines = entry["missing_lines"]
        missing_branches = entry["missing_branches"]
        if missing_lines or missing_branches:
            problems.append(f"{name}: lines {missing_lines} branches {missing_branches}")
        source = Path(name).read_text(encoding="utf-8") if Path(name).exists() else ""
        if "pragma: no cover" in source:
            problems.append(f"{name}: contains 'pragma: no cover'")
    total = report["totals"]["percent_covered"]
    if total < TOTAL_FLOOR:
        problems.append(f"total coverage {total:.1f}% is below {TOTAL_FLOOR}%")
    if problems:
        sys.stdout.write("coverage floors NOT met:\n  " + "\n  ".join(problems) + "\n")
        return 1
    sys.stdout.write(
        f"coverage floors met: {len(FULL_COVERAGE)} security modules at 100%, total {total:.1f}%\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "../runs/gates/coverage-p1.json"))
