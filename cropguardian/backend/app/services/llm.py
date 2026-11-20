"""Meta Llama API client (OpenAI-compatible endpoint): vision triage + Bangla advice (D-031).

Safety properties:
- every call goes through `AllowListedClient` (https, allow-listed host, no redirects, breaker);
- 20 s timeout, ONE retry on timeout / 5xx / 429, then the caller falls back (not sure / card);
- a per-day call cap in Redis stops runaway spend; if Redis is unreachable the cap fails CLOSED;
- no personal data is ever put in a prompt: the image is a re-encoded JPEG with EXIF/GPS removed,
  and the advice prompt carries only the disease label and KB passages;
- the API key, prompts and model output are never logged (only model name, status and latency).
"""

from __future__ import annotations

import base64
import json
import re
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.clock import utcnow
from app.core.config import Settings
from app.core.http import (
    AllowListedClient,
    CircuitBreaker,
    CircuitOpenError,
    HTTPError,
    OutboundBlockedError,
)
from app.core.logging import get_logger

PROMPT_DIR = Path(__file__).resolve().parent.parent / "ai" / "prompts"
VISION_PROMPT_VERSION = "vision_v1"
ADVICE_PROMPT_VERSION = "advice_v1"
_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)
log = get_logger("cg.llm")


def clean_api_key(raw: str) -> str:
    """Dashboard copy-paste often adds whitespace, quotes or a 'Bearer ' prefix; any of them turns a
    valid key into an HTTP 401. Normalise once; never log the value."""
    key = raw.strip().strip("\"'").strip()
    if key.lower().startswith("bearer "):
        key = key[7:].strip()
    return key


class LlmUnavailableError(Exception):
    """No answer: key missing, cap reached, breaker open, network/timeout or bad status."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@lru_cache
def prompt(name: str) -> str:
    if not re.fullmatch(r"[a-z]+_v\d+", name):
        raise ValueError("bad prompt name")
    return (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")


def parse_json_object(text: str) -> dict[str, Any] | None:
    """Lenient extraction of ONE JSON object from model text (code fences / chatter tolerated)."""
    if not isinstance(text, str) or len(text) > 20_000:
        return None
    cleaned = _FENCE.sub("", text.strip())
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        value = json.loads(cleaned[start : end + 1])
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def _content_text(payload: Any) -> str:
    """OpenAI-compatible shape: choices[0].message.content (string or list of parts)."""
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        # native Llama API shape, in case the base URL points there
        try:
            content = payload["completion_message"]["content"]
        except (KeyError, TypeError):
            return ""
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return str(content.get("text", ""))
    if isinstance(content, list):
        return "".join(str(p.get("text", "")) for p in content if isinstance(p, dict))
    return ""


@dataclass(frozen=True)
class LlmReply:
    data: dict[str, Any] | None
    model: str
    latency_ms: int


class LlamaService:
    def __init__(
        self,
        settings: Settings,
        redis: Redis | None,
        client: AllowListedClient | None = None,
    ) -> None:
        self.settings = settings
        self.redis = redis
        self.client = client or AllowListedClient(
            frozenset(settings.outbound_allowlist),
            connect_timeout=5.0,
            read_timeout=settings.llm_timeout_s,
            breaker=CircuitBreaker(threshold=4, reset_seconds=60.0),
        )

    @property
    def api_key(self) -> str:
        return clean_api_key(self.settings.llama_api_key)

    @property
    def configured(self) -> bool:
        return bool(self.api_key) and self.settings.advice_mode == "live"

    async def _within_cap(self) -> bool:
        cap = self.settings.llm_daily_call_cap
        if cap <= 0 or self.redis is None:
            return False
        key = f"cg:llm_calls:{utcnow().date().isoformat()}"
        try:
            count = int(await self.redis.incr(key))
            if count == 1:
                await self.redis.expire(key, 2 * 86400)
        except RedisError:
            return False  # fail closed: no budget check, no spend
        return count <= cap

    async def _post(self, body: dict[str, Any]) -> dict[str, Any]:
        url = self.settings.llm_base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        last = "unknown"
        for attempt in range(2):  # one retry
            try:
                response = await self.client.request("POST", url, headers=headers, json=body)
            except (OutboundBlockedError, CircuitOpenError) as exc:
                raise LlmUnavailableError(type(exc).__name__) from exc
            except HTTPError as exc:
                last = type(exc).__name__
                continue
            if response.status_code == 400 and "response_format" in body and attempt == 0:
                body = {k: v for k, v in body.items() if k != "response_format"}
                last = "http_400_response_format"
                continue
            if response.status_code in (429, 500, 502, 503, 504):
                last = f"http_{response.status_code}"
                continue
            if response.status_code != 200:
                raise LlmUnavailableError(f"http_{response.status_code}")
            try:
                payload = response.json()
            except ValueError as exc:
                raise LlmUnavailableError("non_json_body") from exc
            if not isinstance(payload, dict):
                raise LlmUnavailableError("non_object_body")
            return payload
        raise LlmUnavailableError(last)

    async def _complete(
        self, messages: list[dict[str, Any]], *, max_tokens: int, kind: str
    ) -> LlmReply:
        if not self.configured:
            raise LlmUnavailableError("not_configured")
        if not await self._within_cap():
            raise LlmUnavailableError("daily_cap")
        body: dict[str, Any] = {
            "model": self.settings.llm_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        started = time.monotonic()
        try:
            payload = await self._post(body)
        except LlmUnavailableError as exc:
            log.warning("llm_call_failed", kind=kind, reason=exc.reason)
            raise
        latency_ms = int((time.monotonic() - started) * 1000)
        data = parse_json_object(_content_text(payload))
        log.info(
            "llm_call",
            kind=kind,
            model=self.settings.llm_model,
            latency_ms=latency_ms,
            parsed=data is not None,
        )
        return LlmReply(data=data, model=self.settings.llm_model, latency_ms=latency_ms)

    async def vision(self, jpeg: bytes) -> LlmReply:
        data_url = "data:image/jpeg;base64," + base64.b64encode(jpeg).decode("ascii")
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": prompt(VISION_PROMPT_VERSION)},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Classify this photo. Reply with the JSON object only.",
                    },
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            },
        ]
        return await self._complete(messages, max_tokens=300, kind="vision")

    async def advice(self, disease_bn: str, sources: list[tuple[str, str]]) -> LlmReply:
        passages = "\n".join(
            f'<source id="{cid}">{_strip_tags(text)}</source>' for cid, text in sources
        )
        user = f"রোগ: {_strip_tags(disease_bn)}\n\n{passages}\n\nএখন শুধু JSON অবজেক্টটি লিখুন।"
        messages = [
            {"role": "system", "content": prompt(ADVICE_PROMPT_VERSION)},
            {"role": "user", "content": user},
        ]
        return await self._complete(messages, max_tokens=900, kind="advice")

    async def aclose(self) -> None:
        await self.client.aclose()


def _strip_tags(text: str) -> str:
    """KB text is trusted-ish but still data: remove angle brackets so it cannot close <source>."""
    return text.replace("<", " ").replace(">", " ")
