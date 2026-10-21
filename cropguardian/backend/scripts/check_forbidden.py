"""Forbidden-pattern scanner (spec 19.8). Exit 1 on any violation.

Exception: append `# forbidden-ok: <reason>` on the same line; exceptions are listed in the report.
Scans backend/app (Python) and frontend/src (TypeScript) plus repository-level secret files.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # cropguardian/
OK_MARK = "forbidden-ok:"

PY_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("eval(", re.compile(r"(?<![\w.])eval\(")),
    ("exec(", re.compile(r"(?<![\w.])exec\(")),
    ("pickle", re.compile(r"\b(import pickle|from pickle|cPickle|marshal|shelve)\b")),
    ("torch.load without weights_only", re.compile(r"torch\.load\((?!.*weights_only=True)")),
    ("yaml.load(", re.compile(r"\byaml\.load\(")),
    ("subprocess shell=True", re.compile(r"shell\s*=\s*True")),
    ("os.system/os.popen", re.compile(r"\bos\.(system|popen)\(")),
    ("tempfile.mktemp", re.compile(r"\btempfile\.mktemp\(")),
    ("verify=False", re.compile(r"verify\s*=\s*False")),
    ("CORS wildcard", re.compile(r"allow_origins\s*=\s*\[\s*[\"']\*[\"']")),
    ("print(", re.compile(r"(?<![\w.])print\(")),
    ("assert in app code", re.compile(r"^\s*assert\s")),
    (
        "secret compared with ==",
        re.compile(r"\b\w*(token|secret|digest|otp|signature|csrf)\w*\s*(==|!=)\s*[\w\"']", re.I),
    ),
    (
        "logging sensitive variable",
        re.compile(r"log\w*\.\w+\([^)]*\b(password|token|secret|otp|session|phone)\b\s*=", re.I),
    ),
    ("TODO/FIXME in core", re.compile(r"\b(TODO|FIXME)\b")),
]
PY_ONLY_IN = {"TODO/FIXME in core": "app/core"}  # restricted to security-critical modules
PY_ALLOWED_FILES = {
    "direct httpx": {"app/core/http.py"},
    "anthropic": {"app/advisory/llm_adapter.py"},
}
PY_IMPORT_RULES = [
    ("direct httpx import", re.compile(r"^\s*(import httpx|from httpx)"), "app/core/http.py"),
    (
        "anthropic import",
        re.compile(r"^\s*(import anthropic|from anthropic)"),
        "app/advisory/llm_adapter.py",
    ),
]

TS_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("dangerouslySetInnerHTML", re.compile(r"dangerouslySetInnerHTML")),
    ("innerHTML/outerHTML", re.compile(r"\b(innerHTML|outerHTML|insertAdjacentHTML)\b")),
    ("document.write", re.compile(r"document\.write\(")),
    ("eval(", re.compile(r"(?<![\w.])eval\(")),
    ("new Function(", re.compile(r"new Function\(")),
    ("string setTimeout", re.compile(r"setTimeout\(\s*[\"'`]")),
    ("localStorage/sessionStorage", re.compile(r"\b(localStorage|sessionStorage)\b")),
    ("external http(s) literal", re.compile(r"[\"'`]https?://(?!localhost)[^\"'`]+[\"'`]")),
    (
        "target=_blank without rel",
        re.compile(r"target=[\"']_blank[\"'](?![^>]*noopener noreferrer)"),
    ),
]
TS_TOKEN_FILES = ("design/tokens", "design/motion")
HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")

SECRET_FILE_NAMES = {".env", ".env.local", ".env.production"}
SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
BINARY_DATA_SUFFIXES = {".onnx", ".pt", ".pth", ".ckpt", ".safetensors", ".h5", ".npy", ".zip"}
SKIP_DIRS = {"node_modules", ".venv", "__pycache__", ".git", "dist", "runs", "kb/raw", ".vercel"}


def _lines(path: Path):
    try:
        yield from enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
    except OSError:
        return


def scan_python(violations: list[dict], exceptions: list[dict]) -> None:
    for path in (ROOT / "backend" / "app").rglob("*.py"):
        rel = path.relative_to(ROOT / "backend").as_posix()
        for n, line in _lines(path):
            ok = OK_MARK in line
            for name, rx in PY_RULES:
                limit = PY_ONLY_IN.get(name)
                if limit and not rel.startswith(limit):
                    continue
                if rx.search(line.split("#")[0] if name != "TODO/FIXME in core" else line):
                    (exceptions if ok else violations).append(
                        {"file": rel, "line": n, "rule": name}
                    )
            for name, rx, allowed in PY_IMPORT_RULES:
                if rx.search(line) and rel != allowed:
                    (exceptions if ok else violations).append(
                        {"file": rel, "line": n, "rule": name}
                    )


def scan_typescript(violations: list[dict], exceptions: list[dict]) -> None:
    src = ROOT / "frontend" / "src"
    if not src.exists():
        return
    for path in [*src.rglob("*.ts"), *src.rglob("*.tsx")]:
        rel = path.relative_to(ROOT / "frontend").as_posix()
        if ".test." in rel or "/tests/" in rel:
            continue
        for n, line in _lines(path):
            ok = OK_MARK in line
            for name, rx in TS_RULES:
                if rx.search(line):
                    (exceptions if ok else violations).append(
                        {"file": rel, "line": n, "rule": name}
                    )
            if HEX_RE.search(line) and not any(t in rel for t in TS_TOKEN_FILES):
                (exceptions if ok else violations).append(
                    {"file": rel, "line": n, "rule": "hex colour outside design/tokens"}
                )


def scan_repo(violations: list[dict]) -> None:
    try:
        tracked = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        ).stdout.splitlines()
    except (OSError, subprocess.SubprocessError):
        tracked = [
            p.relative_to(ROOT).as_posix()
            for p in ROOT.rglob("*")
            if p.is_file() and not any(s in p.parts for s in SKIP_DIRS)
        ]
    for rel in tracked:
        p = Path(rel)
        if p.name in SECRET_FILE_NAMES or p.suffix in SECRET_SUFFIXES:
            violations.append({"file": rel, "line": 0, "rule": "secret-like file in repo"})
        if p.suffix in BINARY_DATA_SUFFIXES and not rel.startswith(
            ("e2e/fixtures", "backend/tests")
        ):
            violations.append({"file": rel, "line": 0, "rule": "dataset/weights committed"})


def main() -> int:
    violations: list[dict] = []
    exceptions: list[dict] = []
    scan_python(violations, exceptions)
    scan_typescript(violations, exceptions)
    scan_repo(violations)
    report = {"violations": violations, "exceptions": exceptions}
    out = ROOT / "runs" / "gates" / "check_forbidden.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for v in violations:
        sys.stderr.write(f"FORBIDDEN {v['file']}:{v['line']} {v['rule']}\n")
    sys.stdout.write(
        f"check_forbidden: {len(violations)} violations, {len(exceptions)} exceptions\n"
    )
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
