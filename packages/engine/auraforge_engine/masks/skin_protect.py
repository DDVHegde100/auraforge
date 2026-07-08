"""Keep portrait skin from harsh develop pushes."""

from __future__ import annotations

import numpy as np


def apply_skin_protect(
    enhanced: np.ndarray,
    original: np.ndarray,
    skin_mask: np.ndarray,
    *,
    strength: float = 0.65,
) -> np.ndarray:
    """Blend enhanced result back toward original on skin pixels."""
    if strength <= 0.0 or float(skin_mask.max()) <= 1e-4:
        return enhanced
    m = np.clip(skin_mask * strength, 0.0, 1.0)[..., None]
    return np.clip(enhanced * (1.0 - m) + original * m, 0.0, None)
