"""Debug false-color mask overlays."""

from __future__ import annotations

import numpy as np


def render_mask_overlay(
    rgb: np.ndarray,
    *,
    sky: np.ndarray | None = None,
    skin: np.ndarray | None = None,
    subject: np.ndarray | None = None,
) -> np.ndarray:
    """Tint sky cyan, skin magenta, subject yellow for UI debug."""
    base = np.clip(rgb, 0.0, 1.0).astype(np.float32)
    out = base.copy()
    if sky is not None:
        tint = np.array([0.2, 0.75, 0.95], dtype=np.float32)
        m = sky[..., None]
        out = out * (1.0 - 0.45 * m) + tint * (0.45 * m)
    if skin is not None:
        tint = np.array([0.95, 0.35, 0.75], dtype=np.float32)
        m = skin[..., None]
        out = out * (1.0 - 0.40 * m) + tint * (0.40 * m)
    if subject is not None:
        tint = np.array([0.95, 0.85, 0.25], dtype=np.float32)
        m = subject[..., None]
        out = out * (1.0 - 0.30 * m) + tint * (0.30 * m)
    return np.clip(out, 0.0, 1.0)
