"""Radial chromatic aberration — strong lens fringe."""

from __future__ import annotations

import cv2
import numpy as np


def chromatic_aberration(
    rgb: np.ndarray,
    *,
    strength: float = 0.22,
    radial_power: float = 1.4,
    max_shift: float = 3.5,
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    h, w = rgb.shape[:2]
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (x - cx) / max(cx, 1.0)
    ny = (y - cy) / max(cy, 1.0)
    radius = np.sqrt(nx * nx + ny * ny)
    shift = (radius**radial_power) * max_shift * strength

    def _radial_shift(channel: np.ndarray, sign: float) -> np.ndarray:
        dx = nx * shift * sign
        dy = ny * shift * sign
        map_x = np.clip(x + dx, 0, w - 1).astype(np.float32)
        map_y = np.clip(y + dy, 0, h - 1).astype(np.float32)
        return cv2.remap(channel, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)

    r = _radial_shift(rgb[..., 0], 1.0)
    g = rgb[..., 1]
    b = _radial_shift(rgb[..., 2], -1.0)
    return np.clip(np.stack([r, g, b], axis=-1), 0.0, None)
