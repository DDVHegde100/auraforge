"""Mask pack tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.masks.build import build_masks
from auraforge_engine.masks.foliage import foliage_mask


def _sky_rgb(h: int = 64, w: int = 96) -> np.ndarray:
    rgb = np.zeros((h, w, 3), dtype=np.float32)
    rgb[: h // 2, :, 0] = 0.35
    rgb[: h // 2, :, 1] = 0.55
    rgb[: h // 2, :, 2] = 0.95
    rgb[h // 2 :, :, :] = 0.25
    return rgb


def test_build_masks_pack() -> None:
    rgb = _sky_rgb()
    pack = build_masks(rgb)
    assert pack.sky.shape == rgb.shape[:2]
    assert float(pack.sky[:16].mean()) > float(pack.sky[-16:].mean())
    assert pack.sky_source == "heuristic"


def test_foliage_mask_on_green() -> None:
    rgb = np.full((48, 64, 3), 0.2, dtype=np.float32)
    rgb[..., 1] = 0.55
    mask = foliage_mask(rgb)
    assert float(mask.mean()) > 0.05
