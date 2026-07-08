"""Vibrance and saturation."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.histogram import luminance


def apply_saturation(rgb: np.ndarray, amount: float) -> np.ndarray:
    if amount == 0.0:
        return rgb
    lum = luminance(rgb)[..., None]
    return np.clip(lum + (rgb - lum) * (1.0 + amount), 0.0, None)


def apply_vibrance(rgb: np.ndarray, amount: float) -> np.ndarray:
    if amount == 0.0:
        return rgb
    lum = luminance(rgb)[..., None]
    chroma = rgb - lum
    sat = np.sqrt((chroma**2).sum(axis=-1, keepdims=True))
    boost = 1.0 + amount * (1.0 - np.clip(sat * 2.5, 0.0, 1.0))
    return np.clip(lum + chroma * boost, 0.0, None)


def apply_vibrance_sat(
    rgb: np.ndarray,
    *,
    vibrance: float = 0.0,
    saturation: float = 0.0,
) -> np.ndarray:
    out = apply_saturation(rgb, saturation)
    return apply_vibrance(out, vibrance)
