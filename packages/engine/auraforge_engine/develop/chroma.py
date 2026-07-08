"""Chroma-preserving luminance operations."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.histogram import luminance


def relight_preserving_chroma(rgb: np.ndarray, new_lum: np.ndarray) -> np.ndarray:
    old = luminance(rgb)
    scale = np.divide(
        new_lum,
        np.maximum(old, 1e-5),
        out=np.ones_like(old),
        where=old > 1e-5,
    )
    return np.clip(rgb * scale[..., None], 0.0, None)
