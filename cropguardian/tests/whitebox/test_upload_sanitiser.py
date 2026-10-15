"""Whitebox: app/security/upload.py — every pipeline step (threats T4, T10, T15)."""

import pytest

pytestmark = pytest.mark.skip("stub — implement with app.security.upload")


@pytest.mark.parametrize(
    "fixture, status, code",
    [
        ("valid.jpg", None, None),
        ("valid.png", None, None),
        ("valid.webp", None, None),
        ("empty.bin", 415, "unsupported_type"),
        ("over_5mb.jpg", 413, "too_large"),
        ("exactly_5mb.jpg", None, None),                 # boundary: inclusive
        ("html_renamed.jpg", 415, "unsupported_type"),    # wrong magic bytes
        ("svg_renamed.png", 415, "unsupported_type"),
        ("truncated.jpg", 422, "invalid_image"),
        ("decompression_bomb.png", 422, "invalid_image"), # exceeds MAX_IMAGE_PIXELS
        ("tiny_32px.jpg", 422, "invalid_image"),          # min side < 64
        ("jpeg_with_appended_zip.jpg", None, None),        # polyglot: accepted but re-encoded
    ],
)
def test_sanitise(fixture, status, code):
    """status None → returns CleanImage; else raises UploadRejected(status, code)."""


def test_exif_gps_removed_after_reencode():
    """fixture with GPS EXIF → output has no EXIF block at all."""


def test_output_is_always_jpeg_rgb():
    """PNG with alpha / CMYK JPEG → RGB JPEG."""
