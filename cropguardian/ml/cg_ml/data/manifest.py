"""Dataset manifest + checksums (spec 9.4 step 1).

`ml/configs/data_manifest.yaml` is declarative: archive names, URLs, sizes, and the SHA-256 values
PUBLISHED by the data host. Our own computed hashes go to `ml/configs/data_lock.json` the first
time an archive is verified; every later run aborts if the bytes differ from the lock.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml

ALLOWED_DOWNLOAD_HOSTS = frozenset({"data.mendeley.com", "codeload.github.com", "github.com"})
_CHUNK = 1 << 20


class ManifestError(ValueError):
    """The manifest is malformed or a checksum rule was violated."""


class ChecksumMismatchError(RuntimeError):
    """Archive bytes do not match the published hash or the previously recorded lock."""


@dataclass(frozen=True)
class Archive:
    dataset: str
    filename: str
    url: str | None
    size_bytes: int | None
    sha256_published: str | None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def validate_download_url(url: str) -> str:
    """Only https and allow-listed hosts (SSRF / supply-chain hygiene)."""
    parts = urlsplit(url)
    if parts.scheme != "https" or (parts.hostname or "") not in ALLOWED_DOWNLOAD_HOSTS:
        raise ManifestError(f"download URL not allowed: {parts.scheme}://{parts.hostname}")
    return url


def load_manifest(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "datasets" not in data:
        raise ManifestError("manifest must contain a top-level 'datasets' mapping")
    for ds_id, ds in data["datasets"].items():
        for key in ("name", "licence", "role", "archives", "status"):
            if key not in ds:
                raise ManifestError(f"{ds_id}: missing '{key}'")
        if not ds["licence"].get("name"):
            raise ManifestError(f"{ds_id}: licence must be recorded before use (spec 9.2)")
        for a in ds["archives"]:
            sha = a.get("sha256_published")
            if sha is not None and (len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha)):
                raise ManifestError(f"{ds_id}/{a.get('filename')}: sha256_published is not 64 hex chars")
            if a.get("url"):
                validate_download_url(a["url"])
    return data


def archives(manifest: dict[str, Any], dataset: str | None = None) -> list[Archive]:
    out: list[Archive] = []
    for ds_id, ds in manifest["datasets"].items():
        if dataset and ds_id != dataset:
            continue
        for a in ds["archives"]:
            out.append(
                Archive(ds_id, a["filename"], a.get("url"), a.get("size_bytes"), a.get("sha256_published"))
            )
    return out


def load_lock(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ManifestError("lock file must be a JSON object")
    return {str(k): str(v) for k, v in data.items()}


def verify_archive(
    path: Path, archive: Archive, lock_path: Path, *, record: bool = True
) -> str:
    """Return the computed sha256 or raise ChecksumMismatchError.

    Rules: (1) must equal the host-published hash when one is known; (2) must equal our lock from a
    previous run; (3) if both pass and `record`, store it in the lock (first verification).
    """
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = sha256_file(path)
    key = f"{archive.dataset}/{archive.filename}"
    if archive.sha256_published and not hmac.compare_digest(actual, archive.sha256_published):
        raise ChecksumMismatchError(f"{key}: sha256 differs from the published hash")
    lock = load_lock(lock_path)
    if key in lock and not hmac.compare_digest(actual, lock[key]):
        raise ChecksumMismatchError(f"{key}: sha256 differs from the previous run (lock)")
    if record and key not in lock:
        lock[key] = actual
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return actual
