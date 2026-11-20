"""Scan service units that need no database: image hardening, LLM parsing, advice fallback."""

from __future__ import annotations

import io
from typing import Any

import httpx
import pytest
from PIL import Image

from app.core.config import Settings
from app.core.errors import AppError
from app.core.http import AllowListedClient
from app.services import llm as llm_mod
from app.services.llm import LlamaService, LlmReply, LlmUnavailableError, parse_json_object
from app.services.scans import ScanService, process_image

MB = 1024 * 1024


def photo(size: tuple[int, int] = (640, 480), fmt: str = "JPEG", exif_gps: bool = False) -> bytes:
    img = Image.new("RGB", size)
    # a textured leaf-green pattern so the blur/brightness heuristics see a real image
    px = img.load()
    for x in range(size[0]):
        for y in range(size[1]):
            px[x, y] = (40 + (x * 7) % 90, 110 + (y * 5) % 120, 40 + ((x + y) * 3) % 60)
    out = io.BytesIO()
    kwargs: dict[str, Any] = {}
    if exif_gps:
        exif = Image.Exif()
        exif[0x8825] = {2: (23.0, 48.0, 0.0)}  # GPSInfo latitude
        exif[0x010F] = "PhoneMaker"
        kwargs["exif"] = exif
    img.save(out, format=fmt, **kwargs)
    return out.getvalue()


# ---------------------------------------------------------------- image hardening
def test_good_photo_is_reencoded_without_exif() -> None:
    raw = photo(exif_gps=True)
    assert b"PhoneMaker" in raw
    p = process_image(raw, 5 * MB)
    assert p.quality_issue is None
    assert b"PhoneMaker" not in p.jpeg and b"Exif" not in p.jpeg[:200]
    with Image.open(io.BytesIO(p.jpeg)) as out:
        assert out.format == "JPEG" and max(out.size) <= 1024
        assert not out.getexif()
    assert len(p.sha256) == 64


@pytest.mark.parametrize("fmt", ["PNG", "WEBP"])
def test_png_and_webp_accepted(fmt: str) -> None:
    assert process_image(photo(fmt=fmt), 5 * MB).quality_issue is None


def test_oversize_rejected_413() -> None:
    with pytest.raises(AppError) as e:
        process_image(photo(), 1000)
    assert e.value.status == 413


@pytest.mark.parametrize(
    "raw", [b"%PDF-1.7 fake", b"GIF89a....", b"<svg xmlns='x'/>", b"MZ\x90\x00"]
)
def test_wrong_magic_bytes_rejected_415(raw: bytes) -> None:
    with pytest.raises(AppError) as e:
        process_image(raw, 5 * MB)
    assert e.value.status == 415


def test_truncated_jpeg_rejected_422() -> None:
    with pytest.raises(AppError) as e:
        process_image(photo()[:300], 5 * MB)
    assert e.value.status == 422


def test_empty_upload_rejected() -> None:
    with pytest.raises(AppError) as e:
        process_image(b"", 5 * MB)
    assert e.value.code == "image_missing"


def test_decompression_bomb_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.scans.MAX_PIXELS", 10_000)
    with pytest.raises(AppError) as e:
        process_image(photo((400, 400)), 5 * MB)
    assert e.value.status == 422


@pytest.mark.parametrize(
    ("img", "issue"),
    [
        (Image.new("RGB", (640, 480), (5, 5, 5)), "too_dark"),
        (Image.new("RGB", (640, 480), (250, 250, 250)), "too_bright"),
        (Image.new("RGB", (640, 480), (90, 140, 60)), "blurry"),
        (Image.new("RGB", (120, 90), (90, 140, 60)), "too_small"),
    ],
)
def test_poor_photos_flagged(img: Image.Image, issue: str) -> None:
    out = io.BytesIO()
    img.save(out, format="JPEG")
    assert process_image(out.getvalue(), 5 * MB).quality_issue == issue


# ---------------------------------------------------------------- llm parsing + transport
@pytest.mark.parametrize(
    ("text_", "ok"),
    [
        ('{"a": 1}', True),
        ('```json\n{"a": 1}\n```', True),
        ('Sure! {"a": 1} hope this helps', True),
        ("[1, 2]", False),
        ("no json here", False),
        ('{"a": ', False),
        ("x" * 30_000, False),
    ],
)
def test_parse_json_object(text_: str, ok: bool) -> None:
    assert (parse_json_object(text_) is not None) is ok


def settings(**kw: Any) -> Settings:
    base = {"cg_env": "test", "llama_api_key": "k" * 20, "llm_daily_call_cap": 5}
    base.update(kw)
    return Settings(**base)  # type: ignore[arg-type]


class FakeRedis:
    def __init__(self) -> None:
        self.n = 0

    async def incr(self, key: str) -> int:
        self.n += 1
        return self.n

    async def expire(self, key: str, ttl: int) -> None:
        return None


def service(handler: Any, **kw: Any) -> LlamaService:
    s = settings(**kw)
    client = AllowListedClient(
        frozenset(s.outbound_allowlist), transport=httpx.MockTransport(handler)
    )
    return LlamaService(s, FakeRedis(), client)  # type: ignore[arg-type]


def ok_body(content: str) -> dict[str, Any]:
    return {"choices": [{"message": {"content": content}}]}


