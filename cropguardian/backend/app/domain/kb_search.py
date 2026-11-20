"""Knowledge-base retrieval over the versioned BRRI chunks (Gantt P2, Salwa step 3). Pure logic.

What it is (and is not): metadata filter on the diagnosed disease + keyword overlap scoring on a
Bangla/English tokeniser over each chunk's text PLUS its LLM-written context sentence (contextual
retrieval, Anthropic-style: the context was written by Claude after reading the whole factsheet),
top-k with chunk ids. There are NO embeddings and NO vector search yet
(pgvector + multilingual-e5 is *planned*); the Trust Centre and the CloudCamp form say so.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

MAX_K = 8
# Bangla letters (U+0980..U+09FF) or ASCII word characters; Bangla digits are kept as tokens too.
_TOKEN = re.compile(r"[\u0980-\u09FF]+|[A-Za-z0-9]+")
TOPIC_WEIGHT = {
    "cultural": 3.0,
    "prevention": 2.5,
    "symptom": 2.0,
    "conditions": 1.5,
    "overview": 1.0,
}


@dataclass(frozen=True)
class Chunk:
    id: str
    source_id: str
    page: int
    disease: str
    topic: str
    text: str
    context: str = ""  # LLM-written situating sentence (contextual retrieval); indexed with text

    @property
    def indexed(self) -> str:
        return f"{self.context} {self.text}".strip()


@dataclass(frozen=True)
class Hit:
    chunk: Chunk
    score: float


def tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text or "") if len(t) > 1]


def parse_chunks(raw: Iterable[Mapping[str, Any]]) -> list[Chunk]:
    """Validate the KB file. Raises ValueError on any malformed or duplicate chunk."""
    out: list[Chunk] = []
    seen: set[str] = set()
    for item in raw:
        try:
            chunk = Chunk(
                id=str(item["id"]),
                source_id=str(item["source_id"]),
                page=int(item["page"]),
                disease=str(item["disease"]),
                topic=str(item["topic"]),
                text=str(item["text"]),
                context=str(item.get("context", "")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"malformed chunk: {exc}") from exc
        if not re.fullmatch(r"[a-z0-9-]{3,64}", chunk.id) or chunk.id in seen:
            raise ValueError(f"bad or duplicate chunk id: {chunk.id!r}")
        if chunk.topic not in TOPIC_WEIGHT or not chunk.text.strip() or chunk.page < 1:
            raise ValueError(f"bad chunk fields: {chunk.id}")
        seen.add(chunk.id)
        out.append(chunk)
    return out


def search(
    chunks: Iterable[Chunk], *, disease: str | None, question: str = "", k: int = MAX_K
) -> list[Hit]:
    """Top-k chunks. With a disease, only that disease's chunks are eligible (metadata filter);
    the question only re-ranks. Without a disease and without query overlap, returns nothing:
    no retrieval => no advice (the caller shows the 'no advice available' card)."""
    k = max(0, min(k, MAX_K))
    query = set(tokens(question))
    hits: list[Hit] = []
    for chunk in chunks:
        if disease is not None and chunk.disease != disease:
            continue
        overlap = len(query & set(tokens(chunk.indexed))) if query else 0
        if disease is None and overlap == 0:
            continue
        score = TOPIC_WEIGHT[chunk.topic] + overlap * 0.5
        hits.append(Hit(chunk, score))
    hits.sort(key=lambda h: (-h.score, h.chunk.id))
    return hits[:k]
