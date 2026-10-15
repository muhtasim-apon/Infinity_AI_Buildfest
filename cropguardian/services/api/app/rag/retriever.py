"""Hybrid retrieval: pgvector cosine top-20 ∪ full-text top-20 → reciprocal rank fusion (k=60)
→ metadata filter (crop, disease; retired docs excluded) → top-k (``RAG_TOP_K``).
Query embedding: multilingual-e5-small (ONNX) with the ``"query: "`` prefix.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Chunk:
    id: UUID
    document_id: UUID
    title: str
    publisher: str
    page: int | None
    url: str
    content: str
    score: float


async def retrieve(disease_code: str, crop: str, stage: str | None, question: str | None, k: int) -> list[Chunk]:
    """Return ≤ k chunks, best first. Empty list or best score < ``RAG_MIN_SCORE`` → caller escalates."""
    raise NotImplementedError


def rrf(rankings: list[list[UUID]], k: int = 60) -> list[tuple[UUID, float]]:
    """Reciprocal rank fusion: score(d) = Σ 1 / (k + rank_i(d))."""
    raise NotImplementedError
