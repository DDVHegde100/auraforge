"""Simple white balance estimators."""

from __future__ import annotations

import numpy as np


def grey_world_gains(rgb: np.ndarray) -> dict:
    means = rgb.reshape(-1, 3).mean(axis=0) + 1e-6
    gray = float(means.mean())
    gains = gray / means
    return {
        "gw_gain_r": float(gains[0]),
        "gw_gain_g": float(gains[1]),
        "gw_gain_b": float(gains[2]),
        "gw_temp_bias": float(gains[0] - gains[2]),  # + warm, - cool
    }


def white_patch_gains(rgb: np.ndarray, percentile: float = 99.0) -> dict:
    flat = rgb.reshape(-1, 3)
    # average of brightest pixels per channel independently
    thr = np.percentile(flat, percentile, axis=0)
    bright = flat[(flat >= thr).all(axis=1)]
    if len(bright) < 8:
        bright = flat[np.argsort(flat.mean(axis=1))[-max(8, len(flat) // 200) :]]
    means = bright.mean(axis=0) + 1e-6
    mx = float(means.max())
    gains = mx / means
    return {
        "wp_gain_r": float(gains[0]),
        "wp_gain_g": float(gains[1]),
        "wp_gain_b": float(gains[2]),
        "wp_temp_bias": float(gains[0] - gains[2]),
    }


def wb_features(rgb: np.ndarray) -> dict:
    out = {}
    out.update(grey_world_gains(rgb))
    out.update(white_patch_gains(rgb))
    # consensus warmth score
    out["warmth"] = float(0.5 * (out["gw_temp_bias"] + out["wp_temp_bias"]))
    return out
