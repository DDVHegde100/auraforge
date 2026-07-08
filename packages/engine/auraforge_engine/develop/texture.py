"""Fine texture — medium-high frequency (Lightroom Texture analog)."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance
from auraforge_engine.develop.chroma import relight_preserving_chroma


def apply_texture(rgb: np.ndarray, amount: float) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    lum = luminance(rgb).astype(np.float32)
    blur_f = cv2.GaussianBlur(lum, (0, 0), sigmaX=0.9)
    blur_m = cv2.GaussianBlur(lum, (0, 0), sigmaX=2.4)
    detail = (lum - blur_f) * 0.72 + (lum - blur_m) * 0.28
    mid = np.clip(1.0 - np.abs(lum - 0.42) * 2.4, 0.30, 1.0)
    new_lum = lum + detail * amount * 1.35 * mid
    return relight_preserving_chroma(rgb, np.clip(new_lum, 0.0, None))
