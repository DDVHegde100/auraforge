"""Exposure adjustment."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.histogram import luminance


def apply_exposure_stops(rgb: np.ndarray, stops: float) -> np.ndarray:
    if stops == 0.0:
        return rgb
    out = rgb * (2.0**stops)
    if stops <= 0.0:
        return out

    # Protect highlights when lifting exposure — avoids blown skies/skin.
    lum = luminance(out)
    knee = 0.82 + min(stops, 0.65) * 0.08
    roll = np.clip((lum - knee) / max(1.0 - knee, 1e-4), 0.0, 1.0) ** 1.8
    compress = 1.0 - roll * min(0.42, stops * 0.38)
    return out * compress[..., None]
