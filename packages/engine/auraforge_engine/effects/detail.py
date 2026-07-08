"""Multi-scale local detail enhancement."""

from __future__ import annotations

import cv2
import numpy as np


def multiscale_detail(
    rgb: np.ndarray,
    *,
    strength: float = 0.18,
    sigmas: tuple[float, ...] = (1.5, 4.0, 10.0),
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    detail = np.zeros_like(rgb)
    weights = (0.5, 0.35, 0.15)
    for sigma, weight in zip(sigmas, weights):
        blur = cv2.GaussianBlur(rgb, (0, 0), sigmaX=sigma)
        detail += (rgb - blur) * weight
    return np.clip(rgb + detail * strength * 2.2, 0.0, None)