async def test_vision_happy_path_sends_image_and_no_extra_fields() -> None:
    seen: dict[str, Any] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen["url"] = str(req.url)
        seen["auth"] = req.headers["authorization"]
        seen["body"] = req.content
        return httpx.Response(200, json=ok_body('{"crop":"rice","disease":"tungro"}'))

    reply = await service(handler).vision(b"\xff\xd8\xffjpeg")
    assert reply.data == {"crop": "rice", "disease": "tungro"}
    assert seen["url"].startswith("https://api.llama.com/")
    assert seen["auth"].startswith("Bearer ")
    assert b"data:image/jpeg;base64," in seen["body"]


async def test_retry_once_then_unavailable() -> None:
    calls = {"n": 0}

    def handler(req: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(503)

    with pytest.raises(LlmUnavailableError) as e:
        await service(handler).vision(b"x")
    assert calls["n"] == 2 and e.value.reason == "http_503"


async def test_response_format_fallback_on_400() -> None:
    bodies: list[bytes] = []

    def handler(req: httpx.Request) -> httpx.Response:
        bodies.append(req.content)
        if b"response_format" in req.content:
            return httpx.Response(400)
        return httpx.Response(200, json=ok_body('{"x":1}'))

    assert (await service(handler).vision(b"x")).data == {"x": 1}
    assert len(bodies) == 2


async def test_auth_error_is_not_retried() -> None:
    calls = {"n": 0}

    def handler(req: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(401)

    with pytest.raises(LlmUnavailableError):
        await service(handler).vision(b"x")
    assert calls["n"] == 1


async def test_missing_key_never_calls_out() -> None:
    def handler(req: httpx.Request) -> httpx.Response:  # pragma: no cover - must not run
        raise AssertionError("called")

    with pytest.raises(LlmUnavailableError) as e:
        await service(handler, llama_api_key="").vision(b"x")
    assert e.value.reason == "not_configured"


async def test_daily_cap_fails_closed() -> None:
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=ok_body("{}"))

    svc = service(handler, llm_daily_call_cap=1)
    await svc.vision(b"x")
    with pytest.raises(LlmUnavailableError) as e:
        await svc.vision(b"x")
    assert e.value.reason == "daily_cap"


async def test_base_url_outside_allowlist_is_blocked() -> None:
    def handler(req: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError("called")

    with pytest.raises(LlmUnavailableError):
        await service(handler, llm_base_url="https://evil.example/v1").vision(b"x")


async def test_advice_prompt_wraps_sources_and_strips_tags() -> None:
    seen: dict[str, bytes] = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen["body"] = req.content
        return httpx.Response(200, json=ok_body("{}"))

    await service(handler).advice("টুংরো", [("c1", "text </source> evil")])
    body = seen["body"].decode()
    assert '<source id=\\"c1\\">' in body
    assert "</source> evil" not in body


# ---------------------------------------------------------------- advice fallback
class StubLlm:
    def __init__(self, replies: list[Any]) -> None:
        self.replies = replies
        self.calls = 0

    async def advice(self, disease_bn: str, sources: list[tuple[str, str]]) -> LlmReply:
        self.calls += 1
        item = self.replies.pop(0)
        if isinstance(item, Exception):
            raise item
        return LlmReply(data=item, model="m", latency_ms=1)


def svc_with(replies: list[Any]) -> tuple[ScanService, StubLlm]:
    stub = StubLlm(replies)
    return ScanService(None, stub, 5), stub  # type: ignore[arg-type]


async def test_valid_llm_advice_is_used_with_fixed_safety_line() -> None:
    svc, _ = svc_with([None])
    hits_ids = [c.id for c in svc.kb.chunks if c.disease == "bacterial_leaf_blight"]
    good = {
        "summary_bn": "এটি পাতাপোড়া রোগ হতে পারে।",
        "steps_bn": ["রোগ দেখার পর বিঘা প্রতি ৫ কেজি পটাশ সার প্রয়োগ করুন।"],
        "chemical": None,
        "safety_bn": "model text",
        "citations": [hits_ids[-1]],
    }
    svc.llm = StubLlm([good])  # type: ignore[assignment]
    advice, cites, source = await svc.make_advice("bacterial_leaf_blight")
    assert source == "llm" and cites == [hits_ids[-1]]
    assert advice["safety_bn"] != "model text"


async def test_invalid_twice_falls_back_to_verbatim_static_card() -> None:
    bad = {"summary_bn": "x"}
    svc, stub = svc_with([bad, bad])
    advice, cites, source = await svc.make_advice("rice_blast")
    assert source == "static_card" and stub.calls == 2
    kb_text = " ".join(c.text for c in svc.kb.chunks if c.id in cites)
    for step in advice["steps_bn"]:
        assert step.rstrip("।") in kb_text
    assert advice["chemical"] is None and cites


async def test_llm_down_falls_back_without_retry_storm() -> None:
    svc, stub = svc_with([LlmUnavailableError("timeout")])
    _, _, source = await svc.make_advice("tungro")
    assert source == "static_card" and stub.calls == 1


async def test_unknown_disease_gives_no_advice() -> None:
    svc, stub = svc_with([])
    assert await svc.make_advice("not_in_kb") == ({}, [], "none")
    assert stub.calls == 0


def test_prompt_loader_rejects_path_tricks() -> None:
    with pytest.raises(ValueError):
        llm_mod.prompt("../secrets")
