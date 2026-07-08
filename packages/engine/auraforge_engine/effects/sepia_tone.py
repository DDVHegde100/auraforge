"""Sepia / antique monochrome tone."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.histogram import luminance


def sepia_tone(
    rgb: np.ndarray,
    *,
    strength: float = 0.85,
    warmth: float = 0.08,
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    lum = luminance(rgb)[..., None]
    sepia = np.stack(
        [
            lum * (1.0 + 0.18 + warmth),
            lum * (0.92 + warmth * 0.5),
            lum * (0.72 - warmth * 0.3),
        ],
        axis=-1,
    )
    t = max(0.0, min(1.0, strength))
    return np.clip(rgb * (1.0 - t) + sepia * t, 0.0, None)
