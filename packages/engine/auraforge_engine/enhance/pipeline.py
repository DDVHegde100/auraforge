"""Run develop recipe on rgb."""

from __future__ import annotations

import numpy as np

from auraforge_engine.develop import (
    apply_clarity,
    apply_contrast,
    apply_dehaze_lite,
    apply_exposure_stops,
    apply_highlight_recovery,
    apply_mild_denoise,
    apply_shadow_lift,
    apply_vibrance_sat,
    apply_vignette,
    apply_warmth_tint,
)
from auraforge_engine.enhance.recipe import DevelopRecipe


def apply_recipe(rgb: np.ndarray, recipe: DevelopRecipe) -> np.ndarray:
    out = rgb.astype(np.float32, copy=True)
    out = apply_exposure_stops(out, recipe.exposure_stops)
    out = apply_shadow_lift(out, recipe.shadow_lift)
    out = apply_highlight_recovery(out, recipe.highlight_recovery)
    out = apply_contrast(out, recipe.contrast)
    out = apply_vibrance_sat(out, vibrance=recipe.vibrance, saturation=recipe.saturation)
    out = apply_clarity(out, recipe.clarity)
    out = apply_warmth_tint(out, warmth=recipe.warmth, tint=recipe.tint)
    out = apply_mild_denoise(out, recipe.denoise)
    out = apply_dehaze_lite(out, recipe.dehaze)
    out = apply_vignette(out, strength=recipe.vignette)
    return np.clip(out, 0.0, None)
