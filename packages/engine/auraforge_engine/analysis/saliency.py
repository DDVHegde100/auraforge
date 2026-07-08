"""Cheap center + contrast saliency proxy."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


def center_saliency(rgb: np.ndarray) -> dict:
    lum = luminance(rgb)
    h, w = lum.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
    dist = np.sqrt(((yy - cy) / max(h, 1)) ** 2 + ((xx - cx) / max(w, 1)) ** 2)
    center_w = np.clip(1.0 - dist * 1.6, 0.0, 1.0)

    blur = cv2.GaussianBlur(lum, (0, 0), 3.0)
    contrast = np.abs(lum - blur)
    contrast = contrast / (contrast.max() + 1e-6)

    sal = center_w * (0.45 + 0.55 * contrast)
    # focus of mass
    mass = sal.sum() + 1e-8
    fy = float((sal * yy).sum() / mass / max(h - 1, 1))
    fx = float((sal * xx).sum() / mass / max(w - 1, 1))
    return {
        "saliency_center": float(sal[int(cy), int(cx)]),
        "saliency_mean": float(sal.mean()),
        "saliency_focus_x": fx,
        "saliency_focus_y": fy,
    }
