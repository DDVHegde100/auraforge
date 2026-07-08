"""Soft skin mask for local adjustments."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.masks.feather import feather_mask


def skin_soft_mask(rgb: np.ndarray, *, feather_sigma: float = 7.0) -> np.ndarray:
    """Return feathered skin probability mask in [0, 1]."""
    rgb8 = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    hsv = cv2.cvtColor(rgb8, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    ycrcb = cv2.cvtColor(rgb8, cv2.COLOR_RGB2YCrCb)
    cr, cb = ycrcb[..., 1], ycrcb[..., 2]
    ycrcb_skin = ((cr >= 133) & (cr <= 173) & (cb >= 77) & (cb <= 127)).astype(np.float32)
    hsv_skin = (((h <= 25) | (h >= 160)) & (s >= 20) & (v >= 40)).astype(np.float32)
    mask = np.clip(0.65 * ycrcb_skin + 0.35 * hsv_skin, 0.0, 1.0)
    return feather_mask(mask, sigma=feather_sigma)
