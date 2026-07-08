"""Orton glow creative effect."""

from __future__ import annotations

import cv2
import numpy as np


def blend_screen(base: np.ndarray, layer: np.ndarray, opacity: float) -> np.ndarray:
    out = 1.0 - (1.0 - base) * (1.0 - layer)
    return base * (1.0 - opacity) + out * opacity


def blend_soft_light(base: np.ndarray, layer: np.ndarray, opacity: float) -> np.ndarray:
    d = np.where(
        layer <= 0.5,
        2.0 * base * layer + base**2 * (1.0 - 2.0 * layer),
        2.0 * base * (1.0 - layer) + np.sqrt(np.clip(base, 0.0, 1.0)) * (2.0 * layer - 1.0),
    )
    return base * (1.0 - opacity) + d * opacity


def orton_glow(
    rgb: np.ndarray,
    *,
    blur_sigma: float = 28.0,
    opacity: float = 0.45,
    blend_mode: str = "screen",
) -> np.ndarray:
    if opacity <= 0.0:
        return rgb
    blurred = cv2.GaussianBlur(rgb, (0, 0), sigmaX=blur_sigma)
    if blend_mode == "soft_light":
        return blend_soft_light(rgb, blurred, opacity)
    return blend_screen(rgb, blurred, opacity)
