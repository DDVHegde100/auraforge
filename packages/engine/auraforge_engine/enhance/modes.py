"""Enhance mode presets layered on analysis recipe."""

from __future__ import annotations

from enum import Enum

from auraforge_engine.enhance.recipe import DevelopRecipe


class EnhanceMode(str, Enum):
    NATURAL = "natural"
    PORTRAIT = "portrait"
    LAND = "land"
    FOOD = "food"
    GLOW = "glow"


_MODE_BOOST: dict[str, dict[str, float]] = {
    EnhanceMode.NATURAL.value: {
        "contrast": 1.15,
        "vibrance": 1.05,
        "clarity": 1.1,
        "vignette": 0.65,
    },
    EnhanceMode.PORTRAIT.value: {
        "shadow_lift": 1.35,
        "clarity": 0.75,
        "vibrance": 1.2,
        "vignette": 1.5,
        "warmth": 1.22,
    },
    EnhanceMode.LAND.value: {
        "dehaze": 1.5,
        "clarity": 1.4,
        "vibrance": 1.25,
        "saturation": 1.15,
    },
    EnhanceMode.FOOD.value: {
        "warmth": 1.5,
        "saturation": 1.45,
        "vibrance": 1.35,
        "contrast": 1.18,
    },
    EnhanceMode.GLOW.value: {
        "shadow_lift": 1.45,
        "highlight_recovery": 1.3,
        "vibrance": 1.05,
        "vignette": 1.0,
        "warmth": 1.28,
    },
}


def apply_mode(recipe: DevelopRecipe, mode: str) -> DevelopRecipe:
    key = mode.lower().strip()
    if key not in _MODE_BOOST:
        key = EnhanceMode.NATURAL.value
    boosts = _MODE_BOOST[key]
    data = recipe.to_dict()
    for field, scale in boosts.items():
        data[field] = float(data.get(field, 0.0) * scale)
    if key == EnhanceMode.GLOW.value:
        data["vignette"] = max(data["vignette"], 0.08)
        data["shadow_lift"] = max(data["shadow_lift"], 0.06)
    return DevelopRecipe(**data)
