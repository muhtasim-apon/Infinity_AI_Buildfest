"""Seed data (spec 19.7 `make seed`). Idempotent.

Phase 1 seeds the three demo users (tenant `demo`). The base catalogue (crops, stages, areas) needs
the Phase 4 tables and is added there; this script does not pretend otherwise (DECISIONS D-018).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings
from app.db.session import make_engine
from app.services.demo import seed_demo_users


async def main() -> int:
    engine = make_engine(get_settings())
    try:
        count = await seed_demo_users(engine)
    finally:
        await engine.dispose()
    sys.stdout.write(f"demo users present: {count}\n")
    return 0 if count >= 3 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
