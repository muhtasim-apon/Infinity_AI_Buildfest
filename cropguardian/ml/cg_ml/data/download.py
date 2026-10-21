"""Resumable downloads with an https + host allow-list and size/timeouts (spec 9.4 step 1)."""

from __future__ import annotations

import urllib.request
from pathlib import Path

from cg_ml.data.manifest import Archive, validate_download_url

_CHUNK = 1 << 20
_TIMEOUT_S = 60


def download(archive: Archive, dest_dir: Path) -> Path:
    """Download `archive` into `dest_dir`, resuming a partial file. Does not verify the hash."""
    if not archive.url:
        raise ValueError(f"{archive.dataset}/{archive.filename}: no URL in the manifest")
    validate_download_url(archive.url)
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / archive.filename
    if "/" in archive.filename or "\\" in archive.filename or archive.filename.startswith("."):
        raise ValueError("unsafe archive filename")
    have = target.stat().st_size if target.exists() else 0
    if archive.size_bytes and have == archive.size_bytes:
        return target
    if archive.size_bytes and have > archive.size_bytes:
        raise ValueError(f"{target.name}: local file is larger than the expected size; delete it")
    request = urllib.request.Request(archive.url, headers={"User-Agent": "cg-ml/0.1"})  # noqa: S310
    if have:
        request.add_header("Range", f"bytes={have}-")
    with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as resp:  # noqa: S310
        mode = "ab" if have and resp.status == 206 else "wb"
        with target.open(mode) as out:
            while chunk := resp.read(_CHUNK):
                out.write(chunk)
    return target
