"""Midtone contrast."""

from __future__ import annotations

import numpy as np


def apply_contrast(rgb: np.ndarray, amount: float) -> np.ndarray:
    if amount == 0.0:
        return rgb
    pivot = 0.18
    factor = 1.0 + amount
    return np.clip((rgb - pivot) * factor + pivot, 0.0, None)
