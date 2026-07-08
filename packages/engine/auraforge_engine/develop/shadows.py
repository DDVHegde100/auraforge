"""Shadow lift."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.histogram import luminance


def apply_shadow_lift(rgb: np.ndarray, amount: float) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    lum = luminance(rgb)
    shadow_mask = np.clip(1.0 - lum * 2.5, 0.0, 1.0) ** 1.5
    lift = amount * shadow_mask[..., None]
    return rgb + lift * (1.0 - rgb)
