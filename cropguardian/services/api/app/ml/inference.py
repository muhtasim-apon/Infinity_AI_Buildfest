"""ONNX Runtime inference (ADR 0004).

- Session created once at startup: ``InferenceSession(path, providers=["CPUExecutionProvider"])``,
  ``intra_op_num_threads=1``. SHA-256 of the file checked against the active ``model_versions``
  row; mismatch → app not ready (threat T6).
- Called via ``run_in_threadpool`` behind ``asyncio.Semaphore(2)`` so CPU work never blocks the
  event loop and memory stays bounded (A4, A5).
- Hard timeout ``INFERENCE_TIMEOUT_MS`` → ``InferenceTimeout`` → router returns 503.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


class InferenceTimeout(Exception):
    pass


@dataclass(frozen=True)
class LoadedModel:
    name: str
    version: str
    sha256: str
    labels: tuple[str, ...]     # order == model output order == ml/vision/configs/labels.yaml
    temperature: float
    threshold: float


def load_session(path: str, expected_sha256: str) -> LoadedModel:
    raise NotImplementedError


async def predict_logits(model: LoadedModel, tensor: npt.NDArray[np.float32], timeout_ms: int) -> npt.NDArray[np.float32]:
    """Return raw logits of shape (n_classes,)."""
    raise NotImplementedError
