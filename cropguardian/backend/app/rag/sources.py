"""Validation of `kb/sources.yaml` and the ingestion host allow-list (spec 10.1, 10.2, CC-45).

Why: the KB is the only thing advice may cite, so every document must state publisher, edition,
licence note and (once downloaded) a SHA-256. The set of hosts in this file is also the SSRF
allow-list for admin ingestion: a fetch to any other host is refused.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import yaml

REQUIRED = (
    "id",
    "title",
    "publisher",
    "url",
    "edition_date",
    "language",
    "licence_note",
    "retrieved_at",
)
STATUSES = frozenset({"downloaded", "candidate_not_downloaded"})
EXTRACTIONS = frozenset({"text", "needs_ocr", "needs_manual"})
_ID_RE = re.compile(r"^[a-z0-9_]{3,64}$")
_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_HOST_RE = re.compile(r"^[a-z0-9.-]+$")


class SourcesError(ValueError):
    """kb/sources.yaml is invalid. The message lists every problem found."""


def load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(
        path.read_text(encoding="utf-8")
    )  # safe_load only (forbidden-pattern rule)
    if not isinstance(data, dict) or not isinstance(data.get("documents"), list):
        raise SourcesError("top-level 'documents' list is required")
    return data


def validate(data: dict[str, Any]) -> list[str]:  # noqa: PLR0912 (one flat rule list reads best)
    """Return a list of problems (empty = valid)."""
    problems: list[str] = []
    seen: set[str] = set()
    for i, doc in enumerate(data["documents"]):
        label = doc.get("id", f"#{i}") if isinstance(doc, dict) else f"#{i}"
        if not isinstance(doc, dict):
            problems.append(f"{label}: entry is not a mapping")
            continue
        for key in REQUIRED:
            if not str(doc.get(key, "")).strip():
                problems.append(f"{label}: missing '{key}'")
        doc_id = str(doc.get("id", ""))
        if doc_id and not _ID_RE.match(doc_id):
            problems.append(f"{label}: id must match {_ID_RE.pattern}")
        if doc_id in seen:
            problems.append(f"{label}: duplicate id")
        seen.add(doc_id)
        url = str(doc.get("url", ""))
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            problems.append(f"{label}: url must be http(s) with a host")
        if parts.username or parts.password:
            problems.append(f"{label}: credentials in url are not allowed")
        if str(doc.get("retrieved_at", "")) and not _DATE_RE.match(str(doc["retrieved_at"])):
            problems.append(f"{label}: retrieved_at must be YYYY-MM-DD")
        status = doc.get("status")
        if status not in STATUSES:
            problems.append(f"{label}: status must be one of {sorted(STATUSES)}")
        if status == "downloaded":
            sha = str(doc.get("sha256", ""))
            if not _SHA_RE.match(sha):
                problems.append(f"{label}: downloaded documents need a 64-hex sha256")
            if doc.get("extraction") not in EXTRACTIONS:
                problems.append(f"{label}: extraction must be one of {sorted(EXTRACTIONS)}")
            if not isinstance(doc.get("bytes"), int) or doc["bytes"] <= 0:
                problems.append(f"{label}: bytes must be a positive integer")
        elif doc.get("sha256"):
            problems.append(f"{label}: a sha256 without status 'downloaded' is suspicious")
        if "expert_reviewed" in doc and doc["expert_reviewed"] is not False:
            problems.append(
                f"{label}: expert_reviewed may only be set by a real reviewer (none exist yet)"
            )
        if doc.get("disease_hint_verified") is True and not doc.get("disease_hint"):
            problems.append(f"{label}: disease_hint_verified without disease_hint")
    return problems


def allowed_hosts(data: dict[str, Any]) -> frozenset[str]:
    """Lower-case hostnames of every source: the ingestion SSRF allow-list."""
    hosts = set()
    for doc in data["documents"]:
        host = (urlsplit(str(doc.get("url", ""))).hostname or "").lower()
        if host and _HOST_RE.match(host):
            hosts.add(host)
    return frozenset(hosts)


def is_ingestion_url_allowed(url: str, data: dict[str, Any]) -> bool:
    """True only for http(s) URLs whose exact host is a listed source (no suffix matching)."""
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or parts.username or parts.password:
        return False
    return (parts.hostname or "").lower() in allowed_hosts(data)


def load_validated(path: Path) -> dict[str, Any]:
    data = load(path)
    problems = validate(data)
    if problems:
        raise SourcesError("; ".join(problems))
    return data
