"""Unified scene analysis — feeds enhance recipe later."""

from __future__ import annotations

from typing import Any

import numpy as np

from auraforge_engine.analysis.color import color_stats
from auraforge_engine.analysis.content import guess_content
from auraforge_engine.analysis.exposure import classify_exposure
from auraforge_engine.analysis.histogram import histogram_features
from auraforge_engine.analysis.noise import noise_estimate
from auraforge_engine.analysis.saliency import center_saliency
from auraforge_engine.analysis.sky import sky_score
from auraforge_engine.analysis.skin import skin_score
from auraforge_engine.analysis.wb import wb_features


def analyze(rgb: np.ndarray, *, include_hist: bool = False) -> dict[str, Any]:
    """Return JSON-serializable scene analysis."""
    hist = histogram_features(rgb)
    if not include_hist:
        hist = {k: v for k, v in hist.items() if k != "hist"}

    out: dict[str, Any] = {
        "histogram": hist,
        "color": color_stats(rgb),
        "wb": wb_features(rgb),
        "noise": noise_estimate(rgb),
        "saliency": center_saliency(rgb),
        "exposure": classify_exposure(rgb),
        "content": guess_content(rgb),
        "sky": sky_score(rgb),
        "skin": skin_score(rgb),
    }
    return out


def analyze_summary(rgb: np.ndarray) -> dict[str, Any]:
    """Compact summary for UI debug panel."""
    full = analyze(rgb, include_hist=False)
    return {
        "exposure_class": full["exposure"]["exposure_class"],
        "content_class": full["content"]["content_class"],
        "content_confidence": full["content"]["content_confidence"],
        "sky_score": full["sky"]["sky_score"],
        "sky_detected": full["sky"]["sky_detected"],
        "skin_score": full["skin"]["skin_score"],
        "skin_detected": full["skin"]["skin_detected"],
        "noise_score": full["noise"]["noise_score"],
        "warmth": full["wb"]["warmth"],
        "mean_luma": full["histogram"]["mean_luma"],
        "contrast_std": full["color"]["contrast_std"],
        "saliency_focus_x": full["saliency"]["saliency_focus_x"],
        "saliency_focus_y": full["saliency"]["saliency_focus_y"],
    }
