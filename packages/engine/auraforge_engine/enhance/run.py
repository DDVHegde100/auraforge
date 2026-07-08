"""High-level enhance entry — pro develop + local masks."""

from __future__ import annotations

from typing import Any

import numpy as np

from auraforge_engine.analysis import analyze, analyze_summary
from auraforge_engine.enhance.mixer import mix_strength
from auraforge_engine.enhance.modes import apply_mode
from auraforge_engine.enhance.pipeline import apply_recipe
from auraforge_engine.enhance.recipe import recipe_from_analysis
from auraforge_engine.enhance.tune import TuneParams, merge_tune_into_recipe
from auraforge_engine.masks.build import build_masks
from auraforge_engine.masks.stack import apply_mask_stack


def run_enhance(
    rgb: np.ndarray,
    *,
    strength: float = 50.0,
    mode: str = "natural",
    use_onnx_sky: bool = False,
    tune: TuneParams | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    tune = tune or TuneParams()
    masks = build_masks(rgb, use_onnx_sky=use_onnx_sky)
    analysis = analyze(rgb)

    recipe = recipe_from_analysis(analysis)
    recipe = apply_mode(recipe, mode)
    recipe = mix_strength(recipe, strength)
    recipe = merge_tune_into_recipe(recipe, tune)

    out = apply_recipe(rgb, recipe, analysis=analysis, masks=masks)

    out, mask_meta = apply_mask_stack(
        rgb,
        out,
        analysis,
        use_onnx_sky=use_onnx_sky,
        light_boost=0.78 + _norm(tune.light) * 0.38,
        masks=masks,
    )

    meta = {
        "analysis": analyze_summary(rgb),
        "recipe": recipe.to_dict(),
        "mode": mode,
        "strength": float(strength),
        "tune": tune.to_dict(),
        "masks": mask_meta,
        "engine": "pro_develop_v2",
    }
    return out, meta


def _norm(v: float) -> float:
    return max(-1.0, min(1.0, (float(v) - 50.0) / 50.0))
