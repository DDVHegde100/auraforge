"""False-color thermal map look."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis.histogram import luminance


def _lerp(a: np.ndarray, b: np.ndarray, t: np.ndarray) -> np.ndarray:
    return a + (b - a) * t[..., None]


def false_color_thermal(
    rgb: np.ndarray,
    *,
    strength: float = 1.0,
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    t = np.clip(luminance(rgb), 0.0, 1.0)
    # blue -> cyan -> yellow -> red
    c0 = np.array([0.05, 0.08, 0.55], dtype=np.float32)
    c1 = np.array([0.10, 0.75, 0.95], dtype=np.float32)
    c2 = np.array([0.98, 0.88, 0.15], dtype=np.float32)
    c3 = np.array([0.95, 0.15, 0.05], dtype=np.float32)

    mapped = np.zeros_like(rgb)
    m1 = t <= 0.33
    m2 = (t > 0.33) & (t <= 0.66)
    m3 = t > 0.66
    if m1.any():
        local = np.clip(t[m1] / 0.33, 0.0, 1.0)
        mapped[m1] = _lerp(c0, c1, local)
    if m2.any():
        local = np.clip((t[m2] - 0.33) / 0.33, 0.0, 1.0)
        mapped[m2] = _lerp(c1, c2, local)
    if m3.any():
        local = np.clip((t[m3] - 0.66) / 0.34, 0.0, 1.0)
        mapped[m3] = _lerp(c2, c3, local)

    return np.clip(rgb * (1.0 - strength) + mapped * strength, 0.0, 1.0)
