"""Guess scene content: portrait / landscape / food / general."""

from __future__ import annotations

from enum import Enum

import numpy as np

from auraforge_engine.analysis.color import color_stats
from auraforge_engine.analysis.histogram import luminance


class ContentClass(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    FOOD = "food"
    GENERAL = "general"


def _skin_mask_hsv(rgb: np.ndarray) -> np.ndarray:
    rgb8 = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    import cv2

    hsv = cv2.cvtColor(rgb8, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # broad skin range
    m1 = (h <= 25) & (s >= 20) & (v >= 40)
    m2 = (h >= 160) & (s >= 20) & (v >= 40)
    return (m1 | m2).astype(np.float32)


def guess_content(rgb: np.ndarray) -> dict:
    h, w = rgb.shape[:2]
    aspect = w / max(h, 1)
    stats = color_stats(rgb)
    skin = _skin_mask_hsv(rgb)

    # center-weighted skin (portrait cue)
    cy0, cy1 = int(h * 0.15), int(h * 0.85)
    cx0, cx1 = int(w * 0.2), int(w * 0.8)
    center_skin = float(skin[cy0:cy1, cx0:cx1].mean())
    global_skin = float(skin.mean())

    # upper band blue-ish (landscape / sky cue) — rough without full sky module
    upper = rgb[: max(1, h // 3), :, :]
    upper_hsv = np.array(upper)
    lum_u = luminance(upper)
    blue_bias = float(upper[..., 2].mean() - upper[..., 0].mean())

    # food: warm + saturated mids
    warmth = float(rgb[..., 0].mean() - rgb[..., 2].mean())
    sat = stats["sat_mean"]

    scores = {
        ContentClass.PORTRAIT.value: center_skin * 2.2 + global_skin * 0.8 + (0.2 if aspect < 1.1 else 0.0),
        ContentClass.LANDSCAPE.value: (0.35 if aspect > 1.25 else 0.0)
        + max(0.0, blue_bias) * 1.5
        + float(lum_u.mean()) * 0.3,
        ContentClass.FOOD.value: warmth * 1.2 + sat * 1.5 + (0.25 if 0.8 <= aspect <= 1.4 else 0.0),
        ContentClass.GENERAL.value: 0.15,
    }
    best = max(scores, key=scores.get)  # type: ignore[arg-type]
    total = sum(scores.values()) + 1e-8
    confidence = float(scores[best] / total)

    return {
        "content_class": best,
        "content_confidence": confidence,
        "content_scores": {k: float(v) for k, v in scores.items()},
        "center_skin_ratio": center_skin,
    }
