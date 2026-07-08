"""Luminance histogram + exposure mass features."""

from __future__ import annotations

import numpy as np


def luminance(rgb: np.ndarray) -> np.ndarray:
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def histogram_features(rgb: np.ndarray, bins: int = 64) -> dict:
    lum = np.clip(luminance(rgb), 0.0, 1.0)
    hist, edges = np.histogram(lum, bins=bins, range=(0.0, 1.0), density=True)
    # mass in shadows / mids / highlights
    centers = 0.5 * (edges[:-1] + edges[1:])
    total = float(hist.sum()) + 1e-8
    shadow = float(hist[centers < 0.25].sum() / total)
    mid = float(hist[(centers >= 0.25) & (centers < 0.75)].sum() / total)
    highlight = float(hist[centers >= 0.75].sum() / total)
    return {
        "mean_luma": float(lum.mean()),
        "median_luma": float(np.median(lum)),
        "p05_luma": float(np.percentile(lum, 5)),
        "p95_luma": float(np.percentile(lum, 95)),
        "shadow_mass": shadow,
        "mid_mass": mid,
        "highlight_mass": highlight,
        "hist": hist.astype(np.float32).tolist(),
    }
