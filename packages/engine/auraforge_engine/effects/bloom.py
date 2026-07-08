"""Highlight bloom."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


def highlight_bloom(
    rgb: np.ndarray,
    *,
    threshold: float = 0.72,
    blur_sigma: float = 18.0,
    intensity: float = 0.35,
) -> np.ndarray:
    if intensity <= 0.0:
        return rgb
    lum = luminance(rgb)
    mask = np.clip((lum - threshold) / max(1.0 - threshold, 1e-6), 0.0, 1.0)
    mask = cv2.GaussianBlur(mask, (0, 0), sigmaX=blur_sigma * 0.5)
    bloom_layer = cv2.GaussianBlur(rgb * mask[..., None], (0, 0), sigmaX=blur_sigma)
    return np.clip(rgb + bloom_layer * intensity, 0.0, None)
