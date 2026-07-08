"""Warmth and tint."""

from __future__ import annotations

import numpy as np


def apply_warmth_tint(
    rgb: np.ndarray,
    *,
    warmth: float = 0.0,
    tint: float = 0.0,
) -> np.ndarray:
    if warmth == 0.0 and tint == 0.0:
        return rgb
    out = rgb.copy()
    out[..., 0] += warmth * 0.08
    out[..., 2] -= warmth * 0.06
    out[..., 1] += tint * 0.05
    return np.clip(out, 0.0, None)
