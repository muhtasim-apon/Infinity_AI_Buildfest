"""End-to-end scan / alert API over real Postgres + Redis with the Llama call stubbed.

Covers: auth + CSRF required, upload validation, idempotency, abstain path, cited advice,
RLS isolation through the API, outbreak draft -> reviewer approval -> farmer sees it, audit row.
"""

from __future__ import annotations

import io
import uuid
from typing import Any

from PIL import Image

from app.services.llm import LlmReply, LlmUnavailableError
from tests.api.identity_support import ORIGIN, Api, needs_services, sql

pytestmark = needs_services


def leaf_jpeg(seed: int = 0) -> bytes:
    img = Image.new("RGB", (640, 480))
    px = img.load()
    for x in range(640):
        for y in range(480):
            px[x, y] = (40 + (x * 7 + seed) % 90, 110 + (y * 5) % 120, 40 + ((x + y) * 3) % 60)
    out = io.BytesIO()
    img.save(out, format="JPEG")
    return out.getvalue()


class StubLlm:
    def __init__(self, vision: Any = None, advice: Any = None) -> None:
        self.vision_answer = vision
        self.advice_answer = advice
        self.vision_calls = 0

    async def vision(self, jpeg: bytes) -> LlmReply:
        self.vision_calls += 1
        if isinstance(self.vision_answer, Exception):
            raise self.vision_answer
        return LlmReply(self.vision_answer, "stub-model", 5)

    async def advice(self, disease_bn: str, sources: list[tuple[str, str]]) -> LlmReply:
        if self.advice_answer is None:
            raise LlmUnavailableError("stub")
        return LlmReply(self.advice_answer(sources), "stub-model", 5)


def stub(api: Api, **kw: Any) -> StubLlm:
    s = StubLlm(**kw)
    api.shared.app.state.container.scans.llm = s  # type: ignore[attr-defined]
    return s


def demo(api: Api, role: str) -> Api:
    other = api.spawn()
    r = other.post("/api/v1/demo/session", {"role": role, "captcha": "bypass"})
    assert r.status_code == 201, r.text
    other.refresh_csrf()
    return other


def upload(
    api: Api, data: bytes, *, key: str | None = None, region: str = "BD-C", csrf: bool = True
):  # type: ignore[no-untyped-def]
    headers = {"Origin": ORIGIN, "Idempotency-Key": key or uuid.uuid4().hex}
    if csrf:
        headers["X-CSRF-Token"] = api.csrf
    return api.c._send(
        "post",
        "/api/v1/scans",
        files={"image": ("leaf.jpg", data, "image/jpeg")},
        data={"region_code": region},
        headers=headers,
    )


BLAST = {"crop": "rice", "disease": "rice_blast", "confidence": 0.91, "image_quality": "good"}


def cited_advice(sources: list[tuple[str, str]]) -> dict[str, Any]:
    cid = next(c for c, t in sources if "৫ কেজি পটাশ" in t)
    return {
        "summary_bn": "এটি ব্লাস্ট রোগ হতে পারে।",
        "steps_bn": ["রোগের প্রাথমিক অবস্থায় বিঘা প্রতি ৫ কেজি পটাশ সার দিন।"],
        "chemical": None,
        "safety_bn": "x",
        "citations": [cid],
    }


def test_scan_requires_session_and_csrf(app_client: Api) -> None:
    assert upload(app_client, leaf_jpeg()).status_code == 401
    farmer = demo(app_client, "DEMO_FARMER")
    assert upload(farmer, leaf_jpeg(), csrf=False).status_code == 403


def test_staff_cannot_scan(app_client: Api) -> None:
    stub(app_client, vision=BLAST)
    reviewer = demo(app_client, "DEMO_REVIEWER")
    assert upload(reviewer, leaf_jpeg()).status_code == 403


def test_diagnosis_with_cited_bangla_advice_and_idempotency(app_client: Api) -> None:
    s = stub(app_client, vision=BLAST, advice=cited_advice)
    farmer = demo(app_client, "DEMO_FARMER")
    key = uuid.uuid4().hex
    r = upload(farmer, leaf_jpeg(), key=key)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "diagnosed" and body["disease"] == "rice_blast"
    assert body["confidence_band"] == "high" and "confidence" not in body
    assert body["advice_source"] == "llm" and body["citations"][0]["publisher"].startswith(
        "Bangladesh"
    )
    assert body["reviewed_by_agronomist"] is False and body["synthetic"] is True
    again = upload(farmer, leaf_jpeg(seed=9), key=key)  # same key => same result, no new model call
    assert again.json()["id"] == body["id"] and s.vision_calls == 1
    history = farmer.get("/api/v1/scans").json()["scans"]
    assert [h["id"] for h in history].count(body["id"]) == 1  # the demo farmer is shared
    # the photo itself is never stored
    cols = sql("SELECT column_name FROM information_schema.columns WHERE table_name='scans'")
    assert not any("image" in c[0] and c[0] != "image_sha256" for c in cols)


