"""Luminance-first denoise — edges preserved."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance
from auraforge_engine.develop.chroma import relight_preserving_chroma


def apply_denoise_pro(
    rgb: np.ndarray,
    *,
    luma: float = 0.0,
    color: float = 0.0,
) -> np.ndarray:
    if luma <= 0.0 and color <= 0.0:
        return rgb

    out = rgb.astype(np.float32, copy=True)
    if luma > 0.0:
        lum = luminance(out)
        lum8 = (np.clip(lum, 0.0, 1.0) * 255.0).astype(np.uint8)
        sigma = 12.0 + luma * 38.0
        den = cv2.bilateralFilter(lum8, d=5, sigmaColor=sigma, sigmaSpace=sigma * 0.55)
        den_f = den.astype(np.float32) / 255.0
        blend = float(np.clip(luma, 0.0, 1.0))
        new_lum = lum * (1.0 - blend) + den_f * blend
        out = relight_preserving_chroma(out, new_lum)

    if color > 0.0:
        rgb8 = (np.clip(out, 0.0, 1.0) * 255.0).astype(np.uint8)
        sigma = 10.0 + color * 28.0
        den = cv2.bilateralFilter(rgb8, d=5, sigmaColor=sigma, sigmaSpace=sigma * 0.4)
        blend = float(np.clip(color, 0.0, 0.65))
        out8 = cv2.addWeighted(rgb8, 1.0 - blend, den, blend, 0)
        out = out8.astype(np.float32) / 255.0

    return out
