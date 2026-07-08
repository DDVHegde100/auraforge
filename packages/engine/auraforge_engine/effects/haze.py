"""Soft atmospheric haze."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.histogram import luminance


def soft_haze(
    rgb: np.ndarray,
    *,
    lift: float = 0.04,
    desaturate: float = 0.12,
    warmth: float = 0.06,
) -> np.ndarray:
    if lift == 0.0 and desaturate == 0.0 and warmth == 0.0:
        return rgb
    out = rgb + lift
    lum = luminance(out)[..., None]
    out = lum + (out - lum) * (1.0 - desaturate)
    out[..., 0] += warmth * 0.5
    out[..., 2] -= warmth * 0.3
    return np.clip(out, 0.0, None)
