"""Mild denoise for develop stage."""

from __future__ import annotations

import cv2
import numpy as np


def apply_mild_denoise(rgb: np.ndarray, amount: float) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    rgb8 = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    sigma = 18.0 + amount * 42.0
    denoised = cv2.bilateralFilter(rgb8, d=7, sigmaColor=sigma, sigmaSpace=sigma * 0.45)
    blend = float(np.clip(amount, 0.0, 1.0))
    out8 = cv2.addWeighted(rgb8, 1.0 - blend, denoised, blend, 0)
    return out8.astype(np.float32) / 255.0
