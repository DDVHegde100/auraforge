"""Skin tone presence score (portrait helper)."""

from __future__ import annotations

import cv2
import numpy as np


def skin_score(rgb: np.ndarray) -> dict:
    rgb8 = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    hsv = cv2.cvtColor(rgb8, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    # ycrcb often better for skin — blend with hsv
    ycrcb = cv2.cvtColor(rgb8, cv2.COLOR_RGB2YCrCb)
    cr, cb = ycrcb[..., 1], ycrcb[..., 2]
    ycrcb_skin = ((cr >= 133) & (cr <= 173) & (cb >= 77) & (cb <= 127)).astype(np.float32)

    hsv_skin = (((h <= 25) | (h >= 160)) & (s >= 20) & (v >= 40)).astype(np.float32)
    mask = np.clip(0.6 * ycrcb_skin + 0.4 * hsv_skin, 0.0, 1.0)

    h_img, w_img = mask.shape
    cy0, cy1 = int(h_img * 0.12), int(h_img * 0.88)
    cx0, cx1 = int(w_img * 0.15), int(w_img * 0.85)
    center = float(mask[cy0:cy1, cx0:cx1].mean())
    global_ratio = float(mask.mean())

    score = float(np.clip(center * 0.65 + global_ratio * 0.35, 0.0, 1.0))
    return {
        "skin_score": score,
        "skin_detected": score >= 0.08,
        "skin_center_ratio": center,
        "skin_global_ratio": global_ratio,
    }
