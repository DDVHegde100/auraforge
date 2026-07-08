"""Highlight recovery."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.histogram import luminance


def apply_highlight_recovery(rgb: np.ndarray, amount: float) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    lum = luminance(rgb)
    hi_mask = np.clip((lum - 0.75) / 0.25, 0.0, 1.0) ** 2.0
    compressed = 0.75 + (np.clip(lum, 0.0, 1.0) - 0.75) * (1.0 - amount * 0.65)
    scale = np.divide(
        compressed,
        np.maximum(lum, 1e-6),
        out=np.ones_like(lum),
        where=lum > 1e-6,
    )
    result = rgb * (1.0 - hi_mask[..., None] + hi_mask[..., None] * scale[..., None])
    return np.clip(result, 0.0, None)
