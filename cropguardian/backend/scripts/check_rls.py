"""RLS check (spec 16.10). Exit 1 if any public table is neither RLS-forced nor listed in rls_exempt.yml.

Needs a database: `python scripts/check_rls.py` with MIGRATION_DATABASE_URL (or DATABASE_URL) set.
Without a database URL it SKIPS with exit 0 and says so (the gate records the skip; never a silent pass
of a real check - the gate only accepts SKIP in `--offline` runs).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg

EXEMPT_FILE = Path(__file__).resolve().parents[1] / "app" / "db" / "rls_exempt.yml"


def load_exempt() -> set[str]:
    names: set[str] = set()
    in_block = False
    for raw in EXEMPT_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("exempt:"):
            in_block = True
        elif in_block and ":" in line and not line.startswith("#"):
            names.add(line.split(":", 1)[0].strip())
    return names


def main() -> int:
    url = os.environ.get("MIGRATION_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        sys.stdout.write("check_rls: SKIPPED (no database URL)\n")
        return 0 if "--allow-skip" in sys.argv else 2
    exempt = load_exempt()
    bad: list[str] = []
    with psycopg.connect(url, connect_timeout=10) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity "
            "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = 'public' AND c.relkind = 'r'"
        )
        for name, enabled, forced in cur.fetchall():
            if name in exempt:
                continue
            if not (enabled and forced):
                bad.append(name)
    for name in bad:
        sys.stderr.write(f"RLS table public.{name} lacks ENABLE + FORCE ROW LEVEL SECURITY\n")
    sys.stdout.write(f"check_rls: {len(bad)} unprotected tables\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
