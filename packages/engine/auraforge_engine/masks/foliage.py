"""Foliage / greenery mask for landscape selective color."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance
from auraforge_engine.masks.feather import feather_mask


def foliage_mask(rgb: np.ndarray) -> np.ndarray:
    rgb8 = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    hsv = cv2.cvtColor(rgb8, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0].astype(np.float32), hsv[..., 1].astype(np.float32), hsv[..., 2].astype(np.float32)

    green = np.clip(1.0 - np.abs(h - 52.0) / 32.0, 0.0, 1.0) ** 1.35
    sat_w = np.clip(s / 160.0, 0.0, 1.0)
    val_w = np.clip(v / 220.0, 0.0, 1.0)

    lum = luminance(rgb)
    texture = np.abs(lum - cv2.GaussianBlur(lum, (0, 0), sigmaX=2.0))
    detail = np.clip(texture / (texture.mean() + 1e-6), 0.0, 2.0) / 2.0

    mask = green * sat_w * val_w * (0.55 + 0.45 * detail)
    return feather_mask(mask.astype(np.float32), sigma=6.0)
