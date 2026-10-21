"""Layering check (spec 5.3, 0.2.8). Exit 1 on a forbidden import.

Rules: `app.domain` is pure (no framework, db, network, clock); `app.core` never imports api/services/
models; `app.api` never imports `app.db` internals directly except through services (from Phase 1).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"

DOMAIN_FORBIDDEN = {
    "fastapi",
    "starlette",
    "sqlalchemy",
    "asyncpg",
    "psycopg",
    "httpx",
    "requests",
    "redis",
    "boto3",
    "arq",
    "structlog",
    "anthropic",
    "app.db",
    "app.api",
    "app.services",
    "app.core.http",
    "app.core.storage",
}
DOMAIN_FORBIDDEN_CALLS = {"datetime.now", "datetime.utcnow", "time.time", "random.random"}
CORE_FORBIDDEN_PREFIXES = ("app.api", "app.services", "app.models", "app.jobs", "app.main")


def _imports(tree: ast.AST) -> list[str]:
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            found.append(node.module)
    return found


def _calls(tree: ast.AST) -> list[str]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                names.append(f"{node.func.value.id}.{node.func.attr}")
    return names


def check() -> list[str]:
    problems: list[str] = []
    for path in APP.rglob("*.py"):
        rel = path.relative_to(APP.parent).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = _imports(tree)
        if rel.startswith("app/domain/"):
            for imp in imports:
                if any(imp == f or imp.startswith(f + ".") for f in DOMAIN_FORBIDDEN):
                    problems.append(f"{rel}: domain must be pure, imports {imp}")
            for call in _calls(tree):
                if call in DOMAIN_FORBIDDEN_CALLS:
                    problems.append(f"{rel}: domain must not call {call}")
        if rel.startswith("app/core/"):
            for imp in imports:
                if imp.startswith(CORE_FORBIDDEN_PREFIXES):
                    problems.append(f"{rel}: core must not import {imp}")
    return problems


def main() -> int:
    problems = check()
    for p in problems:
        sys.stderr.write(f"LAYER {p}\n")
    sys.stdout.write(f"check_layers: {len(problems)} violations\n")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
