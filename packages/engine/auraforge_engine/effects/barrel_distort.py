"""Barrel / pincushion distortion for toy cameras and compacts."""

from __future__ import annotations

import cv2
import numpy as np


def barrel_distort(
    rgb: np.ndarray,
    *,
    k1: float = 0.12,
    k2: float = 0.0,
    strength: float = 1.0,
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    h, w = rgb.shape[:2]
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (x - cx) / max(cx, 1.0)
    ny = (y - cy) / max(cy, 1.0)
    r2 = nx * nx + ny * ny
    k = k1 * strength
    k22 = k2 * strength
    factor = 1.0 + k * r2 + k22 * r2 * r2
    map_x = (nx * factor * cx + cx).astype(np.float32)
    map_y = (ny * factor * cy + cy).astype(np.float32)
    return cv2.remap(rgb, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT101)
