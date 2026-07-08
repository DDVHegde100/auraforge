"""Optional ONNX sky segmentation stub — falls back to heuristic."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from auraforge_engine.masks.sky import sky_mask


def sky_mask_onnx(rgb: np.ndarray, model_path: str | None = None) -> np.ndarray | None:
    """Return ONNX sky mask if runtime + weights exist; else None."""
    path = Path(model_path) if model_path else None
    if path is None or not path.is_file():
        return None
    try:
        import onnxruntime  # noqa: F401
    except ImportError:
        return None
    # stub: weights present but inference not wired yet
    return None


def resolve_sky_mask(
    rgb: np.ndarray,
    *,
    use_onnx: bool = False,
    model_path: str | None = None,
) -> tuple[np.ndarray, str]:
    if use_onnx:
        onnx = sky_mask_onnx(rgb, model_path=model_path)
        if onnx is not None:
            return np.clip(onnx, 0.0, 1.0).astype(np.float32), "onnx"
    return sky_mask(rgb), "heuristic"
