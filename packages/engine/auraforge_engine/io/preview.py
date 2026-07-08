"""Preview helpers — keep UI light."""

from __future__ import annotations

import base64

import cv2
import numpy as np


def downscale(rgb: np.ndarray, max_size: int = 1600) -> np.ndarray:
    h, w = rgb.shape[:2]
    scale = min(1.0, max_size / max(h, w))
    if scale >= 1.0:
        return rgb
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    return cv2.resize(rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)


def rgb_to_jpeg_bytes(rgb: np.ndarray, quality: int = 88) -> bytes:
    rgb8 = (np.clip(rgb, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
    bgr = cv2.cvtColor(rgb8, cv2.COLOR_RGB2BGR)
    ok, buf = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, int(quality)])
    if not ok:
        raise ValueError("jpeg encode failed")
    return buf.tobytes()


def rgb_to_data_url(rgb: np.ndarray, quality: int = 88) -> str:
    raw = rgb_to_jpeg_bytes(rgb, quality=quality)
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"
