"""RGB channel offset / creative fringe."""

from __future__ import annotations

import numpy as np


def _shift_2d(ch: np.ndarray, dy: int, dx: int) -> np.ndarray:
    h, w = ch.shape
    out = np.zeros_like(ch)
    y0, y1 = max(0, dy), h + min(0, dy)
    x0, x1 = max(0, dx), w + min(0, dx)
    sy0, sy1 = max(0, -dy), h - max(0, dy)
    sx0, sx1 = max(0, -dx), w - max(0, dx)
    out[y0:y1, x0:x1] = ch[sy0:sy1, sx0:sx1]
    return out


def channel_offset_fringe(
    rgb: np.ndarray,
    *,
    red_offset: tuple[int, int] = (2, 0),
    blue_offset: tuple[int, int] = (-2, 0),
    strength: float = 0.18,
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    r = _shift_2d(rgb[..., 0], red_offset[0], red_offset[1])
    g = rgb[..., 1]
    b = _shift_2d(rgb[..., 2], blue_offset[0], blue_offset[1])
    shifted = np.stack([r, g, b], axis=-1)
    return np.clip(rgb * (1.0 - strength) + shifted * strength, 0.0, 1.0)
