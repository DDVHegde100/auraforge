"""Local sky tone enhancement."""

from __future__ import annotations

import numpy as np

from auraforge_engine.develop import apply_dehaze_lite, apply_vibrance_sat, apply_warmth_tint


def apply_sky_tone(
    rgb: np.ndarray,
    mask: np.ndarray,
    *,
    dehaze: float = 0.18,
    vibrance: float = 0.12,
    warmth: float = -0.08,
) -> np.ndarray:
    """Lift sky band saturation/clarity without touching foreground."""
    if float(mask.max()) <= 1e-4:
        return rgb
    m = mask[..., None]
    enhanced = apply_dehaze_lite(rgb, dehaze)
    enhanced = apply_vibrance_sat(enhanced, vibrance=vibrance, saturation=vibrance * 0.5)
    enhanced = apply_warmth_tint(enhanced, warmth=warmth)
    return np.clip(rgb * (1.0 - m) + enhanced * m, 0.0, None)
