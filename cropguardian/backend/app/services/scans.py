"""Scan -> diagnosis -> cited advice, and human-approved outbreak alerts (Gantt P2 + P3).

Pipeline for POST /api/v1/scans:
  1. validate + harden the upload (size, magic bytes, decode, decompression-bomb guard, EXIF/GPS
     strip by re-encoding to JPEG, SHA-256 of the re-encoded bytes);
  2. cheap local photo-quality check; a poor photo abstains WITHOUT calling the model;
  3. Llama vision -> JSON -> `domain.decision.decide` (abstain below threshold, rice only);
  4. diagnosed -> `domain.kb_search.search` (<= 8 BRRI chunks) -> Llama Bangla advice ->
     `domain.advice_validator.validate`; one retry, then the static card built verbatim from chunks;
  5. store the row (no image bytes: D-032) and refresh the outbreak draft for that disease+division.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
from dataclasses import dataclass
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

from PIL import Image, ImageFilter, ImageOps, ImageStat, UnidentifiedImageError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.authz import Principal, Resource, authorize
from app.core.clock import utcnow
from app.core.errors import AppError
from app.core.logging import get_logger
from app.core.tenancy import db_context_for
from app.db.session import session_scope, system_scope
from app.domain import advice_validator, decision, kb_search, outbreak_rules
from app.services import events
from app.services.llm import (
    ADVICE_PROMPT_VERSION,
    VISION_PROMPT_VERSION,
    LlamaService,
    LlmUnavailableError,
)

KB_FILE = Path(__file__).resolve().parent.parent / "data" / "kb_brri_rice.json"
MAX_PIXELS = 40_000_000  # decompression-bomb guard
MAX_SIDE = 1024  # re-encoded size sent to the model
MIN_SIDE = 200
_IDEM = re.compile(r"^[A-Za-z0-9_-]{8,80}$")
_MAGIC = (b"\xff\xd8\xff", b"\x89PNG\r\n\x1a\n")
log = get_logger("cg.scans")

SAFETY_BN = (
    "কোনো রাসায়নিক ব্যবহারের আগে আপনার উপজেলা কৃষি অফিস বা উপসহকারী কৃষি কর্মকর্তার সাথে কথা বলুন। "
    "এই পরামর্শ এখনো কোনো কৃষিবিদ পর্যালোচনা করেননি।"
)


# ------------------------------------------------------------------------------------------------
# knowledge base
@dataclass(frozen=True)
class KnowledgeBase:
    version: str
    chunks: tuple[kb_search.Chunk, ...]
    sources: dict[str, dict[str, Any]]
    diseases: dict[str, dict[str, str]]
    excluded: tuple[dict[str, Any], ...]
    transcription: str
    policy: str

    @property
    def disease_codes(self) -> frozenset[str]:
        return frozenset(self.diseases)

    def by_id(self) -> dict[str, kb_search.Chunk]:
        return {c.id: c for c in self.chunks}


@lru_cache
def load_kb(path: Path = KB_FILE) -> KnowledgeBase:
    raw = json.loads(path.read_text(encoding="utf-8"))
    chunks = tuple(kb_search.parse_chunks(raw["chunks"]))
    sources = raw["sources"]
    diseases = raw["diseases"]
    for chunk in chunks:
        if chunk.source_id not in sources or chunk.disease not in diseases:
            raise ValueError(f"chunk {chunk.id} references an unknown source or disease")
    return KnowledgeBase(
        version=raw["version"],
        chunks=chunks,
        sources=sources,
        diseases=diseases,
        excluded=tuple(raw.get("excluded", [])),
        transcription=raw["transcription"],
        policy=raw["policy"],
    )


def excerpt(text_: str, words: int = 50) -> str:
    parts = text_.split()
    return " ".join(parts[:words]) + (" …" if len(parts) > words else "")


# ------------------------------------------------------------------------------------------------
# image hardening
@dataclass(frozen=True)
class ProcessedImage:
    jpeg: bytes
    sha256: str
    quality_issue: str | None


def process_image(raw: bytes, max_bytes: int) -> ProcessedImage:
    if not raw:
        raise AppError(422, "image_missing")
    if len(raw) > max_bytes:
        raise AppError(413, "payload_too_large")
    is_webp = raw[:4] == b"RIFF" and raw[8:12] == b"WEBP"
    if not (is_webp or any(raw.startswith(m) for m in _MAGIC)):
        raise AppError(415, "unsupported_image_type")
    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    try:
        with Image.open(io.BytesIO(raw)) as probe:
            if probe.format not in ("JPEG", "PNG", "WEBP"):
                raise AppError(415, "unsupported_image_type")
            probe.verify()
        with Image.open(io.BytesIO(raw)) as img:
            img.load()
            oriented = ImageOps.exif_transpose(img) or img
            rgb = oriented.convert("RGB")
    except AppError:
        raise
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError) as exc:
        raise AppError(422, "image_unreadable") from exc
    width, height = rgb.size
    issue = None if min(width, height) >= MIN_SIDE else "too_small"
    rgb.thumbnail((MAX_SIDE, MAX_SIDE))
    if issue is None:
        issue = _quality_issue(rgb)
    out = io.BytesIO()
    rgb.save(out, format="JPEG", quality=85, optimize=True)  # no exif= => metadata dropped
    jpeg = out.getvalue()
    return ProcessedImage(jpeg=jpeg, sha256=hashlib.sha256(jpeg).hexdigest(), quality_issue=issue)


def _quality_issue(rgb: Image.Image) -> str | None:
    """Heuristic thresholds (not tuned on data): very dark, very bright, or almost no edges."""
    gray = rgb.convert("L")
    small = gray.copy()
    small.thumbnail((256, 256))
    mean = ImageStat.Stat(small).mean[0]
    if mean < 25:
        return "too_dark"
    if mean > 235:
        return "too_bright"
    edge_img = small.filter(ImageFilter.FIND_EDGES)
    w, h = edge_img.size
    edge_img = edge_img.crop((2, 2, max(3, w - 2), max(3, h - 2)))  # the filter fires on borders
    edges = ImageStat.Stat(edge_img).stddev[0]
    if edges < 6:
        return "blurry"
    return None


# ------------------------------------------------------------------------------------------------
# service
class ScanService:
    def __init__(self, engine: AsyncEngine, llm: LlamaService, max_upload_mb: int) -> None:
        self.engine = engine
        self.llm = llm
        self.max_bytes = max_upload_mb * 1024 * 1024
        self.kb = load_kb()

    # -- views ---------------------------------------------------------------------------------
    def _citation_view(self, chunk_id: str) -> dict[str, Any] | None:
        chunk = self.kb.by_id().get(chunk_id)
        if chunk is None:
            return None
        src = self.kb.sources[chunk.source_id]
        return {
            "id": chunk.id,
            "source_id": chunk.source_id,
            "title": src["title"],
            "publisher": src["publisher"],
            "url": src["url"],
            "page": chunk.page,
            "excerpt": excerpt(chunk.text),
        }

    def view(self, row: dict[str, Any]) -> dict[str, Any]:
        disease = row.get("disease")
        names = self.kb.diseases.get(disease or "", {})
        cites = [c for c in (self._citation_view(i) for i in row.get("citations") or []) if c]
        advice = row.get("advice") or {}
        return {
            "id": str(row["id"]),
            "created_at": row["created_at"].isoformat(),
            "status": row["status"],
            "crop": row.get("crop"),
            "disease": disease,
            "disease_bn": names.get("bn"),
            "disease_en": names.get("en"),
            "confidence_band": row.get("confidence_band"),
            "reason": row.get("reason"),
            "region_code": row["region_code"],
            "advice": advice or None,
            "advice_source": row.get("advice_source", "none"),
            "citations": cites,
            "model": row.get("model"),
            "prompt_version": row.get("prompt_version"),
            "latency_ms": row.get("latency_ms"),
            "kb_version": self.kb.version,
            "reviewed_by_agronomist": False,
            "synthetic": bool(row.get("synthetic")),
        }

    # -- advice --------------------------------------------------------------------------------
    def static_card(self, disease: str, hits: list[kb_search.Hit]) -> dict[str, Any]:
        """Verbatim BRRI text, so it can never contain an invented number or chemical."""
        names = self.kb.diseases[disease]
        steps: list[str] = []
        cites: list[str] = []
        for hit in hits:
            if hit.chunk.topic not in ("cultural", "prevention"):
                continue
            body = hit.chunk.text.split(":", 1)[-1]
            for item in (s.strip(" ।;") for s in re.split(r"[;।]", body)):
                if item and len(item) <= advice_validator.MAX_STEP_CHARS and len(steps) < 5:
                    steps.append(item + "।")
            cites.append(hit.chunk.id)
            if len(steps) >= 5:
                break
        if not steps:
            steps = ["আপনার উপজেলা কৃষি অফিস বা উপসহকারী কৃষি কর্মকর্তার সাথে যোগাযোগ করুন।"]
            cites = [hits[0].chunk.id] if hits else []
        return {
            "summary_bn": (
                f"ছবিটি দেখে মনে হচ্ছে এটি {names['bn']} হতে পারে। "
                "নিচের ধাপগুলো ব্রি-এর ফ্যাক্ট শীট থেকে হুবহু নেয়া।"
            ),
            "steps_bn": steps,
            "chemical": None,
            "safety_bn": SAFETY_BN,
            "citations": cites,
        }

    async def make_advice(self, disease: str) -> tuple[dict[str, Any], list[str], str]:
        hits = kb_search.search(self.kb.chunks, disease=disease, k=kb_search.MAX_K)
        if not hits:
            return {}, [], "none"
        retrieved = {h.chunk.id: h.chunk.text for h in hits}
        # the model sees the situating context first, then the verbatim passage (contextual RAG)
        sources = [(h.chunk.id, h.chunk.indexed) for h in hits]
        for _attempt in range(2):  # first try + one retry
            try:
                reply = await self.llm.advice(self.kb.diseases[disease]["bn"], sources)
            except LlmUnavailableError:
                break
            errors = advice_validator.validate(reply.data, retrieved)
            if not errors and reply.data is not None:
                advice = dict(reply.data)
                advice["safety_bn"] = SAFETY_BN  # fixed wording, never model-written
                return advice, list(advice["citations"]), "llm"
            log.info("advice_rejected", disease=disease, errors=errors)
        card = self.static_card(disease, hits)
        return card, card["citations"], "static_card"

    # -- create --------------------------------------------------------------------------------
    async def create(
        self,
        p: Principal,
        *,
        image: bytes,
        region_code: str,
        idempotency_key: str,
        request_id: str,
    ) -> dict[str, Any]:
        authorize(p, "scans:create", Resource(owner_id=p.user_id, tenant_id=p.tenant_id))
        if region_code not in outbreak_rules.DIVISIONS:
            raise AppError(422, "region_invalid")
        if not _IDEM.match(idempotency_key or ""):
            raise AppError(422, "idempotency_key_invalid")
        ctx = db_context_for(p.user_id, p.role, p.region_codes)

        existing = await self._find(ctx, p.user_id, idempotency_key)
        if existing is not None:
            return self.view(existing)

        processed = process_image(image, self.max_bytes)
        started = utcnow()
        model: str | None = None
        crop: str | None = None
        if processed.quality_issue is not None:
            result = decision.Decision(status="not_sure", reason="poor_image")
        else:
            try:
                reply = await self.llm.vision(processed.jpeg)
                model = reply.model
                result = decision.decide(reply.data, self.kb.disease_codes)
            except LlmUnavailableError as exc:
                # reason codes only (http_401, not_configured, daily_cap, ...): never a secret
                model = f"unavailable:{exc.reason}"[:120]
                result = decision.Decision(status="not_sure", reason="model_error")
        crop = result.crop

        advice: dict[str, Any] = {}
        citations: list[str] = []
        advice_source = "none"
        if result.status == "diagnosed" and result.disease:
            advice, citations, advice_source = await self.make_advice(result.disease)
        latency_ms = int((utcnow() - started).total_seconds() * 1000)

        row = {
            "tenant": p.tenant_id,
            "uid": p.user_id,
            "idem": idempotency_key,
            "sha": processed.sha256,
            "region": region_code,
            "status": result.status,
            "crop": crop,
            "disease": result.disease,
            "band": result.band,
            "reason": result.reason,
            "advice": json.dumps(advice, ensure_ascii=False),
            "citations": citations,
            "src": advice_source,
            "model": model,
            "pv": (
                f"{VISION_PROMPT_VERSION}+{ADVICE_PROMPT_VERSION}"
                if advice_source == "llm"
                else VISION_PROMPT_VERSION
            ),
            "lat": latency_ms,
            "synthetic": p.is_demo,
        }
        async with session_scope(self.engine, ctx) as db:
            inserted = (
                (
                    await db.execute(
                        text(
                            "INSERT INTO scans (tenant_id, user_id, idempotency_key, image_sha256, "
                            "region_code, status, crop, disease, confidence_band, reason, advice, "
                            "citations, advice_source, model, prompt_version, latency_ms, "
                            "synthetic) "
                            "VALUES (:tenant, CAST(:uid AS uuid), :idem, :sha, :region, :status, "
                            ":crop, :disease, :band, :reason, CAST(:advice AS jsonb), :citations, "
                            ":src, :model, :pv, :lat, :synthetic) "
                            "ON CONFLICT (user_id, idempotency_key) DO NOTHING RETURNING *"
                        ),
                        row,
                    )
                )
                .mappings()
                .first()
            )
        if inserted is None:  # a concurrent duplicate won the race
            again = await self._find(ctx, p.user_id, idempotency_key)
            if again is None:
                raise AppError(409, "conflict")
            return self.view(again)
        if result.status == "diagnosed" and result.disease:
            try:
                await self.refresh_outbreak(p.tenant_id, result.disease, region_code)
            except Exception as exc:  # an alert failure must not lose the farmer's result
                log.warning("outbreak_refresh_failed", error_type=type(exc).__name__)
        log.info(
            "scan_created",
            request_id=request_id,
            status=result.status,
            reason=result.reason,
            advice_source=advice_source,
            latency_ms=latency_ms,
        )
        return self.view(dict(inserted))

    async def _find(self, ctx: Any, user_id: str, idem: str) -> dict[str, Any] | None:
        async with session_scope(self.engine, ctx) as db:
            found = (
                (
                    await db.execute(
                        text(
                            "SELECT * FROM scans WHERE user_id = CAST(:u AS uuid) "
                            "AND idempotency_key = :k"
                        ),
                        {"u": user_id, "k": idem},
                    )
                )
                .mappings()
                .first()
            )
        return dict(found) if found else None

    async def list_mine(self, p: Principal, limit: int = 30) -> list[dict[str, Any]]:
        authorize(p, "scans:read")
        ctx = db_context_for(p.user_id, p.role, p.region_codes)
        async with session_scope(self.engine, ctx) as db:
            rows = (
                (
                    await db.execute(
                        text(
                            "SELECT * FROM scans WHERE user_id = CAST(:u AS uuid) "
                            "ORDER BY created_at DESC LIMIT :n"
                        ),
                        {"u": p.user_id, "n": max(1, min(limit, 100))},
                    )
                )
                .mappings()
                .all()
            )
        return [self.view(dict(r)) for r in rows]

    async def get(self, p: Principal, scan_id: str) -> dict[str, Any]:
        authorize(p, "scans:read")
        if not re.fullmatch(r"[0-9a-fA-F-]{36}", scan_id):
            raise AppError(404, "not_found")
        ctx = db_context_for(p.user_id, p.role, p.region_codes)
        async with session_scope(self.engine, ctx) as db:
            row = (
                (
                    await db.execute(
                        text("SELECT * FROM scans WHERE id = CAST(:i AS uuid)"), {"i": scan_id}
                    )
                )
                .mappings()
                .first()
            )
        if row is None:  # RLS hides other users' rows: indistinguishable from missing
            raise AppError(404, "not_found")
        return self.view(dict(row))

    async def stats(self, p: Principal, days: int = 30) -> dict[str, Any]:
        """Scan counts per division and outcome for the reviewer chart. Counts only: no user ids,
        no advice text. RLS limits staff to their own tenant (demo staff see demo scans)."""
        authorize(p, "scans:stats")
        days = max(1, min(days, 90))
        ctx = db_context_for(p.user_id, p.role, p.region_codes)
        async with session_scope(self.engine, ctx) as db:
            rows = (
                await db.execute(
                    text(
                        "SELECT region_code, status, count(*) FROM scans "
                        "WHERE created_at >= :since GROUP BY region_code, status"
                    ),
                    {"since": utcnow() - timedelta(days=days)},
                )
            ).all()
        by_region: dict[str, dict[str, Any]] = {
            code: {
                "region_code": code,
                "region_bn": bn,
                "region_en": en,
                "diagnosed": 0,
                "not_sure": 0,
                "healthy": 0,
            }
            for code, (bn, en) in outbreak_rules.DIVISIONS.items()
        }
        for region, status, count in rows:
            if region in by_region and status in ("diagnosed", "not_sure", "healthy"):
                by_region[region][status] = int(count)
        return {"days": days, "divisions": list(by_region.values())}

    # -- outbreaks -----------------------------------------------------------------------------
    async def refresh_outbreak(self, tenant: str, disease: str, region: str) -> None:
        now = utcnow()
        async with system_scope(self.engine) as db:
            rows = (
                await db.execute(
                    text(
                        "SELECT disease, region_code, created_at FROM scans WHERE tenant_id = :t "
                        "AND disease = :d AND region_code = :r AND status = 'diagnosed' "
                        "AND created_at >= :since"
                    ),
                    {"t": tenant, "d": disease, "r": region, "since": now - outbreak_rules.WINDOW},
                )
            ).all()
            found = outbreak_rules.clusters(
                (outbreak_rules.Case(r[0], r[1], r[2]) for r in rows), now
            )
            for cluster in found:
                await db.execute(
                    text(
                        "INSERT INTO outbreak_alerts (tenant_id, disease, region_code, case_count, "
                        "window_start, window_end, synthetic) VALUES (:t, :d, :r, :n, :a, :b, :s) "
                        "ON CONFLICT (tenant_id, disease, region_code) WHERE status = 'draft' "
                        "DO UPDATE SET case_count = EXCLUDED.case_count, "
                        "window_start = EXCLUDED.window_start, window_end = EXCLUDED.window_end"
                    ),
                    {
                        "t": tenant,
                        "d": cluster.disease,
                        "r": cluster.region_code,
                        "n": cluster.count,
                        "a": cluster.first,
                        "b": cluster.last,
                        "s": tenant == "demo",
                    },
                )

    def alert_view(self, row: dict[str, Any]) -> dict[str, Any]:
        names = self.kb.diseases.get(row["disease"], {})
        division = outbreak_rules.DIVISIONS.get(row["region_code"], ("", ""))
        return {
            "id": str(row["id"]),
            "disease": row["disease"],
            "disease_bn": names.get("bn"),
            "disease_en": names.get("en"),
            "region_code": row["region_code"],
            "region_bn": division[0],
            "region_en": division[1],
            "case_count": row["case_count"],
            "window_start": row["window_start"].isoformat(),
            "window_end": row["window_end"].isoformat(),
            "status": row["status"],
            "decided_at": row["decided_at"].isoformat() if row.get("decided_at") else None,
            "created_at": row["created_at"].isoformat(),
            "unverified": True,
            "synthetic": bool(row.get("synthetic")),
        }

    async def list_alerts(self, p: Principal) -> list[dict[str, Any]]:
        authorize(p, "alerts:read")
        ctx = db_context_for(p.user_id, p.role, p.region_codes)
        async with session_scope(self.engine, ctx) as db:
            rows = (
                (
                    await db.execute(
                        text(
                            "SELECT * FROM outbreak_alerts WHERE created_at >= :since "
                            "ORDER BY (status = 'draft') DESC, created_at DESC LIMIT 50"
                        ),
                        {"since": utcnow() - timedelta(days=60)},
                    )
                )
                .mappings()
                .all()
            )
        return [self.alert_view(dict(r)) for r in rows]

    async def decide_alert(
        self,
        p: Principal,
        alert_id: str,
        *,
        approve: bool,
        request_id: str,
        ip_hash: str,
    ) -> dict[str, Any]:
        authorize(p, "alerts:decide", Resource(tenant_id=p.tenant_id))
        if not re.fullmatch(r"[0-9a-fA-F-]{36}", alert_id):
            raise AppError(404, "not_found")
        new_status = "approved" if approve else "rejected"
        ctx = db_context_for(p.user_id, p.role, p.region_codes)
        async with session_scope(self.engine, ctx) as db:
            row = (
                (
                    await db.execute(
                        text(
                            "UPDATE outbreak_alerts SET status = :s, "
                            "decided_by = CAST(:u AS uuid), "
                            "decided_at = now() WHERE id = CAST(:i AS uuid) AND status = 'draft' "
                            "RETURNING *"
                        ),
                        {"s": new_status, "u": p.user_id, "i": alert_id},
                    )
                )
                .mappings()
                .first()
            )
            if row is None:
                raise AppError(409, "alert_not_draft")
            await events.record(
                db,
                action=f"alert.{new_status}",
                actor_id=p.user_id,
                actor_role=p.role,
                tenant_id=p.tenant_id,
                object_type="outbreak_alert",
                object_id=alert_id,
                request_id=request_id,
                ip_hash=ip_hash,
                before={"status": "draft"},
                after={"status": new_status},
            )
        return self.alert_view(dict(row))
