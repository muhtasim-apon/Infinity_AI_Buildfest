"""Export the OpenAPI schema to backend/openapi.json (contract between tracks, spec 0.5).

The app disables /openapi.json in production, so the schema is built from a development-mode app.
`--check` fails if the committed file differs from the generated one (contract drift).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from app.core.config import Settings
from app.main import create_app

OUT = Path(__file__).resolve().parents[1] / "openapi.json"


def generate() -> str:
    app = create_app(Settings(cg_env="development", _env_file=None))  # type: ignore[call-arg]
    return json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"


def main() -> int:
    text = generate()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            sys.stderr.write("openapi.json is out of date; run `make openapi`\n")
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8")
    sys.stdout.write(f"wrote {OUT}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
