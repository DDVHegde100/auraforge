"""Capture sharpening — luminance-only with edge + skin protection."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance
from auraforge_engine.develop.chroma import relight_preserving_chroma


def apply_capture_sharpen(
    rgb: np.ndarray,
    amount: float,
    *,
    radius: float | None = None,
    masking: float = 0.72,
    protect_mask: np.ndarray | None = None,
) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    h, w = rgb.shape[:2]
    rad = radius if radius is not None else max(0.7, min(h, w) / 2200.0)

    lum = luminance(rgb).astype(np.float32)
    blur = cv2.GaussianBlur(lum, (0, 0), sigmaX=rad)
    detail = lum - blur

    smooth = cv2.GaussianBlur(lum, (0, 0), sigmaX=3.2)
    local = np.abs(lum - smooth)
    mask = np.clip(local / 0.022, 0.0, 1.0) ** (1.0 / max(0.15, masking))

    if protect_mask is not None:
        protect = np.clip(protect_mask, 0.0, 1.0)
        mask = mask * (1.0 - protect * 0.72)

    new_lum = lum + detail * amount * 2.2 * mask
    return relight_preserving_chroma(rgb, np.clip(new_lum, 0.0, None))
