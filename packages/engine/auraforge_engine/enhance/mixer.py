"""Scale develop recipe by 0–100 strength."""

from __future__ import annotations

from auraforge_engine.enhance.recipe import DevelopRecipe

# Perceptual curves — 50 on the slider should still feel like a real edit.
_CURVE: dict[str, float] = {
    "exposure_stops": 0.62,
    "shadow_lift": 0.58,
    "highlight_recovery": 0.58,
    "contrast": 0.55,
    "vibrance": 0.52,
    "saturation": 0.52,
    "clarity": 0.50,
    "warmth": 0.58,
    "tint": 0.58,
    "denoise": 0.72,
    "dehaze": 0.55,
    "vignette": 0.85,
    "blacks": 0.58,
    "whites": 0.58,
    "texture": 0.55,
    "sharpen": 0.58,
    "hsl_selective": 0.60,
}


def mix_strength(recipe: DevelopRecipe, strength: float) -> DevelopRecipe:
    raw = max(0.0, min(100.0, strength)) / 100.0
    if raw == 0.0:
        return DevelopRecipe()
    if raw == 1.0:
        return recipe

    data = recipe.to_dict()
    scaled: dict[str, float] = {}
    for field, value in data.items():
        exp = _CURVE.get(field, 0.58)
        t = raw**exp
        scaled[field] = float(value * t)
    return DevelopRecipe(**scaled)
