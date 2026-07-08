"""Local contrast / clarity — midtone-safe, single scale."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


def apply_clarity(rgb: np.ndarray, amount: float) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    blur = cv2.GaussianBlur(rgb, (0, 0), sigmaX=2.0)
    detail = rgb - blur
    lum = luminance(rgb)
    mid = np.clip(1.0 - np.abs(lum - 0.45) * 2.0, 0.50, 1.0)[..., None]
    return np.clip(rgb + detail * amount * 1.15 * mid, 0.0, None)
