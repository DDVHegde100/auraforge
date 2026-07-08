"""Feather binary/soft masks."""

from __future__ import annotations

import cv2
import numpy as np


def feather_mask(mask: np.ndarray, sigma: float = 8.0) -> np.ndarray:
    if sigma <= 0.0:
        return np.clip(mask, 0.0, 1.0).astype(np.float32)
    blurred = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), sigmaX=sigma)
    return np.clip(blurred, 0.0, 1.0)
