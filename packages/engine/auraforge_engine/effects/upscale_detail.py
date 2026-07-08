"""Detail boost — unsharp only (resize path removed; it caused halos)."""

from __future__ import annotations

import numpy as np

from auraforge_engine.effects.sharp import unsharp_mask


def upscale_detail(
    rgb: np.ndarray,
    *,
    strength: float = 0.5,
    micro_scale: float = 1.0,  # kept for API compat, ignored
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    t = max(0.0, min(1.0, strength))
    return unsharp_mask(rgb, amount=t * 0.42, radius=0.9 + t * 0.35, threshold=0.005)
