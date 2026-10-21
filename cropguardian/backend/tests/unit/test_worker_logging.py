import pytest

# gunicorn needs POSIX-only modules; this test runs in CI (Linux) and is skipped on Windows.
pytest.importorskip("gunicorn.arbiter")


@pytest.mark.security
def test_uvicorn_access_log_is_explicitly_disabled():
    from app.core.worker import CgUvicornWorker

    assert CgUvicornWorker.CONFIG_KWARGS["access_log"] is False


@pytest.mark.security
def test_gunicorn_conf_uses_the_no_access_log_worker_and_no_accesslog():
    import runpy
    from pathlib import Path

    conf = runpy.run_path(str(Path(__file__).resolve().parents[2] / "gunicorn.conf.py"))
    assert conf["worker_class"] == "app.core.worker.CgUvicornWorker"
    assert conf["accesslog"] is None
