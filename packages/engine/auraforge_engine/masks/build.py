"""Unified mask pack — build once, reuse across develop + local edits."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from auraforge_engine.masks.feather import feather_mask
from auraforge_engine.masks.foliage import foliage_mask
from auraforge_engine.masks.onnx_sky import resolve_sky_mask
from auraforge_engine.masks.skin import skin_soft_mask
from auraforge_engine.masks.subject import subject_mask


@dataclass
class MaskPack:
    sky: np.ndarray
    skin: np.ndarray
    subject: np.ndarray
    foliage: np.ndarray
    sky_source: str = "heuristic"


def build_masks(
    rgb: np.ndarray,
    *,
    use_onnx_sky: bool = False,
) -> MaskPack:
    skin = skin_soft_mask(rgb, feather_sigma=8.0)
    sky_raw, source = resolve_sky_mask(rgb, use_onnx=use_onnx_sky)
    sky = feather_mask(sky_raw, sigma=9.0)
    subject = subject_mask(rgb, skin)
    foliage = foliage_mask(rgb)
    return MaskPack(
        sky=np.clip(sky, 0.0, 1.0).astype(np.float32),
        skin=skin,
        subject=np.clip(subject, 0.0, 1.0).astype(np.float32),
        foliage=np.clip(foliage, 0.0, 1.0).astype(np.float32),
        sky_source=source,
    )
