"""Red halation bloom — CineStill / tungsten film highlight bleed."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


def film_halation(
    rgb: np.ndarray,
    *,
    amount: float = 0.35,
    threshold: float = 0.72,
    spread: float = 14.0,
    color: list[float] | None = None,
) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    tint = np.array(color or [1.0, 0.28, 0.12], dtype=np.float32)
    lum = luminance(rgb)
    mask = np.clip((lum - threshold) / max(1.0 - threshold, 1e-4), 0.0, 1.0)
    k = int(max(3, spread * 2)) | 1
    bleed = cv2.GaussianBlur((rgb * mask[..., None]).astype(np.float32), (k, k), sigmaX=spread)
    return np.clip(rgb + bleed * tint * amount, 0.0, None)
