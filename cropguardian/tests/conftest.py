"""Shared pytest configuration.

Fixtures to implement:
  - ``settings``     test Settings (no real secrets; LLM provider = fake)
  - ``client``       httpx.AsyncClient over the ASGI app
  - ``db``           disposable Postgres with pgvector (testcontainers) + migrations + synthetic seed
  - ``farmer_token`` / ``agronomist_token`` / ``admin_token`` / ``other_farmer_token``
  - ``fake_llm``     respx route returning canned JSON (valid / uncited / banned / slow / 500)
  - ``images``       paths in tests/fixtures/images/ (valid jpeg/png/webp, dark, blurry, non-leaf)
  - ``malicious``    paths in tests/fixtures/malicious/ (generated harmless samples)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "services" / "api"))
