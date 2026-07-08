"""Rim / edge light from luminance edges."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


def rim_light(
    rgb: np.ndarray,
    *,
    intensity: float = 0.25,
    blur_sigma: float = 1.2,
    tint: tuple[float, float, float] = (1.0, 0.95, 0.82),
) -> np.ndarray:
    if intensity <= 0.0:
        return rgb
    lum = luminance(rgb)
    blur = cv2.GaussianBlur(lum, (0, 0), sigmaX=blur_sigma)
    edge = np.clip(lum - blur, 0.0, None)
    edge = edge / (edge.max() + 1e-6)
    edge = cv2.GaussianBlur(edge, (0, 0), sigmaX=0.8)
    tint_rgb = np.array(tint, dtype=np.float32)
    add = edge[..., None] * tint_rgb * intensity
    return np.clip(rgb + add, 0.0, None)
