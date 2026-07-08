"""Soft algorithmic sky mask — blue, cyan, sunset, and bright overcast."""

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
    warm_hue = ((hue >= 4) & (hue <= 32)).astype(np.float32)
    light = np.clip((val.astype(np.float32) - 70.0) / 130.0, 0.0, 1.0)
    low_sat = np.clip(1.0 - sat.astype(np.float32) / 150.0, 0.0, 1.0)

    blue_sky = blue_hue * (0.35 + 0.65 * light) * (0.40 + 0.60 * low_sat)
    sunset_sky = warm_hue * np.clip(sat.astype(np.float32) / 120.0, 0.0, 1.0) * light
    bright_overcast = low_sat * light * (1.0 - blue_hue * 0.5)

    color_mask = np.clip(blue_sky + sunset_sky * 0.85 + bright_overcast * 0.55, 0.0, 1.0)

    lum = luminance(rgb)
    blur = cv2.GaussianBlur(lum, (0, 0), 2.5)
    texture = np.abs(lum - blur)
    smooth = 1.0 - np.clip(texture / (texture.mean() + 1e-6), 0.0, 1.8) / 1.8

    y = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    top_bias = np.clip(1.18 - y * 1.05, 0.0, 1.0) ** 1.05

    mask = color_mask * smooth * top_bias

    # Clean speckle + expand coherent sky regions
    mask8 = (np.clip(mask, 0.0, 1.0) * 255.0).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask8 = cv2.morphologyEx(mask8, cv2.MORPH_CLOSE, kernel)
    mask8 = cv2.morphologyEx(mask8, cv2.MORPH_OPEN, kernel)
    mask = mask8.astype(np.float32) / 255.0

    # Suppress obvious foreground (dark textured bottom)
    ground = (1.0 - top_bias) * np.clip(texture / (texture.mean() + 1e-6), 0.0, 2.0) / 2.0
    mask = mask * (1.0 - ground * 0.65)

    return np.clip(mask, 0.0, 1.0).astype(np.float32)
