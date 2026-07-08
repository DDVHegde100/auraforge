"""Enhance recipe tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis import analyze
from auraforge_engine.enhance import recipe_from_analysis


def _dark_rgb() -> np.ndarray:
    rgb = np.zeros((48, 64, 3), dtype=np.float32)
    rgb[..., 1] = 0.15
    rgb[..., 2] = 0.25
    return rgb


def test_recipe_from_under_exposure() -> None:
    rgb = _dark_rgb()
    analysis = analyze(rgb)
    recipe = recipe_from_analysis(analysis)
    assert recipe.exposure_stops > 0.0 or recipe.shadow_lift > 0.0
