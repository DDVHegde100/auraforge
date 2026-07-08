"""3x3 color matrix + offset for film stock emulations."""

from __future__ import annotations

import numpy as np


def color_matrix(
    rgb: np.ndarray,
    *,
    matrix: list[list[float]] | None = None,
    offset: list[float] | None = None,
    strength: float = 1.0,
) -> np.ndarray:
    if strength <= 0.0:
        return rgb
    m = np.array(
        matrix or [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        dtype=np.float32,
    )
    identity = np.eye(3, dtype=np.float32)
    t = max(0.0, min(1.0, strength))
    blend = identity * (1.0 - t) + m * t
    off = np.array(offset or [0.0, 0.0, 0.0], dtype=np.float32) * t
    flat = rgb.reshape(-1, 3).astype(np.float32)
    out = flat @ blend.T + off
    return out.reshape(rgb.shape)
