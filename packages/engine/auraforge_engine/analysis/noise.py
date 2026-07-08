"""Flat-patch noise estimate (high-iso proxy)."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


def noise_estimate(rgb: np.ndarray, tile: int = 32) -> dict:
    lum = luminance(rgb)
    h, w = lum.shape
    best = None
    # find flattest tile by local std
    for y in range(0, max(1, h - tile), tile):
        for x in range(0, max(1, w - tile), tile):
            patch = lum[y : y + tile, x : x + tile]
            if patch.size < tile * tile // 2:
                continue
            std = float(patch.std())
            if best is None or std < best:
                best = std
    if best is None:
        best = float(lum.std())
    # residual high-pass as secondary signal
    blur = cv2.GaussianBlur(lum, (0, 0), 1.2)
    residual = float(np.std(lum - blur))
    score = float(np.clip(0.65 * best + 0.35 * residual, 0.0, 1.0))
    return {
        "noise_flat_std": float(best),
        "noise_residual": residual,
        "noise_score": score,
    }