def test_llm_down_gives_not_sure_never_500(app_client: Api) -> None:
    stub(app_client, vision=LlmUnavailableError("timeout"))
    farmer = demo(app_client, "DEMO_FARMER")
    r = upload(farmer, leaf_jpeg())
    assert r.status_code == 201
    assert (r.json()["status"], r.json()["reason"]) == ("not_sure", "model_error")


def test_low_confidence_abstains_and_advice_falls_back(app_client: Api) -> None:
    stub(app_client, vision={**BLAST, "confidence": 0.4})
    farmer = demo(app_client, "DEMO_FARMER")
    assert upload(farmer, leaf_jpeg()).json()["reason"] == "low_confidence"
    stub(app_client, vision=BLAST, advice=None)  # advice model down => verbatim static card
    body = upload(farmer, leaf_jpeg()).json()
    assert body["advice_source"] == "static_card" and body["citations"]


def test_dark_photo_abstains_without_calling_the_model(app_client: Api) -> None:
    s = stub(app_client, vision=BLAST)
    farmer = demo(app_client, "DEMO_FARMER")
    out = io.BytesIO()
    Image.new("RGB", (640, 480), (3, 3, 3)).save(out, format="JPEG")
    body = upload(farmer, out.getvalue()).json()
    assert (body["status"], body["reason"]) == ("not_sure", "poor_image") and s.vision_calls == 0


def test_upload_validation(app_client: Api) -> None:
    stub(app_client, vision=BLAST)
    farmer = demo(app_client, "DEMO_FARMER")
    assert upload(farmer, b"%PDF-1.4 not an image").status_code == 415
    assert upload(farmer, leaf_jpeg(), region="23.8,90.4").status_code == 422
    assert upload(farmer, leaf_jpeg(), key="short").status_code == 422
    big = b"\xff\xd8\xff" + b"0" * (6 * 1024 * 1024)
    assert upload(farmer, big).status_code == 413


def test_other_users_scan_is_404(app_client: Api) -> None:
    stub(app_client, vision=BLAST, advice=cited_advice)
    a = demo(app_client, "DEMO_FARMER")
    sid = upload(a, leaf_jpeg()).json()["id"]
    assert a.get(f"/api/v1/scans/{sid}").status_code == 200
    reviewer = demo(app_client, "DEMO_REVIEWER")
    assert reviewer.get(f"/api/v1/scans/{sid}").status_code == 403
    assert a.get("/api/v1/scans/not-a-uuid").status_code == 404
    assert a.get(f"/api/v1/scans/{uuid.uuid4()}").status_code == 404


def test_outbreak_draft_needs_reviewer_approval(app_client: Api) -> None:
    sql("DELETE FROM outbreak_alerts WHERE tenant_id='demo'")
    sql("DELETE FROM scans WHERE tenant_id='demo'")
    stub(app_client, vision={**BLAST, "disease": "tungro"}, advice=None)
    farmer = demo(app_client, "DEMO_FARMER")
    for i in range(3):
        assert upload(farmer, leaf_jpeg(seed=i), region="BD-G").status_code == 201
    assert farmer.get("/api/v1/alerts").json()["alerts"] == []  # draft is invisible to farmers
    reviewer = demo(app_client, "DEMO_REVIEWER")
    drafts = reviewer.get("/api/v1/alerts").json()["alerts"]
    assert len(drafts) == 1 and drafts[0]["status"] == "draft" and drafts[0]["case_count"] == 3
    aid = drafts[0]["id"]
    assert farmer.post(f"/api/v1/alerts/{aid}/decision", {"decision": "approve"}).status_code == 403
    assert reviewer.post(f"/api/v1/alerts/{aid}/decision", {"decision": "maybe"}).status_code == 422
    ok = reviewer.post(f"/api/v1/alerts/{aid}/decision", {"decision": "approve"})
    assert ok.status_code == 200 and ok.json()["status"] == "approved"
    assert (
        reviewer.post(f"/api/v1/alerts/{aid}/decision", {"decision": "reject"}).status_code == 409
    )
    seen = farmer.get("/api/v1/alerts").json()["alerts"]
    assert [a["id"] for a in seen] == [aid] and seen[0]["unverified"] is True
    audit = sql("SELECT action FROM audit_log WHERE object_id=%s", (aid,))
    assert audit == [("alert.approved",)]


def test_kb_sources_is_public_and_honest(app_client: Api) -> None:
    body = app_client.get("/api/v1/kb/sources").json()
    assert len(body["sources"]) == 9 and body["excluded"]
    assert "not calibrated" in body["limits"]["confidence"]
    assert body["limits"]["outbreak_rule"]["needs_reviewer_approval"] is True
