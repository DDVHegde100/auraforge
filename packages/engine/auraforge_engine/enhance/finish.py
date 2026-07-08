"""Scene-adaptive polish after develop + masks."""

from __future__ import annotations

from typing import Any

import numpy as np

from auraforge_engine.analysis.histogram import luminance
from auraforge_engine.develop.warmth import apply_warmth_tint


def adaptive_finish(
    rgb: np.ndarray,
    analysis: dict[str, Any],
    *,
    strength: float = 0.5,
) -> np.ndarray:
    """Subtle WB + tone curve only — no extra sharpening."""
    t = max(0.0, min(1.0, strength))
    if t <= 0.0:
        return rgb
    out = _refine_white_balance(rgb, analysis, t * 0.35)
    out = _adaptive_tone_curve(out, analysis, t * 0.42)
    return np.clip(out, 0.0, None)


def _refine_white_balance(rgb: np.ndarray, analysis: dict[str, Any], amount: float) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    wb = analysis.get("wb", {})
    warmth = float(wb.get("warmth", 0.0))
    correction = -warmth * 0.14 * amount
    if abs(correction) < 0.008:
        return rgb
    return apply_warmth_tint(rgb, warmth=correction)


def _adaptive_tone_curve(rgb: np.ndarray, analysis: dict[str, Any], amount: float) -> np.ndarray:
    if amount <= 0.0:
        return rgb
    hist = analysis.get("histogram", {})
    p05 = float(hist.get("p05_luma", 0.05))
    p95 = float(hist.get("p95_luma", 0.95))
    if p95 - p05 < 0.10:
        return rgb

    lum = luminance(rgb)
    toe = max(0.0, 0.16 - p05) * amount * 0.42
    shoulder = max(0.0, p95 - 0.90) * amount * 0.28
    curved = lum + toe * (1.0 - lum) * np.clip(1.0 - lum * 2.4, 0.0, 1.0)
    curved = curved - shoulder * np.clip((curved - 0.80) / 0.20, 0.0, 1.0) ** 1.8 * curved

    scale = np.divide(
        curved,
        np.maximum(lum, 1e-5),
        out=np.ones_like(lum),
        where=lum > 1e-5,
    )
    return rgb * scale[..., None]
