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


from auraforge_engine.enhance import DevelopRecipe, mix_strength


def test_mix_strength_zero_is_identity() -> None:
    base = DevelopRecipe(contrast=0.2, clarity=0.15)
    mixed = mix_strength(base, 0.0)
    assert mixed.contrast == 0.0
    assert mixed.clarity == 0.0


def test_mix_strength_half() -> None:
    base = DevelopRecipe(contrast=0.2)
    mixed = mix_strength(base, 50.0)
    assert mixed.contrast > 0.12
    assert mixed.contrast < 0.18


from auraforge_engine.enhance import apply_mode


def test_portrait_mode_boosts_vignette() -> None:
    base = DevelopRecipe(vignette=0.10, clarity=0.12)
    out = apply_mode(base, "portrait")
    assert out.vignette > base.vignette
    assert out.clarity < base.clarity


from auraforge_engine.enhance import apply_recipe, run_enhance


def test_apply_recipe_changes_image() -> None:
    rgb = np.full((16, 16, 3), 0.35, dtype=np.float32)
    recipe = DevelopRecipe(exposure_stops=0.5, contrast=0.1)
    out = apply_recipe(rgb, recipe)
    assert float(out.mean()) > float(rgb.mean())


def test_run_enhance_returns_meta() -> None:
    rgb = np.full((24, 32, 3), 0.4, dtype=np.float32)
    out, meta = run_enhance(rgb, strength=60.0, mode="natural")
    assert out.shape == rgb.shape
    assert meta["strength"] == 60.0
    assert "recipe" in meta
