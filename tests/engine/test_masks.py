"""Mask tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.masks import skin_soft_mask


def _skin_rgb(h: int = 64, w: int = 96) -> np.ndarray:
    rgb = np.full((h, w, 3), 0.25, dtype=np.float32)
    rgb[20:50, 30:70, 0] = 0.82
    rgb[20:50, 30:70, 1] = 0.58
    rgb[20:50, 30:70, 2] = 0.48
    return rgb


def test_skin_soft_mask_hits_face_region() -> None:
    rgb = _skin_rgb()
    mask = skin_soft_mask(rgb)
    assert float(mask[30:45, 40:60].mean()) > float(mask.mean())
