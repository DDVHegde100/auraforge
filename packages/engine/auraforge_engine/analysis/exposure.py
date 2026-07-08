"""Exposure classification from histogram features."""

from __future__ import annotations

from enum import Enum

import numpy as np

from auraforge_engine.analysis.histogram import histogram_features


class ExposureClass(str, Enum):
    UNDER = "under"
    FLAT = "flat"
    BALANCED = "balanced"
    CONTRASTY = "contrasty"
    OVER = "over"


def classify_exposure(rgb: np.ndarray) -> dict:
    feat = histogram_features(rgb)
    mean = feat["mean_luma"]
    p05 = feat["p05_luma"]
    p95 = feat["p95_luma"]
    spread = p95 - p05
    shadow = feat["shadow_mass"]
    highlight = feat["highlight_mass"]

    if mean < 0.28 or (shadow > 0.45 and mean < 0.4):
        label = ExposureClass.UNDER
    elif mean > 0.72 or (highlight > 0.4 and mean > 0.55):
        label = ExposureClass.OVER
    elif spread < 0.35:
        label = ExposureClass.FLAT
    elif spread > 0.75 and shadow > 0.15 and highlight > 0.12:
        label = ExposureClass.CONTRASTY
    else:
        label = ExposureClass.BALANCED

    return {
        "exposure_class": label.value,
        "exposure_spread": float(spread),
        **{k: feat[k] for k in ("mean_luma", "shadow_mass", "mid_mass", "highlight_mass")},
    }
