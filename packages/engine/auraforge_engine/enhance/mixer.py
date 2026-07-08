"""Scale develop recipe by 0–100 strength."""

from __future__ import annotations

from auraforge_engine.enhance.recipe import DevelopRecipe


def mix_strength(recipe: DevelopRecipe, strength: float) -> DevelopRecipe:
    t = max(0.0, min(100.0, strength)) / 100.0
    if t == 0.0:
        return DevelopRecipe()
    if t == 1.0:
        return recipe
    return DevelopRecipe(
        **{field: float(getattr(recipe, field) * t) for field in recipe.to_dict()},
    )
