"""AI selective HSL — uses unified masks when available."""

from __future__ import annotations

from typing import Any

import cv2
import numpy as np

from auraforge_engine.masks.build import MaskPack


def apply_hsl_selective(
    rgb: np.ndarray,
    analysis: dict[str, Any],
    *,
    strength: float = 0.5,
    masks: MaskPack | None = None,
) -> np.ndarray:
    t = max(0.0, min(1.0, strength))
    if t <= 0.0:
        return rgb

    rgb8 = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    hsv = cv2.cvtColor(rgb8, cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    sky_score = float(analysis.get("sky", {}).get("sky_score", 0.0))
    skin_score = float(analysis.get("skin", {}).get("skin_score", 0.0))
    content = analysis.get("content", {}).get("content_class", "general")

    sat = s.copy()
    val = v.copy()

    if masks is not None and sky_score > 0.12:
        sky_m = masks.sky * t
        sat = sat + sky_m * (16.0 + sky_score * 24.0)
        val = val + sky_m * (6.0 + sky_score * 12.0) * 0.4
    elif sky_score > 0.18:
        sky_m = np.clip(1.0 - np.abs(h - 105.0) / 35.0, 0.0, 1.0) ** 1.4
        sky_m *= np.clip((v - 80.0) / 120.0, 0.0, 1.0) * t
        sat = sat + sky_m * (18.0 + sky_score * 22.0)
        val = val + sky_m * (8.0 + sky_score * 10.0) * 0.35

    if masks is not None and (content == "landscape" or sky_score > 0.22):
        sat = sat + masks.foliage * 14.0 * t
    elif content == "landscape" or sky_score > 0.25:
        green_m = np.clip(1.0 - np.abs(h - 55.0) / 28.0, 0.0, 1.0) ** 1.3
        green_m *= np.clip(s / 180.0, 0.0, 1.0) * t
        sat = sat + green_m * 16.0

    if masks is not None and skin_score > 0.06:
        skin_m = masks.skin * t
        sat = sat - skin_m * np.clip(sat - 138.0, 0.0, 85.0) * 0.38
        val = val - skin_m * np.clip(val - 208.0, 0.0, 48.0) * 0.28
    elif skin_score > 0.08:
        skin_m = np.clip(1.0 - np.abs(h - 12.0) / 18.0, 0.0, 1.0) ** 1.5
        skin_m *= np.clip(s / 160.0, 0.0, 1.0) * t
        sat = sat - skin_m * np.clip(sat - 140.0, 0.0, 80.0) * 0.35
        val = val - skin_m * np.clip(val - 210.0, 0.0, 45.0) * 0.25

    if content == "food":
        warm_m = np.clip(1.0 - np.abs(h - 18.0) / 22.0, 0.0, 1.0) * t
        sat = sat + warm_m * 20.0

    hsv_out = np.stack([h, np.clip(sat, 0.0, 255.0), np.clip(val, 0.0, 255.0)], axis=-1).astype(np.uint8)
    rgb8_out = cv2.cvtColor(hsv_out, cv2.COLOR_HSV2RGB)
    return rgb8_out.astype(np.float32) / 255.0
