"""Split tone shadows and highlights."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.histogram import luminance


def split_tone(
    rgb: np.ndarray,
    *,
    shadow_rgb: tuple[float, float, float] = (0.02, 0.04, 0.10),
    highlight_rgb: tuple[float, float, float] = (1.0, 0.92, 0.78),
    balance: float = 0.0,
    strength: float = 0.25,
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    lum = luminance(rgb)
    split = 0.5 + balance * 0.25
    shadow_w = np.clip(1.0 - lum / split, 0.0, 1.0)
    hi_w = np.clip((lum - split) / max(1.0 - split, 1e-6), 0.0, 1.0)
    shadow_tint = np.array(shadow_rgb, dtype=np.float32)
    hi_tint = np.array(highlight_rgb, dtype=np.float32)
    tinted = rgb.copy()
    tinted = tinted * (1.0 - shadow_w[..., None] * strength) + shadow_tint * shadow_w[..., None] * strength
    tinted = tinted * (1.0 - hi_w[..., None] * strength) + hi_tint * hi_w[..., None] * strength
    return tinted
