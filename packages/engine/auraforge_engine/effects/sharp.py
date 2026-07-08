"""Quality-preserving unsharp mask — no resize, noise-aware."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


def unsharp_mask(
    rgb: np.ndarray,
    *,
    amount: float = 0.25,
    radius: float = 1.1,
    threshold: float = 0.004,
) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    t = max(0.0, min(1.0, amount))
    blur = cv2.GaussianBlur(rgb, (0, 0), sigmaX=radius)
    detail = rgb - blur
    lum_d = luminance(detail)
    mask = (np.abs(lum_d) > threshold).astype(np.float32)[..., None]
    return np.clip(rgb + detail * t * mask, 0.0, None)
