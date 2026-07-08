"""Light dehaze."""

from __future__ import annotations

import cv2
import numpy as np


def apply_dehaze_lite(rgb: np.ndarray, strength: float) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    dark = np.min(rgb, axis=-1)
    blur = cv2.GaussianBlur(dark, (0, 0), sigmaX=15.0)
    transmission = 1.0 - strength * (blur / (float(np.max(blur)) + 1e-6))
    transmission = np.clip(transmission, 0.55, 1.0)
    return np.clip(rgb / transmission[..., None], 0.0, None)
