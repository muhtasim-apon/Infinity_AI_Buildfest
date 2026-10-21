"""Safe archive extraction (zip-slip, symlinks, decompression bombs) - spec 16.7/16.11 mindset.

Dataset archives come from third parties, so they are treated as untrusted: every member path is
checked before anything is written, symlinks are refused, and total/ratio limits stop bombs.
RAR is extracted with the external 7-Zip/unrar binary (no shell, fixed arguments) and the result
is re-validated.
"""

from __future__ import annotations

import shutil
import stat
import subprocess
import zipfile
from pathlib import Path

MAX_TOTAL_BYTES = 8 * 1024**3
MAX_RATIO = 200  # uncompressed/compressed per member
MAX_MEMBERS = 200_000


class UnsafeArchiveError(RuntimeError):
    """The archive contains a dangerous member or exceeds limits."""


def _is_inside(base: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(base.resolve())
    except ValueError:
        return False
    return True


def extract_zip(archive: Path, dest: Path) -> int:
    dest.mkdir(parents=True, exist_ok=True)
    count = 0
    total = 0
    with zipfile.ZipFile(archive) as zf:
        infos = zf.infolist()
        if len(infos) > MAX_MEMBERS:
            raise UnsafeArchiveError("too many members")
        for info in infos:
            name = info.filename
            if name.startswith(("/", "\\")) or ".." in Path(name).parts or ":" in name.split("/")[0]:
                raise UnsafeArchiveError(f"unsafe member path: {name!r}")
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise UnsafeArchiveError(f"symlink member refused: {name!r}")
            target = dest / name
            if not _is_inside(dest, target):
                raise UnsafeArchiveError(f"member escapes destination: {name!r}")
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            total += info.file_size
            if total > MAX_TOTAL_BYTES:
                raise UnsafeArchiveError("uncompressed size limit exceeded")
            if info.compress_size and info.file_size / info.compress_size > MAX_RATIO and info.file_size > 10**7:
                raise UnsafeArchiveError(f"suspicious compression ratio: {name!r}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, target.open("wb") as out:
                shutil.copyfileobj(src, out, 1 << 20)
            count += 1
    return count


def find_rar_tool() -> str | None:
    for candidate in ("7z", "7za", "unrar"):
        found = shutil.which(candidate)
        if found:
            return found
    for path in (r"C:\Program Files\7-Zip\7z.exe", r"C:\Program Files (x86)\7-Zip\7z.exe"):
        if Path(path).exists():
            return path
    return None


def extract_rar(archive: Path, dest: Path) -> int:
    tool = find_rar_tool()
    if tool is None:
        raise UnsafeArchiveError("no RAR extractor found (install 7-Zip or unrar)")
    dest.mkdir(parents=True, exist_ok=True)
    if Path(tool).name.lower().startswith("unrar"):
        cmd = [tool, "x", "-y", "-idq", str(archive), str(dest) + "/"]
    else:
        cmd = [tool, "x", "-y", f"-o{dest}", str(archive)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, check=False)  # noqa: S603
    if proc.returncode != 0:
        raise UnsafeArchiveError(f"extractor failed ({proc.returncode})")
    count = 0
    for path in dest.rglob("*"):
        if path.is_symlink() or not _is_inside(dest, path):
            raise UnsafeArchiveError(f"unsafe entry after extraction: {path}")
        if path.is_file():
            count += 1
    return count


def extract(archive: Path, dest: Path) -> int:
    suffix = archive.suffix.lower()
    if suffix == ".zip":
        return extract_zip(archive, dest)
    if suffix == ".rar":
        return extract_rar(archive, dest)
    raise UnsafeArchiveError(f"unsupported archive type: {suffix}")
