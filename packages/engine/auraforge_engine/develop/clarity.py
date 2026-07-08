"""Local contrast / clarity."""

from __future__ import annotations

import cv2
import numpy as np


def apply_clarity(rgb: np.ndarray, amount: float) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    blur = cv2.GaussianBlur(rgb, (0, 0), sigmaX=2.5)
    detail = rgb - blur
    return np.clip(rgb + detail * amount, 0.0, None)
