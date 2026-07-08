"""Structured film grain — luminance-dependent, per-channel, ISO-aware."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


def grain_pro(
    rgb: np.ndarray,
    *,
    amount: float = 0.10,
    iso: float = 400.0,
    color: float = 0.32,
    size: float = 1.0,
    seed: int = 42,
) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    h, w = rgb.shape[:2]
    rng = np.random.default_rng(seed)
    iso_scale = float(np.sqrt(max(iso, 50.0) / 400.0))
    lum = luminance(rgb)
    # More grain in shadows (film emulsion behavior)
    weight = (0.55 + 0.85 * (1.0 - lum)) * iso_scale * amount

    mono = rng.normal(0.0, 1.0, (h, w)).astype(np.float32)
    if size > 1.0:
        k = int(size * 2) | 1
        mono = cv2.GaussianBlur(mono, (k, k), sigmaX=size * 0.85)

    chroma_r = rng.normal(0.0, color, (h, w)).astype(np.float32) if color > 0 else np.zeros((h, w), np.float32)
    chroma_b = rng.normal(0.0, color * 0.85, (h, w)).astype(np.float32) if color > 0 else np.zeros((h, w), np.float32)

    noise = np.stack([mono + chroma_r, mono, mono + chroma_b], axis=-1)
    return np.clip(rgb + noise * weight[..., None], 0.0, None)
