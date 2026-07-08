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
        "contrast": 1.08,
        "vibrance": 1.06,
        "clarity": 1.05,
        "texture": 1.08,
        "sharpen": 1.05,
        "vignette": 0.70,
    },
    EnhanceMode.PORTRAIT.value: {
        "shadow_lift": 1.28,
        "clarity": 0.92,
        "texture": 1.15,
        "vibrance": 1.18,
        "sharpen": 0.92,
        "vignette": 1.45,
        "warmth": 1.20,
        "hsl_selective": 0.85,
    },
    EnhanceMode.LAND.value: {
        "dehaze": 1.45,
        "clarity": 1.32,
        "texture": 1.22,
        "vibrance": 1.22,
        "saturation": 1.12,
        "hsl_selective": 1.25,
        "sharpen": 1.12,
    },
    EnhanceMode.FOOD.value: {
        "warmth": 1.38,
        "saturation": 1.38,
        "vibrance": 1.32,
        "contrast": 1.14,
        "texture": 1.18,
        "sharpen": 1.08,
    },
    EnhanceMode.GLOW.value: {
        "shadow_lift": 1.38,
        "highlight_recovery": 1.25,
        "vibrance": 1.08,
        "vignette": 0.95,
        "warmth": 1.25,
        "clarity": 0.88,
        "sharpen": 0.82,
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
        data["vignette"] = max(data["vignette"], 0.10)
        data["shadow_lift"] = max(data["shadow_lift"], 0.08)
        data["whites"] = max(data["whites"], 0.04)
    return DevelopRecipe(**data)
