import io
import stat
import zipfile
from pathlib import Path

import pytest

from cg_ml.data import extract as ex
from cg_ml.data.extract import UnsafeArchiveError, extract_zip


def make_zip(path: Path, members: dict[str, bytes], symlink: str | None = None) -> Path:
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)
        if symlink:
            info = zipfile.ZipInfo(symlink)
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            zf.writestr(info, "/etc/passwd")
    return path


def test_extracts_normal_archive(tmp_path):
    z = make_zip(tmp_path / "a.zip", {"Healthy/a.jpg": b"x", "Blast/b.jpg": b"y"})
    assert extract_zip(z, tmp_path / "out") == 2
    assert (tmp_path / "out" / "Healthy" / "a.jpg").read_bytes() == b"x"


@pytest.mark.parametrize("name", ["../evil.txt", "a/../../evil.txt", "/abs.txt", "C:/win.txt"])
def test_zip_slip_and_absolute_paths_refused(tmp_path, name):
    z = make_zip(tmp_path / "a.zip", {name: b"x"})
    with pytest.raises(UnsafeArchiveError):
        extract_zip(z, tmp_path / "out")
    assert not (tmp_path / "evil.txt").exists()


def test_symlink_member_refused(tmp_path):
    z = make_zip(tmp_path / "a.zip", {"ok.txt": b"x"}, symlink="link")
    with pytest.raises(UnsafeArchiveError, match="symlink"):
        extract_zip(z, tmp_path / "out")


def test_decompression_bomb_ratio_refused(tmp_path, monkeypatch):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("zeros.bin", b"\0" * 30_000_000)  # compresses ~1000:1
    p = tmp_path / "bomb.zip"
    p.write_bytes(buf.getvalue())
    with pytest.raises(UnsafeArchiveError, match="ratio"):
        extract_zip(p, tmp_path / "out")


def test_total_size_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(ex, "MAX_TOTAL_BYTES", 10)
    z = make_zip(tmp_path / "a.zip", {"a.bin": b"x" * 20})
    with pytest.raises(UnsafeArchiveError, match="size"):
        extract_zip(z, tmp_path / "out")


def test_unsupported_type_and_corrupt_zip(tmp_path):
    with pytest.raises(UnsafeArchiveError, match="unsupported"):
        ex.extract(tmp_path / "a.tar.gz", tmp_path / "o")
    bad = tmp_path / "bad.zip"
    bad.write_bytes(b"not a zip")
    with pytest.raises(zipfile.BadZipFile):
        extract_zip(bad, tmp_path / "o")
