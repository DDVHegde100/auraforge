"""Export float RGB [0,1] images."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def export_jpeg(rgb: np.ndarray, path: Path | str, quality: int = 92) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rgb8 = (np.clip(rgb, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)
    bgr = cv2.cvtColor(rgb8, cv2.COLOR_RGB2BGR)
    ok = cv2.imwrite(str(path), bgr, [cv2.IMWRITE_JPEG_QUALITY, int(quality)])
    if not ok:
        raise ValueError(f"could not write jpeg {path}")
