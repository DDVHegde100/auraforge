"""High-level enhance entry."""

from __future__ import annotations

from typing import Any

import numpy as np

from auraforge_engine.analysis import analyze, analyze_summary
from auraforge_engine.enhance.mixer import mix_strength
from auraforge_engine.enhance.modes import apply_mode
from auraforge_engine.enhance.pipeline import apply_recipe
from auraforge_engine.enhance.recipe import recipe_from_analysis
from auraforge_engine.masks.stack import apply_mask_stack


def run_enhance(
    rgb: np.ndarray,
    *,
    strength: float = 50.0,
    mode: str = "natural",
    use_onnx_sky: bool = False,
) -> tuple[np.ndarray, dict[str, Any]]:
    analysis = analyze(rgb)
    recipe = recipe_from_analysis(analysis)
    recipe = apply_mode(recipe, mode)
    recipe = mix_strength(recipe, strength)
    out = apply_recipe(rgb, recipe)
    out, mask_meta = apply_mask_stack(
        rgb,
        out,
        analysis,
        use_onnx_sky=use_onnx_sky,
    )
    meta = {
        "analysis": analyze_summary(rgb),
        "recipe": recipe.to_dict(),
        "mode": mode,
        "strength": float(strength),
        "masks": mask_meta,
    }
    return out, meta
