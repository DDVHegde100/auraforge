"""Multi-scale local detail enhancement."""

from __future__ import annotations

import cv2
import numpy as np


def multiscale_detail(
    rgb: np.ndarray,
    *,
    strength: float = 0.18,
    sigmas: tuple[float, ...] = (0.8, 2.0, 5.0, 12.0),
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    detail = np.zeros_like(rgb)
    weights = (0.38, 0.28, 0.22, 0.12)
    for sigma, weight in zip(sigmas, weights):
        blur = cv2.GaussianBlur(rgb, (0, 0), sigmaX=sigma)
        detail += (rgb - blur) * weight
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).astype(np.float32)
    edge = cv2.Laplacian(lum, cv2.CV_32F, ksize=3)
    edge = np.clip(np.abs(edge) * 3.0, 0.0, 1.0)[..., None]
    boost = 1.0 + edge * 0.6
    return np.clip(rgb + detail * strength * 2.8 * boost, 0.0, None)
