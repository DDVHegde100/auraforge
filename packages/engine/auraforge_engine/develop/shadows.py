"""Shadow lift."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.histogram import luminance


def apply_shadow_lift(rgb: np.ndarray, amount: float) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    lum = luminance(rgb)
    shadow_mask = np.clip(1.0 - lum * 2.2, 0.0, 1.0) ** 1.45
    lift = amount * shadow_mask[..., None]

    # Lift luminance while preserving chroma ratio in shadows.
    lifted_lum = np.clip(lum + lift[..., 0] * (1.0 - lum), 0.0, None)
    scale = np.divide(
        lifted_lum,
        np.maximum(lum, 1e-5),
        out=np.ones_like(lum),
        where=lum > 1e-5,
    )
    return np.clip(rgb * scale[..., None], 0.0, None)
