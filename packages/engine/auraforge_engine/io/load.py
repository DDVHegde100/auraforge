"""Load common image formats into float32 RGB [0, 1]."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

JPEG_PNG = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG", ".webp", ".WEBP"}


def load_jpeg_png(path: Path | str) -> np.ndarray:
    path = Path(path)
    if path.suffix not in JPEG_PNG:
        raise ValueError(f"not jpeg/png: {path.suffix}")
    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError(f"could not read {path}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return rgb.astype(np.float32) / 255.0


def load_rgb(path: Path | str) -> np.ndarray:
    path = Path(path)
    if path.suffix in JPEG_PNG:
        return load_jpeg_png(path)
    raise ValueError(f"unsupported type: {path.suffix}")
