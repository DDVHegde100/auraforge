"""Exposure adjustment."""

from __future__ import annotations

import numpy as np


def apply_exposure_stops(rgb: np.ndarray, stops: float) -> np.ndarray:
    if stops == 0.0:
        return rgb
    return rgb * (2.0**stops)
