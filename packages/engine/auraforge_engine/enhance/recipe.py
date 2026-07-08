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

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def recipe_from_analysis(analysis: dict[str, Any]) -> DevelopRecipe:
    """Build a base develop recipe from unified analysis output."""
    exposure = analysis["exposure"]["exposure_class"]
    content = analysis["content"]["content_class"]
    sky = float(analysis["sky"]["sky_score"])
    noise = float(analysis["noise"]["noise_score"])
    warmth_bias = float(analysis["wb"]["warmth"])
    contrast_std = float(analysis["color"]["contrast_std"])

    recipe = DevelopRecipe()

    if exposure == "under":
        recipe.exposure_stops = 0.35
        recipe.shadow_lift = 0.18
    elif exposure == "over":
        recipe.exposure_stops = -0.25
        recipe.highlight_recovery = 0.28
    elif exposure == "flat":
        recipe.contrast = 0.10
        recipe.clarity = 0.08
    elif exposure == "contrasty":
        recipe.shadow_lift = 0.08
        recipe.highlight_recovery = 0.15

    if noise > 0.25:
        recipe.denoise = min(0.65, 0.25 + noise * 0.55)

    if contrast_std < 0.08:
        recipe.contrast += 0.06
        recipe.clarity += 0.05

    if content == "portrait":
        recipe.clarity = min(recipe.clarity, 0.10)
        recipe.vibrance = 0.08
        recipe.shadow_lift = max(recipe.shadow_lift, 0.10)
        recipe.vignette = 0.12
    elif content == "landscape":
        recipe.dehaze = 0.10 + sky * 0.12
        recipe.clarity = max(recipe.clarity, 0.12)
        recipe.vibrance = 0.10
    elif content == "food":
        recipe.warmth = 0.35
        recipe.saturation = 0.12
        recipe.vibrance = 0.14
    else:
        recipe.vibrance = 0.06
        recipe.saturation = 0.04

    if sky > 0.3:
        recipe.dehaze = max(recipe.dehaze, 0.08)
        recipe.highlight_recovery = max(recipe.highlight_recovery, 0.12)

    if warmth_bias < -0.02:
        recipe.warmth += 0.20
    elif warmth_bias > 0.04:
        recipe.warmth -= 0.10

    return recipe


def recipe_for_rgb(rgb: np.ndarray) -> DevelopRecipe:
    return recipe_from_analysis(analyze(rgb))
