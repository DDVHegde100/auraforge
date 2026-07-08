"""RGB ↔ Lab helpers (OpenCV D65)."""

from __future__ import annotations

import cv2
import numpy as np


def rgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    rgb8 = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    return cv2.cvtColor(rgb8, cv2.COLOR_RGB2LAB).astype(np.float32)


def lab_to_rgb(lab: np.ndarray) -> np.ndarray:
    lab8 = np.clip(lab, 0.0, 255.0).astype(np.uint8)
    rgb8 = cv2.cvtColor(lab8, cv2.COLOR_LAB2RGB)
    return rgb8.astype(np.float32) / 255.0
