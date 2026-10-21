import hashlib
import json
from pathlib import Path

import pytest
import yaml

from cg_ml.data.manifest import (
    Archive,
    ChecksumMismatchError,
    ManifestError,
    archives,
    load_manifest,
    sha256_file,
    validate_download_url,
    verify_archive,
)

REPO_MANIFEST = Path(__file__).resolve().parents[1] / "configs" / "data_manifest.yaml"


def write(tmp_path: Path, body: dict) -> Path:
    p = tmp_path / "m.yaml"
    p.write_text(yaml.safe_dump(body), encoding="utf-8")
    return p


def ds(**over):
    base = {
        "name": "x", "licence": {"name": "CC BY 4.0"}, "role": "r", "status": "training_source",
        "archives": [{"filename": "a.zip", "url": "https://data.mendeley.com/a"}],
    }  # fmt: skip
    base.update(over)
    return base


def test_committed_manifest_is_valid_and_records_every_licence():
    m = load_manifest(REPO_MANIFEST)
    assert set(m["datasets"]) >= {"D1", "D2", "D3", "D4", "N1", "X1"}
    for k, v in m["datasets"].items():
        assert v["licence"]["name"], k


def test_d4_plantvillage_is_blocked_until_licence_verified():
    m = load_manifest(REPO_MANIFEST)
    assert m["datasets"]["D4"]["status"] == "blocked_licence_unconfirmed"
    assert m["datasets"]["D4"]["archives"] == []


def test_published_hashes_in_manifest_are_64_hex():
    m = load_manifest(REPO_MANIFEST)
    for a in archives(m):
        if a.sha256_published:
            assert len(a.sha256_published) == 64


@pytest.mark.parametrize(
    "url",
    ["http://data.mendeley.com/x", "https://evil.example.com/x", "ftp://data.mendeley.com/x",
     "https://data.mendeley.com.evil.com/x", "file:///etc/passwd"],
)  # fmt: skip
def test_download_url_allow_list(url):
    with pytest.raises(ManifestError):
        validate_download_url(url)


def test_missing_licence_is_refused(tmp_path):
    body = {"datasets": {"D9": ds(licence={})}}
    with pytest.raises(ManifestError, match="licence"):
        load_manifest(write(tmp_path, body))


def test_bad_hash_and_missing_keys_refused(tmp_path):
    bad = ds(archives=[{"filename": "a.zip", "sha256_published": "xyz"}])
    with pytest.raises(ManifestError):
        load_manifest(write(tmp_path, {"datasets": {"D9": bad}}))
    with pytest.raises(ManifestError):
        load_manifest(write(tmp_path, {"datasets": {"D9": {"name": "x"}}}))
    with pytest.raises(ManifestError):
        load_manifest(write(tmp_path, {"nope": 1}))


def test_sha256_file_matches_hashlib(tmp_path):
    f = tmp_path / "f.bin"
    f.write_bytes(b"crop guardian" * 1000)
    assert sha256_file(f) == hashlib.sha256(b"crop guardian" * 1000).hexdigest()


def test_verify_records_lock_then_detects_tampering(tmp_path):
    f = tmp_path / "a.zip"
    f.write_bytes(b"v1")
    lock = tmp_path / "lock.json"
    arc = Archive("D1", "a.zip", None, None, None)
    first = verify_archive(f, arc, lock)
    assert json.loads(lock.read_text())["D1/a.zip"] == first
    assert verify_archive(f, arc, lock) == first  # stable on re-run
    f.write_bytes(b"v2-tampered")
    with pytest.raises(ChecksumMismatchError, match="previous run"):
        verify_archive(f, arc, lock)


def test_verify_rejects_published_hash_mismatch(tmp_path):
    f = tmp_path / "a.zip"
    f.write_bytes(b"data")
    arc = Archive("D1", "a.zip", None, None, "0" * 64)
    with pytest.raises(ChecksumMismatchError, match="published"):
        verify_archive(f, arc, tmp_path / "lock.json")
    assert not (tmp_path / "lock.json").exists()  # a bad archive is never recorded


def test_verify_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        verify_archive(
            tmp_path / "nope.zip", Archive("D1", "nope.zip", None, None, None), tmp_path / "l"
        )
