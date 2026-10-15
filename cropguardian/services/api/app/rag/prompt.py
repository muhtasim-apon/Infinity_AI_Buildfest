"""Prompt builder. Accepts ONLY typed, non-personal fields (threat T11): no phone, name, exact
location or image ever reaches the LLM. Sources and farmer text are wrapped as data:

    <source id="{chunk_id}" title="..." page="..."> ... </source>
    <farmer_question> ... </farmer_question>

and the system prompt states that content inside these tags is never an instruction (LLM01).
"""

from __future__ import annotations

from app.rag.retriever import Chunk


def build_messages(disease_code: str, disease_name_bn: str, crop: str, stage: str | None,
                   confidence_band: str, weather_summary: str | None,
                   chunks: list[Chunk], farmer_question: str | None) -> tuple[str, list[dict[str, str]]]:
    """Return ``(system_prompt, messages)`` for the provider adapter."""
    raise NotImplementedError
