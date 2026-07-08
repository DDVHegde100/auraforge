"""Luminance-zone relighting — shadows, mids, highlights."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance
from auraforge_engine.effects.bloom import highlight_bloom


def light_remap(
    rgb: np.ndarray,
    *,
    strength: float = 0.45,
    shadow_lift: float = 0.10,
    highlight_glow: float = 0.22,
    mid_punch: float = 0.12,
    shadow_tint: tuple[float, float, float] = (0.92, 0.96, 1.04),
    highlight_tint: tuple[float, float, float] = (1.04, 1.02, 0.96),
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    t = max(0.0, min(1.0, strength))
    lum = luminance(rgb)
    shadow_w = np.clip(1.0 - lum / 0.38, 0.0, 1.0) ** 1.6
    hi_w = np.clip((lum - 0.62) / 0.38, 0.0, 1.0) ** 1.4
    mid_w = np.clip(1.0 - np.abs(lum - 0.48) / 0.48, 0.0, 1.0) ** 1.2

    out = rgb.astype(np.float32, copy=True)
    if shadow_lift > 0:
        lift = shadow_lift * t * shadow_w[..., None]
        out = out + lift * (1.0 - out)
        st = np.array(shadow_tint, dtype=np.float32)
        out = out * (1.0 - shadow_w[..., None] * t * 0.35) + out * st * shadow_w[..., None] * t * 0.35

    if mid_punch > 0:
        pivot = 0.18
        factor = 1.0 + mid_punch * t * mid_w
        out = (out - pivot) * factor[..., None] + pivot

    if highlight_glow > 0:
        out = highlight_bloom(
            out,
            threshold=0.68,
            blur_sigma=14.0 + 10.0 * t,
            intensity=highlight_glow * t,
        )
        ht = np.array(highlight_tint, dtype=np.float32)
        out = out * (1.0 - hi_w[..., None] * t * 0.28) + out * ht * hi_w[..., None] * t * 0.28

    return np.clip(out, 0.0, None)
