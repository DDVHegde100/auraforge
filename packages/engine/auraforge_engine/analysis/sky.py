"""Sky presence score from color + position heuristics."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


def sky_score(rgb: np.ndarray) -> dict:
    h, w = rgb.shape[:2]
    if h < 8:
        return {"sky_score": 0.0, "sky_detected": False}

    # upper 40% weighted more
    upper_h = max(1, int(h * 0.42))
    upper = rgb[:upper_h, :, :]
    rgb8 = (np.clip(upper, 0.0, 1.0) * 255.0).astype(np.uint8)
    hsv = cv2.cvtColor(rgb8, cv2.COLOR_RGB2HSV)
    hue, sat, val = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    # blue/cyan sky hues in opencv: ~90-130, also light desaturated blues
    blue_hue = ((hue >= 85) & (hue <= 135)).astype(np.float32)
    light = (val >= 100).astype(np.float32)
    low_sat_sky = (sat <= 120).astype(np.float32)
    sky_mask = blue_hue * light * (0.5 + 0.5 * low_sat_sky)

    # penalize high local texture (trees vs open sky)
    lum = luminance(upper)
    blur = cv2.GaussianBlur(lum, (0, 0), 2.0)
    texture = np.abs(lum - blur)
    smooth = 1.0 - np.clip(texture / (texture.mean() + 1e-6), 0.0, 1.5) / 1.5

    score_map = sky_mask * smooth
    score = float(np.clip(score_map.mean() * 1.8, 0.0, 1.0))

    # horizontal band consistency
    row_means = score_map.mean(axis=1)
    top_bias = float(row_means[: max(1, len(row_means) // 3)].mean())
    score = float(np.clip(0.7 * score + 0.3 * top_bias, 0.0, 1.0))

    return {
        "sky_score": score,
        "sky_detected": score >= 0.22,
        "sky_upper_ratio": float(sky_mask.mean()),
    }
