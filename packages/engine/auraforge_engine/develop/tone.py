"""Lightroom-style parametric tone (blacks / shadows / highlights / whites)."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.histogram import luminance
from auraforge_engine.develop.chroma import relight_preserving_chroma


def apply_parametric_tone(
    rgb: np.ndarray,
    *,
    blacks: float = 0.0,
    shadows: float = 0.0,
    highlights: float = 0.0,
    whites: float = 0.0,
    contrast: float = 0.0,
) -> np.ndarray:
    lum = luminance(rgb)
    target = lum.astype(np.float32, copy=True)

    if blacks != 0.0:
        toe = np.clip(1.0 - lum / 0.14, 0.0, 1.0) ** 2.2
        target = target + blacks * toe * (0.12 - target * 0.35)

    if shadows > 0.0:
        sh = np.clip(1.0 - lum / 0.38, 0.0, 1.0) ** 1.55
        target = target + shadows * sh * (1.0 - target)
    elif shadows < 0.0:
        sh = np.clip(1.0 - lum / 0.42, 0.0, 1.0) ** 1.4
        target = target + shadows * sh * target * 0.65

    if highlights > 0.0:
        hi = np.clip((lum - 0.62) / 0.38, 0.0, 1.0) ** 1.85
        compressed = 0.62 + (lum - 0.62) * (1.0 - highlights * 0.72)
        target = target * (1.0 - hi) + compressed * hi
    elif highlights < 0.0:
        hi = np.clip((lum - 0.58) / 0.42, 0.0, 1.0) ** 1.6
        target = target + (-highlights) * hi * (1.0 - target) * 0.45

    if whites > 0.0:
        wh = np.clip((lum - 0.82) / 0.18, 0.0, 1.0) ** 1.3
        target = target + whites * wh * (1.0 - target) * 0.55
    elif whites < 0.0:
        wh = np.clip((lum - 0.78) / 0.22, 0.0, 1.0)
        target = target + whites * wh * target * 0.35

    if contrast != 0.0:
        pivot = 0.18
        target = (target - pivot) * (1.0 + contrast) + pivot

    return relight_preserving_chroma(rgb, np.clip(target, 0.0, None))
