"""Edge-aware detail + micro-upscale sharpening."""

from __future__ import annotations

import cv2
import numpy as np


def upscale_detail(
    rgb: np.ndarray,
    *,
    strength: float = 0.5,
    micro_scale: float = 1.18,
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    t = max(0.0, min(1.0, strength))
    h, w = rgb.shape[:2]
    up_w = max(2, int(round(w * micro_scale)))
    up_h = max(2, int(round(h * micro_scale)))
    up = cv2.resize(rgb, (up_w, up_h), interpolation=cv2.INTER_LANCZOS4)
    down = cv2.resize(up, (w, h), interpolation=cv2.INTER_AREA)

    blur_fine = cv2.GaussianBlur(down, (0, 0), sigmaX=0.8)
    blur_mid = cv2.GaussianBlur(down, (0, 0), sigmaX=2.2)
    blur_coarse = cv2.GaussianBlur(down, (0, 0), sigmaX=5.5)
    detail = (down - blur_fine) * 1.2 + (down - blur_mid) * 0.65 + (down - blur_coarse) * 0.25

    lum = (0.2126 * down[..., 0] + 0.7152 * down[..., 1] + 0.0722 * down[..., 2]).astype(np.float32)
    edge = cv2.Laplacian(lum, cv2.CV_32F, ksize=3)
    edge = np.abs(edge)
    edge = edge / (edge.max() + 1e-6)
    edge = cv2.GaussianBlur(edge, (0, 0), sigmaX=1.0)
    edge_mask = np.clip(edge * 2.2, 0.0, 1.0)[..., None]

    sharpened = down + detail * (1.8 + 1.4 * t) * (0.35 + 0.65 * edge_mask)
    return np.clip(rgb * (1.0 - t * 0.85) + sharpened * t * 0.85, 0.0, None)
