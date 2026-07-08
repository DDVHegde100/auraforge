"""Creative vignette."""

from __future__ import annotations

import numpy as np


def apply_vignette(
    rgb: np.ndarray,
    *,
    strength: float = 0.0,
    feather: float = 0.75,
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    h, w = rgb.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    radius = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    max_r = np.sqrt(cx**2 + cy**2)
    mask = np.clip(radius / (max_r * feather), 0.0, 1.0) ** 1.8
    factor = 1.0 - strength * mask
    return np.clip(rgb * factor[..., None], 0.0, None)
