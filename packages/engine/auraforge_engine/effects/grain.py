"""Film grain overlay."""

from __future__ import annotations

import cv2
import numpy as np


def film_grain(
    rgb: np.ndarray,
    *,
    amount: float = 0.08,
    size: float = 1.0,
    seed: int = 42,
) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    h, w = rgb.shape[:2]
    noise = np.random.default_rng(seed).normal(0.0, amount, (h, w)).astype(np.float32)
    if size > 1.0:
        k = int(size * 2) | 1
        noise = cv2.GaussianBlur(noise, (k, k), sigmaX=size)
    return np.clip(rgb + noise[..., None], 0.0, None)
