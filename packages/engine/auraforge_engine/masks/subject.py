"""Subject mask from skin + center saliency."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.saliency import center_saliency
from auraforge_engine.masks.feather import feather_mask


def subject_mask(rgb: np.ndarray, skin_mask: np.ndarray) -> np.ndarray:
    """Combine skin and saliency focus into a soft subject mask."""
    h, w = rgb.shape[:2]
    sal = center_saliency(rgb)
    fx = float(sal["saliency_focus_x"]) * max(w - 1, 1)
    fy = float(sal["saliency_focus_y"]) * max(h - 1, 1)

    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dist = np.sqrt((xx - fx) ** 2 + (yy - fy) ** 2)
    radius = max(min(h, w) * 0.28, 12.0)
    center_blob = np.clip(1.0 - dist / radius, 0.0, 1.0) ** 1.4

    combined = np.clip(0.55 * skin_mask + 0.45 * center_blob, 0.0, 1.0)
    return feather_mask(combined, sigma=5.0)


def apply_subject_lightness(
    rgb: np.ndarray,
    mask: np.ndarray,
    *,
    amount: float = 0.08,
) -> np.ndarray:
    if amount <= 0.0 or float(mask.max()) <= 1e-4:
        return rgb
    m = mask[..., None]
    lift = amount * m
    return np.clip(rgb + lift * (1.0 - rgb), 0.0, None)
