"""Mask tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.masks import sky_mask


def _sky_rgb(h: int = 64, w: int = 96) -> np.ndarray:
    rgb = np.zeros((h, w, 3), dtype=np.float32)
    rgb[: h // 2, :, 0] = 0.35
    rgb[: h // 2, :, 1] = 0.55
    rgb[: h // 2, :, 2] = 0.95
    rgb[h // 2 :, :, :] = 0.25
    return rgb


def test_sky_mask_high_in_upper_band() -> None:
    rgb = _sky_rgb()
    mask = sky_mask(rgb)
    assert float(mask[:16, :].mean()) > float(mask[-16:, :].mean())


from auraforge_engine.masks import feather_mask


def test_feather_softens_edges() -> None:
    hard = np.zeros((32, 32), dtype=np.float32)
    hard[:16, :] = 1.0
    soft = feather_mask(hard, sigma=6.0)
    assert float(soft[15, 16]) > 0.0
    assert float(soft[15, 16]) < 1.0
