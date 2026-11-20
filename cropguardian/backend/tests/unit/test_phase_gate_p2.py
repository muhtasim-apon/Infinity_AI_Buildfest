"""Phase gate semantics that matter for trust (spec 19.6, DECISIONS D-011, D-019, D-024).

A P2 step whose target is not built must FAIL ("not built yet"), never N/A or PASS, so a green P2
gate means every check ran. Earlier gates keep their step lists. Step 9 runs the whole suite when the
test Postgres + Redis are up and keeps the same coverage floor when they are not.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "phase_gate.py"
_spec = importlib.util.spec_from_file_location("phase_gate", SCRIPT)
assert _spec and _spec.loader
phase_gate = importlib.util.module_from_spec(_spec)
sys.modules["phase_gate"] = phase_gate  # dataclasses look the defining module up here
_spec.loader.exec_module(phase_gate)


def marker_of(cmd: list[str]) -> str:
    """The pytest -m expression: the argument after the LAST "-m" (the first one is `python -m pytest`)."""
    last = max(i for i, part in enumerate(cmd) if part == "-m")
    return cmd[last + 1]


def steps(phase: int, offline: bool = True) -> dict[str, Any]:
    return {fn.__name__: fn for fn in phase_gate.steps_for(phase, offline, None)}


@pytest.fixture
def empty_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A repo layout with no e2e specs and no frontend scripts: nothing for P2 to run."""
    (tmp_path / "e2e" / "journeys").mkdir(parents=True)
    (tmp_path / "frontend" / "scripts").mkdir(parents=True)
    monkeypatch.setattr(phase_gate, "REPO", tmp_path)
    monkeypatch.setattr(phase_gate, "E2E", tmp_path / "e2e")
    monkeypatch.setattr(phase_gate, "FRONTEND", tmp_path / "frontend")
    return tmp_path


def test_phase_2_has_its_own_checks_and_earlier_phases_do_not() -> None:
    p2 = steps(2)
    for name in (
        "p2_budgets",
        "p2_no_inline",
        "p2_e2e_layout",
        "p2_axe",
        "p2_visual",
        "p2_lighthouse",
        "p2_stills",
    ):
        assert name in p2, f"P2 gate is missing {name}"
    for earlier in (0, 1):
        assert not any(n.startswith("p2_") for n in steps(earlier)), f"phase {earlier} changed"


@pytest.mark.parametrize("name", ["p2_visual", "p2_lighthouse", "p2_stills", "p2_e2e_layout"])
def test_an_unbuilt_p2_check_fails_and_says_why(name: str, empty_repo: Path) -> None:
    step = steps(2)[name]()
    assert step.status == "FAIL", f"{name} must not be N/A or PASS when its target is missing"
    assert "not built yet" in step.note


def test_the_layout_check_needs_both_specs(empty_repo: Path) -> None:
    (empty_repo / "e2e" / "journeys" / "layout.spec.ts").write_text("//", encoding="utf-8")
    step = steps(2)["p2_e2e_layout"]()
    assert step.status == "FAIL"
    assert "shells.spec.ts" in step.note


def test_a_built_spec_without_installed_e2e_dependencies_fails(empty_repo: Path) -> None:
    (empty_repo / "e2e" / "journeys" / "a11y.spec.ts").write_text("//", encoding="utf-8")
    step = steps(2)["p2_axe"]()
    assert step.status == "FAIL"
    assert "not installed" in step.note


