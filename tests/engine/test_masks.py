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


from auraforge_engine.masks import apply_skin_protect, skin_soft_mask


def test_skin_protect_blends_toward_original() -> None:
    rgb = _skin_rgb()
    enhanced = np.clip(rgb * 1.4, 0.0, 1.0)
    skin = skin_soft_mask(rgb)
    out = apply_skin_protect(enhanced, rgb, skin, strength=0.8)
    diff_enh = float(np.abs(enhanced - rgb).mean())
    diff_out = float(np.abs(out - rgb).mean())
    assert diff_out < diff_enh


from auraforge_engine.masks import apply_subject_lightness, subject_mask


def test_subject_mask_nonzero_on_portrait() -> None:
    rgb = _skin_rgb()
    skin = skin_soft_mask(rgb)
    subj = subject_mask(rgb, skin)
    assert float(subj.max()) > 0.2


def test_subject_lightness_lifts_masked_area() -> None:
    rgb = np.full((32, 32, 3), 0.3, dtype=np.float32)
    mask = np.zeros((32, 32), dtype=np.float32)
    mask[10:22, 10:22] = 1.0
    out = apply_subject_lightness(rgb, mask, amount=0.15)
    assert float(out[15, 15].mean()) > float(rgb[15, 15].mean())
