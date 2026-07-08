"""Lab-based white balance — smoother than RGB offset."""

from __future__ import annotations

from typing import Any

import numpy as np

from auraforge_engine.develop.lab import lab_to_rgb, rgb_to_lab


def apply_wb_pro(
    rgb: np.ndarray,
    *,
    warmth: float = 0.0,
    tint: float = 0.0,
    analysis: dict[str, Any] | None = None,
) -> np.ndarray:
    if warmth == 0.0 and tint == 0.0 and not analysis:
        return rgb

    lab = rgb_to_lab(rgb)
    a = lab[..., 1] - 128.0
    b = lab[..., 2] - 128.0

    if analysis:
        wb = analysis.get("wb", {})
        cast = float(wb.get("warmth", 0.0))
        b -= cast * 10.0 * 0.55
        a -= float(wb.get("gw_gain_r", 1.0) - wb.get("gw_gain_b", 1.0)) * 4.0

    b += warmth * 14.0
    a += tint * 11.0

    out = lab.copy()
    out[..., 1] = np.clip(a + 128.0, 0.0, 255.0)
    out[..., 2] = np.clip(b + 128.0, 0.0, 255.0)
    return lab_to_rgb(out)
