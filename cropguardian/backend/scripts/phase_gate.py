"""Phase gate (spec 19.6): `python scripts/phase_gate.py --phase N [--keep-going] [--offline]`.

Runs the steps in order, stops at the first failure unless --keep-going, prints a table, writes
runs/gates/phase-N.json, appends to PROGRESS.md and prints `PHASE N GATE: PASS|FAIL (step X)`.

Steps whose target does not exist yet (e.g. frontend before it is scaffolded) are recorded as
`N/A` with the reason - never as PASS. A step that *could* run but cannot because a tool is missing
is `SKIP` and makes the gate FAIL unless `--offline` is given (spec: --offline skips with a note).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]  # cropguardian/
BACKEND = REPO / "backend"
FRONTEND = REPO / "frontend"
RUNS = REPO / "runs" / "gates"
PY = sys.executable
NPM = shutil.which("npm") or "npm"  # npm.cmd on Windows
DEPENDS: dict[int, list[int]] = {
    0: [],
    1: [0],
    2: [0],
    3: [0],
    4: [1, 3],
    5: [0],
    6: [4, 5],
    7: [2, 4],
    8: [4],
    9: [3],
    10: [2, 8, 9],
    11: [6, 7, 8, 10],
    12: [11],
}


@dataclass
class Step:
    name: str
    status: str  # PASS FAIL N/A SKIP
    seconds: float
    note: str = ""


def run(
    cmd: list[str], cwd: Path, timeout: int = 900, env: dict[str, str] | None = None
) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, **(env or {})},
            check=False,
        )
    except FileNotFoundError:
        return 127, f"not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "timeout"
    tail = (proc.stdout + proc.stderr).strip().splitlines()[-6:]
    return proc.returncode, " | ".join(tail)[:400]


def have_module(mod: str) -> bool:
    return (
        subprocess.run([PY, "-c", f"import {mod}"], capture_output=True, check=False).returncode
        == 0
    )


def is_git_ignored(path: Path) -> bool:
    """True if git ignores `path`: a local .env is fine as long as it can never be committed."""
    git = shutil.which("git")
    if git is None:
        return False
    cmd = [git, "-C", str(REPO), "check-ignore", "-q", str(path)]
    return subprocess.run(cmd, check=False).returncode == 0


def docker_ok() -> bool:
    if not shutil.which("docker"):
        return False
    return (
        subprocess.run(["docker", "info"], capture_output=True, timeout=30, check=False).returncode
        == 0
    )


# Connection settings for the throwaway test Postgres + Redis (docker-compose.test.yml, `make test-db`).
TEST_STACK_ENV = {
    "MIGRATION_DATABASE_URL": "postgresql://cg_migrator:dev-migrator-pw@127.0.0.1:55432/cropguardian",
    "TEST_SUPER_DATABASE_URL": "postgresql://postgres:test-only-password@127.0.0.1:55432/cropguardian",
    "TEST_API_DATABASE_URL": "postgresql://cg_api:dev-api-pw@127.0.0.1:55432/cropguardian",
    "TEST_REDIS_URL": "redis://127.0.0.1:56379/0",
    "PYTHONPATH": str(BACKEND),
}  # fmt: skip


def test_stack_up() -> bool:
    """True when the test Postgres and Redis ports accept connections."""
    for port in (55432, 56379):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=1).close()
        except OSError:
            return False
    return True


def tool_step(
    name: str,
    module_or_bin: str,
    cmd: list[str],
    cwd: Path,
    offline: bool,
    is_module: bool = True,
    env: dict[str, str] | None = None,
) -> Step:
    t0 = time.time()
    present = have_module(module_or_bin) if is_module else shutil.which(module_or_bin) is not None
    if not present:
        return Step(
            name,
            "SKIP",
            0.0,
            f"{module_or_bin} not installed" + ("" if offline else " (use --offline to accept)"),
        )
    code, note = run(cmd, cwd, env=env)
    return Step(name, "PASS" if code == 0 else "FAIL", time.time() - t0, "" if code == 0 else note)


def steps_for(phase: int, offline: bool, db_url: str | None) -> list:
    def environment() -> Step:
        t0 = time.time()
        missing = [d for d in DEPENDS.get(phase, []) if not _gate_passed(d)]
        if missing:
            return Step(
                "1 environment", "FAIL", time.time() - t0, f"dependency gates not passed: {missing}"
            )
        leaked = [
            p
            for p in REPO.glob(".env*")
            if p.is_file() and p.name != ".env.example" and not is_git_ignored(p)
        ]
        if leaked:
            return Step(
                "1 environment",
                "FAIL",
                time.time() - t0,
                f"unignored secret-like files: {[p.name for p in leaked]}",
            )
        return Step("1 environment", "PASS", time.time() - t0, f"python {sys.version.split()[0]}")

    def fmt_lint() -> Step:
        a = tool_step(
            "3 ruff format", "ruff", [PY, "-m", "ruff", "format", "--check", "."], BACKEND, offline
        )
        if a.status != "PASS":
            return a
        return tool_step(
            "3 format+lint", "ruff", [PY, "-m", "ruff", "check", "."], BACKEND, offline
        )

    def frontend_lint() -> Step:
        if not (FRONTEND / "package.json").exists() or not (FRONTEND / "node_modules").exists():
            return Step("3b frontend lint", "N/A", 0.0, "frontend not installed (npm ci)")
        return tool_step(
            "3b frontend lint",
            "npm",
            [NPM, "run", "lint", "--silent"],
            FRONTEND,
            offline,
            is_module=False,
        )

    def types() -> Step:
        return tool_step("4 mypy", "mypy", [PY, "-m", "mypy"], BACKEND, offline)

    def bandit() -> Step:
        return tool_step(
            "5 bandit", "bandit", [PY, "-m", "bandit", "-q", "-r", "app", "-ll"], BACKEND, offline
        )

    def gitleaks() -> Step:
        t0 = time.time()
        binary = os.environ.get("GITLEAKS_BIN") or shutil.which("gitleaks")
        if not binary:
            note = "gitleaks not installed (set GITLEAKS_BIN)" + (
                "" if offline else " (use --offline)"
            )
            return Step("5 gitleaks", "SKIP", 0.0, note)
        cfg = str(REPO / ".gitleaks.toml")
        common = ["--redact", "--no-banner", "--config", cfg]
        for label, args, cwd in (
            ("history", [binary, "git", *common, str(REPO.parent)], REPO),
            # "." (cwd is REPO) keeps .gitleaksignore fingerprints relative, so they match on any machine
            ("working tree", [binary, "dir", *common, "."], REPO),
        ):
            code, note = run(args, cwd, timeout=300)
            if code != 0:
                return Step("5 gitleaks", "FAIL", time.time() - t0, f"{label}: {note}")
        return Step("5 gitleaks", "PASS", time.time() - t0, "git history + working tree")

    def project_checks() -> Step:
        t0 = time.time()
        for script in ("check_forbidden", "check_layers", "check_honesty"):
            code, note = run([PY, f"scripts/{script}.py"], BACKEND)
            if code != 0:
                return Step("6 project checks", "FAIL", time.time() - t0, f"{script}: {note}")
        return Step("6 project checks", "PASS", time.time() - t0, "forbidden, layers, honesty")

    def rls() -> Step:
        t0 = time.time()
        if not db_url:
            return Step(
                "6 check_rls",
                "SKIP",
                0.0,
                "no database URL" + ("" if offline else " (use --offline)"),
            )
        code, note = run(
            [PY, "scripts/check_rls.py"], BACKEND, env={"MIGRATION_DATABASE_URL": db_url}
        )
        return Step(
            "6 check_rls",
            "PASS" if code == 0 else "FAIL",
            time.time() - t0,
            "" if code == 0 else note,
        )

    def security_review_file() -> Step:
        t0 = time.time()
        f = REPO / "docs" / "security-reviews" / f"phase-{phase:02d}.md"
        if not f.exists():
            return Step("6 security review", "FAIL", 0.0, f"missing {f.relative_to(REPO)}")
        text = f.read_text(encoding="utf-8", errors="replace")
        if any(
            ln.lstrip().startswith("|") and "UNRESOLVED-HIGH" in ln.upper()
            for ln in text.splitlines()
        ):
            return Step(
                "6 security review", "FAIL", time.time() - t0, "unresolved HIGH finding listed"
            )
        return Step("6 security review", "PASS", time.time() - t0)

    def npm_audit() -> Step:
        t0 = time.time()
        if not (FRONTEND / "node_modules").exists():
            return Step("7 npm audit", "N/A", 0.0, "frontend not installed (npm ci)")
        if offline:
            return Step("7 npm audit", "SKIP", 0.0, "--offline (recorded)")
        code, note = run([NPM, "run", "audit:gate", "--silent"], FRONTEND)
        return Step(
            "7 npm audit",
            "PASS" if code == 0 else "FAIL",
            time.time() - t0,
            "" if code == 0 else note,
        )

    def pip_audit() -> Step:
        if offline:
            return Step("7 pip-audit", "SKIP", 0.0, "--offline (recorded)")
        t0 = time.time()
        for label, req_dir in (("backend", BACKEND), ("ml", REPO / "ml")):
            req = req_dir / "requirements.txt"
            if not req.exists():
                continue
            code, note = run(
                [
                    PY,
                    str(BACKEND / "scripts" / "run_pip_audit.py"),
                    "-r",
                    str(req),
                    "--progress-spinner",
                    "off",
                ],
                BACKEND,
                timeout=600,
            )
            if code != 0:
                return Step("7 pip-audit", "FAIL", time.time() - t0, f"{label}: {note}")
        return Step("7 pip-audit", "PASS", time.time() - t0, "backend + ml requirements")

    def migrations() -> Step:
        t0 = time.time()
        if not db_url:
            return Step(
                "8 migrations",
                "SKIP",
                0.0,
                "no migration database URL" + ("" if offline else " (use --offline)"),
            )
        env = {"MIGRATION_DATABASE_URL": db_url, "PYTHONPATH": str(BACKEND)}
        for args in (["upgrade", "head"], ["downgrade", "-1"], ["upgrade", "head"]):
            code, note = run([PY, "-m", "alembic", *args], BACKEND, env=env)
            if code != 0:
                return Step(
                    "8 migrations", "FAIL", time.time() - t0, f"alembic {' '.join(args)}: {note}"
                )
        return Step("8 migrations", "PASS", time.time() - t0, "up, down 1, up")

    def tests() -> Step:
        # Identity code (Phase 1+) is exercised by the real-Postgres tests, so the 85% floor only makes
        # sense over the whole suite. Without the test stack the unit-only run keeps the same floor.
        stack = test_stack_up()
        marker = "not perf and not chaos and not rag_live" + (
            "" if stack else " and not integration"
        )
        step = tool_step(
            "9 backend tests",
            "pytest",
            [
                PY,
                "-m",
                "pytest",
                "-q",
                "-m",
                marker,
                "--cov",
                "--cov-branch",
                "--cov-report=term-missing:skip-covered",
            ],
            BACKEND,
            offline,
            env=TEST_STACK_ENV if stack else None,
        )
        if step.status == "PASS":
            step.note = (
                "full suite on real Postgres+Redis" if stack else "unit only (no test stack)"
            )
        return step

    def security_suite() -> Step:
        return tool_step(
            "10 security suite",
            "pytest",
            [PY, "-m", "pytest", "-q", "-m", "security"],
            BACKEND,
            offline,
        )

    def openapi() -> Step:
        t0 = time.time()
        code, note = run(
            [PY, "scripts/export_openapi.py", "--check"], BACKEND, env={"PYTHONPATH": str(BACKEND)}
        )
        return Step(
            "2 openapi contract",
            "PASS" if code == 0 else "FAIL",
            time.time() - t0,
            "" if code == 0 else note,
        )

    def frontend_build() -> Step:
        if not (FRONTEND / "package.json").exists() or not (FRONTEND / "node_modules").exists():
            return Step("2b frontend build", "N/A", 0.0, "frontend not installed (npm ci)")
        return tool_step(
            "2b frontend build",
            "npm",
            [NPM, "run", "build", "--silent"],
            FRONTEND,
            offline,
            is_module=False,
        )

    def frontend_tests() -> Step:
        if not (FRONTEND / "node_modules").exists():
            return Step("14 frontend tests", "N/A", 0.0, "frontend not installed (npm ci)")
        return tool_step(
            "14 frontend tests",
            "npm",
            [NPM, "test", "--silent"],
            FRONTEND,
            offline,
            is_module=False,
        )

    def compose_healthy() -> Step:
        t0 = time.time()
        if not docker_ok():
            return Step(
                "20 P0 compose stack",
                "SKIP",
                0.0,
                "docker not running" + ("" if offline else " (use --offline)"),
            )
        # 1) all compose files parse
        for files in (["docker-compose.yml"], ["docker-compose.test.yml"]):
            args = ["docker", "compose", *[x for f in files for x in ("-f", f)], "config", "-q"]
            code, note = run(args, REPO)
            if code != 0:
                return Step(
                    "20 P0 compose stack", "FAIL", time.time() - t0, f"config {files}: {note}"
                )
        # 2) bring up the real stack, migrate, wait for the API to be healthy
        if not (REPO / ".env").exists():
            run([PY, "backend/scripts/make_env.py"], REPO)
        bash = shutil.which("bash")
        if bash is None:
            return Step("20 P0 compose stack", "SKIP", 0.0, "bash not found (needed for verify.sh)")
        run([bash, "infra/nginx/make-certs.sh"], REPO, timeout=300)
        code, note = run(
            [
                "docker",
                "compose",
                "up",
                "-d",
                "--build",
                "postgres",
                "redis",
                "minio",
                "minio-init",
                "api",
                "nginx",
            ],
            REPO,
            timeout=900,
        )
        if code != 0:
            return Step("20 P0 compose stack", "FAIL", time.time() - t0, f"up: {note}")
        deadline = time.time() + 120
        healthy = False
        while time.time() < deadline:
            probe, out = run(
                ["docker", "compose", "ps", "api", "--format", "{{.Health}}"], REPO, timeout=30
            )
            if probe == 0 and out.strip().endswith("healthy") and "unhealthy" not in out:
                healthy = True
                break
            time.sleep(3)
        if not healthy:
            return Step("20 P0 compose stack", "FAIL", time.time() - t0, "api never became healthy")
        code, note = run(
            ["docker", "compose", "--profile", "tools", "run", "--rm", "--build", "migrate"],
            REPO,
            timeout=600,
        )
        if code != 0:
            return Step("20 P0 compose stack", "FAIL", time.time() - t0, f"migrate: {note}")
        # 3) edge assertions through the real Nginx (headers, redirect, TRACE, limits, caching)
        code, note = run(
            [bash, "infra/nginx/verify.sh", "https://localhost", "http://localhost"],
            REPO,
            timeout=300,
        )
        return Step(
            "20 P0 compose stack",
            "PASS" if code == 0 else "FAIL",
            time.time() - t0,
            "up, healthy, migrated, edge checks" if code == 0 else note,
        )

    def hosted_health() -> Step:
        t0 = time.time()
        url = os.environ.get("HOSTED_HEALTH_URL", "")
        if not url:
            return Step(
                "20 P0 hosted /health",
                "SKIP",
                0.0,
                "HOSTED_HEALTH_URL not set" + ("" if offline else " (use --offline)"),
            )
        code, note = run(
            [
                PY,
                "-c",
                "import sys,urllib.request as u;r=u.urlopen(sys.argv[1],timeout=60);sys.exit(0 if r.status==200 else 1)",
                url,
            ],
            REPO,
            timeout=90,
        )
        return Step(
            "20 P0 hosted /health",
            "PASS" if code == 0 else "FAIL",
            time.time() - t0,
            "" if code == 0 else note,
        )

    def identity_suite() -> Step:
        """Whole backend suite against REAL Postgres + Redis (no silent skips), then coverage floors."""
        t0 = time.time()
        name = "21 P1 identity suite"
        if not docker_ok():
            return Step(
                name, "SKIP", 0.0, "docker not running" + ("" if offline else " (use --offline)")
            )
        compose_test = ["docker", "compose", "-f", "docker-compose.test.yml"]
        code, note = run([*compose_test, "up", "-d", "--wait"], REPO, timeout=300)
        if code != 0:
            return Step(name, "FAIL", time.time() - t0, f"test stack: {note}")
        env = TEST_STACK_ENV
        code, note = run([PY, "-m", "alembic", "upgrade", "head"], BACKEND, env=env)
        if code != 0:
            return Step(name, "FAIL", time.time() - t0, f"alembic upgrade: {note}")
        RUNS.mkdir(parents=True, exist_ok=True)
        report = RUNS / "coverage-p1.json"
        proc = subprocess.run(
            [PY, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider", "-rs", "--cov=app",
             "--cov-branch", f"--cov-report=json:{report}", "--cov-fail-under=80"],
            cwd=BACKEND, capture_output=True, text=True, timeout=1800, check=False,
            env={**os.environ, **env},
        )  # fmt: skip
        out = proc.stdout + proc.stderr
        if proc.returncode != 0:
            return Step(
                name, "FAIL", time.time() - t0, " | ".join(out.strip().splitlines()[-6:])[:400]
            )
        silent = [ln for ln in out.splitlines() if "SKIPPED" in ln and "TEST_" in ln]
        if silent:
            return Step(
                name, "FAIL", time.time() - t0, f"tests silently skipped: {silent[0][:200]}"
            )
        code, note = run([PY, "scripts/check_coverage.py", str(report)], BACKEND)
        return Step(
            name,
            "PASS" if code == 0 else "FAIL",
            time.time() - t0,
            note if code else "real Postgres+Redis; coverage floors met",
        )

    def compose_smoke() -> Step:
        """register+verify+login, admin TOTP flow, 429 on login, audit chain - on the real stack."""
        t0 = time.time()
        name = "22 P1 compose smoke"
        if not docker_ok():
            return Step(
                name, "SKIP", 0.0, "docker not running" + ("" if offline else " (use --offline)")
            )
        bash = shutil.which("bash")
        if bash is None:
            return Step(name, "SKIP", 0.0, "bash not found")
        run(
            ["docker", "compose", "restart", "api"], REPO, timeout=120
        )  # re-seed demo users after migrate
        deadline = time.time() + 120
        while time.time() < deadline:
            probe, out = run(
                ["docker", "compose", "ps", "api", "--format", "{{.Health}}"], REPO, timeout=30
            )
            if probe == 0 and out.strip().endswith("healthy") and "unhealthy" not in out:
                break
            time.sleep(3)
        run(["docker", "compose", "restart", "nginx"], REPO, timeout=60)
        time.sleep(3)
        code, note = run(
            [PY, "scripts/p1_smoke.py", "--insecure-loopback"], BACKEND, timeout=300,
            env={"PYTHONPATH": str(BACKEND)},
        )  # fmt: skip
        return Step(
            name,
            "PASS" if code == 0 else "FAIL",
            time.time() - t0,
            note if code else "15 end-to-end checks",
        )

    def hosted_ready() -> Step:
        t0 = time.time()
        base = os.environ.get("HOSTED_HEALTH_URL", "").rsplit("/health", 1)[0]
        if not base:
            return Step(
                "23 P1 hosted readiness",
                "SKIP",
                0.0,
                "HOSTED_HEALTH_URL not set" + ("" if offline else " (use --offline)"),
            )
        code, note = run(
            [PY, "-c", "import json,sys,urllib.request as u;d=json.load(u.urlopen(sys.argv[1]+'/health/ready',timeout=60));sys.exit(0 if d=={'db':'ok','redis':'ok'} else 1)", base],
            REPO, timeout=90,
        )  # fmt: skip
        return Step(
            "23 P1 hosted readiness",
            "PASS" if code == 0 else "FAIL",
            time.time() - t0,
            "db + redis ok"
            if code == 0
            else "hosted /health/ready is not db+redis ok (deploy the new code and set REDIS_URL)",
        )

    common = [
        environment,
        openapi,
        frontend_build,
        fmt_lint,
        frontend_lint,
        types,
        bandit,
        gitleaks,
        project_checks,
        rls,
        security_review_file,
        pip_audit,
        npm_audit,
        migrations,
        tests,
        security_suite,
        frontend_tests,
    ]
    phase_specific = {
        0: [compose_healthy, hosted_health],
        1: [compose_healthy, identity_suite, compose_smoke, hosted_health, hosted_ready],
    }.get(phase, [])
    return [*common, *phase_specific]


def _gate_passed(phase: int) -> bool:
    f = RUNS / f"phase-{phase}.json"
    try:
        return json.loads(f.read_text(encoding="utf-8")).get("result") == "PASS"
    except (OSError, ValueError):
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", type=int, required=True)
    ap.add_argument("--keep-going", action="store_true")
    ap.add_argument("--offline", action="store_true")
    args = ap.parse_args()

    db_url = os.environ.get("MIGRATION_DATABASE_URL") or None
    results: list[Step] = []
    failed: str | None = None
    for make_step in steps_for(args.phase, args.offline, db_url):
        step = make_step()
        results.append(step)
        sys.stdout.write(f"{step.status:5} {step.name} ({step.seconds:.1f}s) {step.note}\n")
        sys.stdout.flush()
        bad = step.status == "FAIL" or (step.status == "SKIP" and not args.offline)
        if bad and failed is None:
            failed = step.name
        if bad and not args.keep_going:
            break

    result = "PASS" if failed is None else "FAIL"
    RUNS.mkdir(parents=True, exist_ok=True)
    report = {
        "phase": args.phase,
        "result": result,
        "failed_step": failed,
        "offline": args.offline,
        "at": datetime.now(UTC).isoformat(),
        "steps": [asdict(s) for s in results],
    }
    (RUNS / f"phase-{args.phase}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    line = f"- gate phase {args.phase}: {result}{'' if failed is None else f' (step {failed})'} at {report['at']}\n"
    progress = REPO / "PROGRESS.md"
    if progress.exists():
        progress.write_text(progress.read_text(encoding="utf-8") + line, encoding="utf-8")

    if result == "PASS":
        (REPO / ".phase").write_text(f"{args.phase}\n", encoding="utf-8")
        sys.stdout.write(f"PHASE {args.phase} GATE: PASS\n")
        return 0
    sys.stdout.write(f"PHASE {args.phase} GATE: FAIL (step {failed})\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
