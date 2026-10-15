"""Upload sanitiser (threats T4, T10, T15).

Pipeline, in order — every step is a whitebox-tested branch (tests/whitebox/test_upload_sanitiser.py):
  1. size ≤ MAX_UPLOAD_MB                                  → else 413
  2. magic bytes ∈ {JPEG FF D8 FF, PNG 89 50 4E 47, WebP RIFF....WEBP} → else 415
  3. Pillow open with Image.MAX_IMAGE_PIXELS = 25_000_000; verify(); reopen → else 422
  4. min side ≥ 64 px                                       → else 422
  5. convert RGB, re-encode JPEG q=90 → drops EXIF/ICC/scripts, defeats polyglots
"""

from __future__ import annotations

from dataclasses import dataclass

ALLOWED_MAGIC: dict[str, bytes] = {
    "jpeg": b"\xff\xd8\xff",
    "png": b"\x89PNG\r\n\x1a\n",
    "webp": b"RIFF",  # plus b"WEBP" at offset 8
}


class UploadRejected(Exception):
    def __init__(self, status: int, code: str) -> None:
        super().__init__(code)
        self.status = status
        self.code = code


@dataclass(frozen=True)
class CleanImage:
    jpeg_bytes: bytes
    width: int
    height: int
    sha256: str


def sanitise(raw: bytes, max_bytes: int) -> CleanImage:
    """Run the pipeline above. Raises ``UploadRejected(status, code)``."""
    raise NotImplementedError
