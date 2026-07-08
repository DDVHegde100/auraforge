"""Map scene analysis to develop parameters."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from auraforge_engine.analysis import analyze


@dataclass
class DevelopRecipe:
    exposure_stops: float = 0.0
    shadow_lift: float = 0.0
    highlight_recovery: float = 0.0
    contrast: float = 0.0
    vibrance: float = 0.0
    saturation: float = 0.0
    clarity: float = 0.0
    warmth: float = 0.0
    tint: float = 0.0
    denoise: float = 0.0
    dehaze: float = 0.0
    vignette: float = 0.0
    blacks: float = 0.0
    whites: float = 0.0
    texture: float = 0.0
    sharpen: float = 0.0
    hsl_selective: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def recipe_from_analysis(analysis: dict[str, Any]) -> DevelopRecipe:
    """Scene-aware recipe tuned like a pro Lightroom edit."""
    hist = analysis["histogram"]
    exp = analysis["exposure"]
    content = analysis["content"]
    sky = float(analysis["sky"]["sky_score"])
    noise = float(analysis["noise"]["noise_score"])
    warmth_bias = float(analysis["wb"]["warmth"])
    contrast_std = float(analysis["color"]["contrast_std"])
    sat_mean = float(analysis["color"]["sat_mean"])

    mean = float(hist["mean_luma"])
    median = float(hist["median_luma"])
    spread = float(exp["exposure_spread"])
    shadow_m = float(hist["shadow_mass"])
    hi_m = float(hist["highlight_mass"])
    p05 = float(hist["p05_luma"])
    p95 = float(hist["p95_luma"])
    conf = float(content["content_confidence"])
    cls = content["content_class"]

    recipe = DevelopRecipe()

    skew = mean - median
    target_mean = 0.47
    recipe.exposure_stops = float(np.clip((target_mean - mean) * 1.15 - skew * 0.20, -0.28, 0.58))

    recipe.shadow_lift = float(np.clip((shadow_m - 0.18) * 0.52 + max(0.0, 0.24 - p05) * 0.62, 0.0, 0.32))
    recipe.highlight_recovery = float(
        np.clip((hi_m - 0.06) * 0.55 + max(0.0, p95 - 0.91) * 0.85, 0.0, 0.36)
    )
    recipe.blacks = float(np.clip((0.04 - p05) * 0.85, -0.10, 0.06))
    recipe.whites = float(np.clip((0.97 - p95) * 0.55, 0.0, 0.14))

    exposure = exp["exposure_class"]
    if exposure == "under":
        recipe.exposure_stops = max(recipe.exposure_stops, 0.32)
        recipe.shadow_lift = max(recipe.shadow_lift, 0.18)
        recipe.blacks = min(recipe.blacks, -0.02)
    elif exposure == "over":
        recipe.exposure_stops = min(recipe.exposure_stops, -0.14)
        recipe.highlight_recovery = max(recipe.highlight_recovery, 0.28)
        recipe.whites = max(recipe.whites, 0.06)
    elif exposure == "flat":
        recipe.contrast = max(recipe.contrast, 0.10)
        recipe.clarity = max(recipe.clarity, 0.08)
        recipe.texture = max(recipe.texture, 0.05)
    elif exposure == "contrasty":
        recipe.shadow_lift = max(recipe.shadow_lift, 0.10)
        recipe.highlight_recovery = max(recipe.highlight_recovery, 0.18)

    if spread < 0.42:
        deficit = 0.42 - spread
        recipe.contrast += deficit * 0.26
        recipe.clarity += deficit * 0.12
        recipe.texture += deficit * 0.08

    if contrast_std < 0.088:
        recipe.contrast += (0.088 - contrast_std) * 0.52

    if noise > 0.18:
        recipe.denoise = min(0.62, 0.14 + noise * 0.52)
    recipe.sharpen = float(np.clip(0.16 - noise * 0.09, 0.06, 0.20))

    content_w = 0.48 + 0.52 * conf
    recipe.hsl_selective = float(np.clip(0.42 + conf * 0.38 + sky * 0.12, 0.35, 0.88))

    if cls == "portrait":
        recipe.texture = max(recipe.texture, 0.05 * content_w)
        recipe.clarity = min(recipe.clarity + 0.04 * content_w, 0.11)
        recipe.vibrance = max(recipe.vibrance, 0.10 * content_w)
        recipe.shadow_lift = max(recipe.shadow_lift, 0.12 * content_w)
        recipe.vignette = max(recipe.vignette, 0.12 * content_w)
        recipe.hsl_selective *= 0.85
    elif cls == "landscape":
        recipe.dehaze = max(recipe.dehaze, (0.12 + sky * 0.18) * content_w)
        recipe.clarity = max(recipe.clarity, 0.14 * content_w)
        recipe.texture = max(recipe.texture, 0.07 * content_w)
        recipe.vibrance = max(recipe.vibrance, 0.12 * content_w)
    elif cls == "food":
        recipe.warmth = max(recipe.warmth, 0.32 * content_w)
        recipe.saturation = max(recipe.saturation, 0.12 * content_w)
        recipe.vibrance = max(recipe.vibrance, 0.14 * content_w)
        recipe.texture = max(recipe.texture, 0.06 * content_w)
    else:
        recipe.vibrance = max(recipe.vibrance, 0.08)
        recipe.saturation = max(recipe.saturation, 0.05)
        recipe.texture = max(recipe.texture, 0.04)

    if sky > 0.30:
        recipe.dehaze = max(recipe.dehaze, 0.08 + sky * 0.10)
        recipe.highlight_recovery = max(recipe.highlight_recovery, 0.12)

    if sat_mean < 0.135:
        recipe.vibrance = max(recipe.vibrance, 0.08 + (0.135 - sat_mean) * 0.55)

    if warmth_bias < -0.026:
        recipe.warmth += 0.18
    elif warmth_bias > 0.048:
        recipe.warmth -= 0.10

    # Every photo gets a visible baseline — AI Enhance at default should never feel like a no-op.
    recipe.contrast = max(recipe.contrast, 0.10)
    recipe.vibrance = max(recipe.vibrance, 0.14)
    recipe.saturation = max(recipe.saturation, 0.08)
    recipe.clarity = max(recipe.clarity, 0.10)
    recipe.texture = max(recipe.texture, 0.08)
    recipe.sharpen = max(recipe.sharpen, 0.12)
    recipe.hsl_selective = max(recipe.hsl_selective, 0.45)

    return recipe


def recipe_for_rgb(rgb: np.ndarray) -> DevelopRecipe:
    return recipe_from_analysis(analyze(rgb))
