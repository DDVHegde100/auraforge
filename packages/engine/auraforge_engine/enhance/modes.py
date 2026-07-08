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
        "contrast": 1.0,
        "vibrance": 0.85,
        "clarity": 0.9,
        "vignette": 0.5,
    },
    EnhanceMode.PORTRAIT.value: {
        "shadow_lift": 1.2,
        "clarity": 0.55,
        "vibrance": 1.1,
        "vignette": 1.4,
        "warmth": 1.15,
    },
    EnhanceMode.LAND.value: {
        "dehaze": 1.35,
        "clarity": 1.25,
        "vibrance": 1.15,
        "saturation": 1.1,
    },
    EnhanceMode.FOOD.value: {
        "warmth": 1.4,
        "saturation": 1.35,
        "vibrance": 1.25,
        "contrast": 1.1,
    },
    EnhanceMode.GLOW.value: {
        "shadow_lift": 1.3,
        "highlight_recovery": 1.2,
        "vibrance": 0.9,
        "vignette": 0.8,
        "warmth": 1.2,
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
