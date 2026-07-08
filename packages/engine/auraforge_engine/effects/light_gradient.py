"""Floating light gradient overlay."""

from __future__ import annotations

import numpy as np


def floating_light_gradient(
    rgb: np.ndarray,
    *,
    angle_deg: float = 35.0,
    intensity: float = 0.22,
    warmth: float = 0.12,
    falloff: float = 1.6,
) -> np.ndarray:
    if intensity <= 0.0:
        return rgb
    h, w = rgb.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    x = x / max(w - 1, 1)
    y = y / max(h - 1, 1)
    rad = np.deg2rad(angle_deg)
    proj = x * np.cos(rad) + y * np.sin(rad)
    grad = np.clip((proj - 0.15) / 0.85, 0.0, 1.0) ** falloff
    tint = np.array([1.0, 0.92 + warmth * 0.3, 0.78 - warmth * 0.2], dtype=np.float32)
    glow = grad[..., None] * tint * intensity
    return np.clip(rgb + glow * (1.0 - rgb * 0.35), 0.0, None)
