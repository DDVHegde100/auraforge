"""Soft algorithmic sky mask."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


def sky_mask(rgb: np.ndarray) -> np.ndarray:
    """Return float mask in [0, 1] where 1 ≈ sky."""
    h, w = rgb.shape[:2]
    if h < 8:
        return np.zeros((h, w), dtype=np.float32)

    rgb8 = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    hsv = cv2.cvtColor(rgb8, cv2.COLOR_RGB2HSV)
    hue, sat, val = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    blue_hue = ((hue >= 85) & (hue <= 135)).astype(np.float32)
    light = np.clip((val.astype(np.float32) - 80.0) / 120.0, 0.0, 1.0)
    low_sat = np.clip(1.0 - sat.astype(np.float32) / 140.0, 0.0, 1.0)
    color_mask = blue_hue * (0.35 + 0.65 * light) * (0.45 + 0.55 * low_sat)

    lum = luminance(rgb)
    blur = cv2.GaussianBlur(lum, (0, 0), 2.5)
    texture = np.abs(lum - blur)
    smooth = 1.0 - np.clip(texture / (texture.mean() + 1e-6), 0.0, 1.8) / 1.8

    y = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    top_bias = np.clip(1.15 - y * 1.1, 0.0, 1.0)

    mask = color_mask * smooth * top_bias
    return np.clip(mask, 0.0, 1.0).astype(np.float32)
