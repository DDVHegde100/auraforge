"""Lab-ish stats + contrast + saturation (lightweight, opencv)."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


def color_stats(rgb: np.ndarray) -> dict:
    rgb8 = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    lab = cv2.cvtColor(rgb8, cv2.COLOR_RGB2LAB).astype(np.float32)
    # opencv L:0-255, a/b:0-255 centered ~128
    L, a, b = lab[..., 0], lab[..., 1] - 128.0, lab[..., 2] - 128.0
    lum = luminance(rgb)
    sat = _saturation(rgb)
    return {
        "lab_L_mean": float(L.mean() / 255.0),
        "lab_a_mean": float(a.mean()),
        "lab_b_mean": float(b.mean()),
        "contrast_std": float(lum.std()),
        "local_rms": float(_local_rms(lum)),
        "sat_mean": float(sat.mean()),
        "sat_p95": float(np.percentile(sat, 95)),
    }


def _saturation(rgb: np.ndarray) -> np.ndarray:
    mx = rgb.max(axis=-1)
    mn = rgb.min(axis=-1)
    return np.where(mx > 1e-6, (mx - mn) / mx, 0.0)


def _local_rms(lum: np.ndarray, k: int = 7) -> float:
    blur = cv2.GaussianBlur(lum, (k | 1, k | 1), 0)
    return float(np.sqrt(np.mean((lum - blur) ** 2)))
