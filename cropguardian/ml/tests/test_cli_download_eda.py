import io
import json
import urllib.request
import zipfile
from pathlib import Path

import pytest
import yaml
from PIL import Image

from cg_ml import __main__ as cli
from cg_ml.data import download as dl
from cg_ml.data import eda, extract
from cg_ml.data.manifest import Archive


def jpg(path: Path, color=(30, 160, 60), size=(200, 160)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(path, "JPEG")


class FakeResp(io.BytesIO):
    def __init__(self, data: bytes, status: int = 200):
        super().__init__(data)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


# --- download ------------------------------------------------------------------------------------
def test_download_requires_url_and_allowed_host(tmp_path):
    with pytest.raises(ValueError, match="no URL"):
        dl.download(Archive("D1", "a.zip", None, None, None), tmp_path)
    with pytest.raises(Exception, match="not allowed"):
        dl.download(Archive("D1", "a.zip", "https://evil.example.com/a.zip", None, None), tmp_path)


def test_download_rejects_path_traversal_filename(tmp_path):
    arc = Archive("D1", "../a.zip", "https://data.mendeley.com/a", None, None)
    with pytest.raises(ValueError, match="unsafe"):
        dl.download(arc, tmp_path)


def test_download_writes_and_resumes(tmp_path, monkeypatch):
    seen = {}

    def fake_open(req, timeout):
        seen["range"] = req.headers.get("Range")
        return FakeResp(b"world", 206) if req.headers.get("Range") else FakeResp(b"helloworld", 200)

    monkeypatch.setattr(urllib.request, "urlopen", fake_open)
    arc = Archive("D1", "a.zip", "https://data.mendeley.com/a", 10, None)
    (tmp_path / "a.zip").write_bytes(b"hello")  # partial
    path = dl.download(arc, tmp_path)
    assert seen["range"] == "bytes=5-"
    assert path.read_bytes() == b"helloworld"
    assert dl.download(arc, tmp_path) == path  # already complete: no new request
    (tmp_path / "a.zip").write_bytes(b"x" * 11)
    with pytest.raises(ValueError, match="larger"):
        dl.download(arc, tmp_path)


def test_download_fresh_file(tmp_path, monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: FakeResp(b"abc", 200))
    arc = Archive("D1", "b.zip", "https://data.mendeley.com/b", None, None)
    assert dl.download(arc, tmp_path).read_bytes() == b"abc"


# --- extract: rar tool paths ------------------------------------------------------------------------
def test_rar_without_tool_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(extract, "find_rar_tool", lambda: None)
    with pytest.raises(extract.UnsafeArchiveError, match="no RAR extractor"):
        extract.extract_rar(tmp_path / "a.rar", tmp_path / "o")


def test_rar_extractor_failure_and_success(tmp_path, monkeypatch):
    monkeypatch.setattr(extract, "find_rar_tool", lambda: "7z")

    class Fail:
        returncode = 2

    monkeypatch.setattr(extract.subprocess, "run", lambda *a, **k: Fail())
    with pytest.raises(extract.UnsafeArchiveError, match="failed"):
        extract.extract_rar(tmp_path / "a.rar", tmp_path / "o")

    class Ok:
        returncode = 0

    def fake_run(cmd, **k):
        (tmp_path / "o").mkdir(exist_ok=True)
        (tmp_path / "o" / "f.jpg").write_bytes(b"x")
        return Ok()

    monkeypatch.setattr(extract.subprocess, "run", fake_run)
    assert extract.extract_rar(tmp_path / "a.rar", tmp_path / "o") == 1
    monkeypatch.setattr(extract, "find_rar_tool", lambda: "unrar")
    assert extract.extract(tmp_path / "a.rar", tmp_path / "o") == 1


# --- eda -----------------------------------------------------------------------------------------
def test_eda_makes_figures_and_handles_empty(tmp_path):
    csv_path = tmp_path / "files_D1.csv"
    header = (
        "dataset,source_rel_path,class_raw,class_code,status,width,height,"
        "brightness_mean,laplacian_var,processed_rel_path"
    )
    rows = [header]
    for i in range(6):
        rows.append(f"D1,a{i}.jpg,Healthy,healthy,ok,200,160,{100 + i},{20 + i},healthy/{i}.jpg")
        rows.append(f"D2,b{i}.jpg,Blast,blast,ok,300,200,{90 + i},{30 + i},blast/{i}.jpg")
    rows.append("D1,bad.jpg,Healthy,healthy,corrupt,0,0,0,0,")
    csv_path.write_text("\n".join(rows), encoding="utf-8")
    recs = eda.read_records([csv_path])
    assert eda.status_counts(recs) == {"ok": 12, "corrupt": 1}
    out = eda.make_figures(recs, tmp_path / "figs")
    assert len(out) == 5
    assert all(p.exists() and p.stat().st_size > 1000 for p in out)
    assert eda.make_figures([r for r in recs if r["status"] != "ok"], tmp_path / "f2") == []


# --- CLI end to end on a tiny synthetic manifest ----------------------------------------------------
def test_cli_verify_prepare_eda_end_to_end(tmp_path, monkeypatch):
    raw, ext, proc, eda_dir = (
        tmp_path / "raw",
        tmp_path / "ext",
        tmp_path / "proc",
        tmp_path / "eda",
    )
    cfg = tmp_path / "cfg"
    cfg.mkdir()
    src = tmp_path / "src"
    for i in range(3):
        jpg(src / "Healthy" / f"{i}.jpg", color=(i * 40, 120, 60))
        jpg(src / "Tungro" / f"{i}.jpg", color=(200, i * 30, 60))
    raw.mkdir()
    with zipfile.ZipFile(raw / "d.zip", "w") as zf:
        for f in src.rglob("*.jpg"):
            zf.write(f, f.relative_to(src).as_posix())
    manifest = {
        "datasets": {
            "D1": {
                "name": "synthetic",
                "licence": {"name": "CC BY 4.0"},
                "role": "test",
                "status": "training_source",
                "archives": [{"filename": "d.zip", "url": "https://data.mendeley.com/d"}],
                "classes_claimed_by_page": {"Healthy": 3, "Tungro": 3},
            },
            "D3": {
                "name": "later",
                "licence": {"name": "CC BY 4.0"},
                "role": "x",
                "status": "pending_download",
                "archives": [],
            },
        }
    }
    (cfg / "data_manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    labels = (cli.CONFIGS / "labels.yaml").read_text(encoding="utf-8")
    (cfg / "labels.yaml").write_text(labels, encoding="utf-8")
    overrides = {
        "CONFIGS": cfg,
        "RAW": raw,
        "EXTRACTED": ext,
        "PROCESSED": proc,
        "EDA_DIR": eda_dir,
        "LOCK": cfg / "lock.json",
        "ML": tmp_path,
    }
    for name, val in overrides.items():
        monkeypatch.setattr(cli, name, val)
    assert cli.main(["data", "verify"]) == 0
    verified = json.loads((tmp_path / "reports" / "data_verify.json").read_text())
    assert verified["D1/d.zip"]["sha256"]
    assert cli.main(["data", "prepare"]) == 0
    summary = json.loads((eda_dir / "summary_D1.json").read_text())
    assert summary["by_status"] == {"ok": 6}
    assert summary["page_vs_found"]["Healthy"]["difference"] == 0
    assert cli.main(["data", "eda"]) == 0
    assert (eda_dir / "class_counts_by_source.png").exists()
    # tamper -> prepare must abort (checksum lock, spec 9.4 step 1)
    (raw / "d.zip").write_bytes(b"tampered")
    with pytest.raises(Exception, match="differs"):
        cli.main(["data", "prepare"])
    assert cli.main(["data", "verify"]) == 2


def test_cli_missing_archive_and_unknown_dataset(tmp_path, monkeypatch, capsys):
    cfg = tmp_path / "cfg"
    cfg.mkdir()
    manifest = {
        "datasets": {
            "D1": {
                "name": "x",
                "licence": {"name": "L"},
                "role": "r",
                "status": "training_source",
                "archives": [{"filename": "gone.zip"}],
            }
        }
    }
    (cfg / "data_manifest.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")
    labels = (cli.CONFIGS / "labels.yaml").read_text(encoding="utf-8")
    (cfg / "labels.yaml").write_text(labels, encoding="utf-8")
    for name, val in {
        "CONFIGS": cfg,
        "RAW": tmp_path / "raw",
        "EDA_DIR": tmp_path / "eda",
        "LOCK": cfg / "l.json",
        "ML": tmp_path,
    }.items():
        monkeypatch.setattr(cli, name, val)
    assert cli.main(["data", "verify"]) == 1
    assert "MISSING" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        cli.main(["data", "verify", "--dataset", "NOPE"])
    assert cli.main(["data", "download"]) == 0  # no URL -> skipped, not fatal
    with pytest.raises(SystemExit, match="download"):
        cli.main(["data", "prepare"])
    with pytest.raises(SystemExit, match="prepare"):
        cli.main(["data", "eda"])
