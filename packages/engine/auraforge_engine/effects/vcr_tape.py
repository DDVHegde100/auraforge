"""VHS / VCR tape aesthetic — scanlines, softness, tracking noise."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.effects.fringe import channel_offset_fringe


def vcr_tape(
    rgb: np.ndarray,
    *,
    scanline_strength: float = 0.14,
    softness: float = 0.28,
    tracking_noise: float = 0.035,
    chroma_bleed: float = 0.16,
    desaturate: float = 0.12,
    seed: int = 7,
) -> np.ndarray:
    out = rgb.astype(np.float32, copy=True)
    if softness > 0:
        blur = cv2.GaussianBlur(out, (0, 0), sigmaX=softness * 2.5)
        out = out * (1.0 - softness) + blur * softness
    if desaturate > 0:
        lum = 0.2126 * out[..., 0] + 0.7152 * out[..., 1] + 0.0722 * out[..., 2]
        out = out * (1.0 - desaturate) + lum[..., None] * desaturate
    if scanline_strength > 0:
        h = out.shape[0]
        mask = np.ones((h, 1, 1), dtype=np.float32)
        mask[1::2] = 1.0 - scanline_strength
        out = out * mask
    if tracking_noise > 0:
        rng = np.random.default_rng(seed)
        h, w = out.shape[:2]
        bands = rng.normal(0.0, tracking_noise, (max(1, h // 8), w)).astype(np.float32)
        bands = cv2.resize(bands, (w, h), interpolation=cv2.INTER_LINEAR)
        out = out + bands[..., None]
    if chroma_bleed > 0:
        out = channel_offset_fringe(
            out,
            red_offset=(0, 2),
            blue_offset=(0, -2),
            strength=chroma_bleed,
        )
    return np.clip(out, 0.0, None)