def test_step_9_runs_the_whole_suite_when_the_test_stack_is_up(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    def fake_tool_step(name: str, module: str, cmd: list[str], cwd: Path, offline: bool, **kw: Any):
        captured.update(cmd=cmd, env=kw.get("env"), name=name)
        return phase_gate.Step(name, "PASS", 0.0)

    monkeypatch.setattr(phase_gate, "tool_step", fake_tool_step)
    monkeypatch.setattr(phase_gate, "stack_env", lambda: dict(phase_gate.TEST_STACK_ENV))
    step = steps(2)["tests"]()
    marker = marker_of(captured["cmd"])
    assert "not perf" in marker  # we really read the marker expression
    assert "integration" not in marker
    assert captured["env"] == phase_gate.TEST_STACK_ENV
    assert "real Postgres" in step.note


def test_step_9_keeps_the_same_floor_without_the_stack(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_tool_step(name: str, module: str, cmd: list[str], cwd: Path, offline: bool, **kw: Any):
        captured.update(cmd=cmd, env=kw.get("env"))
        return phase_gate.Step(name, "PASS", 0.0)

    monkeypatch.setattr(phase_gate, "tool_step", fake_tool_step)
    monkeypatch.setattr(phase_gate, "stack_env", lambda: None)
    step = steps(2)["tests"]()
    marker = marker_of(captured["cmd"])
    assert "not perf" in marker
    assert "not integration" in marker
    assert captured["env"] is None
    assert "unit only" in step.note
    # the coverage floor is the project's own (pyproject fail_under = 85), never lowered here
    assert not any("--cov-fail-under" in part for part in captured["cmd"])


_CI_STACK = {
    "MIGRATION_DATABASE_URL": "postgresql://m:x@127.0.0.1:5432/cg",
    "TEST_SUPER_DATABASE_URL": "postgresql://s:x@127.0.0.1:5432/cg",
    "TEST_API_DATABASE_URL": "postgresql://a:x@127.0.0.1:5432/cg",
    "TEST_REDIS_URL": "redis://127.0.0.1:6379/0",
}


def test_stack_env_prefers_the_services_the_environment_provides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for k, v in _CI_STACK.items():
        monkeypatch.setenv(k, v)
    probed: list[tuple[str, int]] = []
    monkeypatch.setattr(phase_gate, "_reachable", lambda h, p: probed.append((h, p)) or True)
    env = phase_gate.stack_env()
    assert env is not None
    assert env["TEST_SUPER_DATABASE_URL"] == _CI_STACK["TEST_SUPER_DATABASE_URL"]
    assert ("127.0.0.1", 5432) in probed and ("127.0.0.1", 6379) in probed


def test_stack_env_falls_back_to_the_local_test_stack(monkeypatch: pytest.MonkeyPatch) -> None:
    for k in _CI_STACK:
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setattr(phase_gate, "_reachable", lambda h, p: p in (55432, 56379))
    assert phase_gate.stack_env() == phase_gate.TEST_STACK_ENV


def test_stack_env_is_none_when_nothing_answers(monkeypatch: pytest.MonkeyPatch) -> None:
    for k, v in _CI_STACK.items():
        monkeypatch.setenv(k, v)
    monkeypatch.setattr(phase_gate, "_reachable", lambda h, p: False)
    assert phase_gate.stack_env() is None
    assert phase_gate.test_stack_up() is False


def test_stack_env_ignores_a_partial_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for k, v in _CI_STACK.items():
        monkeypatch.setenv(k, v)
    monkeypatch.delenv("TEST_REDIS_URL")
    monkeypatch.setattr(phase_gate, "_reachable", lambda h, p: p in (5432, 6379))
    assert phase_gate.stack_env() is None  # never half CI, half local


def test_a_dependency_gate_is_satisfied_only_when_all_its_steps_rerun(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(phase_gate, "RUNS", tmp_path)  # no stored reports at all (as in CI)
    monkeypatch.setattr(phase_gate, "REPO", tmp_path)  # no stray .env files
    # phase 1 re-runs every phase-0 step, so the missing phase-0 report is not a failure
    assert "dependency" not in steps(1)["environment"]().note
    # a phase whose steps do NOT include all of phase 0's still needs the stored phase-0 PASS
    monkeypatch.setitem(phase_gate.DEPENDS, 99, [0])
    step = steps(99)["environment"]()
    assert step.status == "FAIL"
    assert "dependency gates not passed: [0]" in step.note


def test_the_i18n_check_joins_project_checks_only_from_phase_2(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ran: list[str] = []

    def fake_run(cmd: list[str], cwd: Path, **kw: Any):
        ran.append(Path(cmd[1]).stem)
        return 0, ""

    monkeypatch.setattr(phase_gate, "run", fake_run)
    steps(1)["project_checks"]()
    assert "check_i18n" not in ran
    ran.clear()
    steps(2)["project_checks"]()
    assert ran == ["check_forbidden", "check_layers", "check_honesty", "check_i18n"]
