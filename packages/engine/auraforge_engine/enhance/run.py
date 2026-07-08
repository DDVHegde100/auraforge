"""High-level enhance entry."""

from __future__ import annotations

from typing import Any

import numpy as np

from auraforge_engine.analysis import analyze, analyze_summary
from auraforge_engine.effects.light_remap import light_remap
from auraforge_engine.effects.upscale_detail import upscale_detail
from auraforge_engine.effects.detail import multiscale_detail
from auraforge_engine.enhance.mixer import mix_strength
from auraforge_engine.enhance.modes import apply_mode
from auraforge_engine.enhance.pipeline import apply_recipe
from auraforge_engine.enhance.recipe import recipe_from_analysis
from auraforge_engine.enhance.tune import TuneParams, merge_tune_into_recipe
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
    analysis = analyze(rgb)
    recipe = recipe_from_analysis(analysis)
    recipe = apply_mode(recipe, mode)
    recipe = merge_tune_into_recipe(recipe, tune)
    recipe = mix_strength(recipe, strength)
    out = apply_recipe(rgb, recipe)

    accent = max(0.0, min(1.0, strength / 100.0))
    out = multiscale_detail(out, strength=0.06 + accent * 0.14 + max(0.0, _norm(tune.detail)) * 0.12)

    out, mask_meta = apply_mask_stack(
        rgb,
        out,
        analysis,
        use_onnx_sky=use_onnx_sky,
        light_boost=0.65 + _norm(tune.light) * 0.35,
    )

    light_t = max(0.0, min(1.0, 0.25 + accent * 0.35 + _norm(tune.light) * 0.35))
    out = light_remap(
        out,
        strength=light_t,
        shadow_lift=0.08 + max(0.0, _norm(tune.shadows)) * 0.14,
        highlight_glow=0.12 + max(0.0, _norm(tune.highlights)) * 0.22,
        mid_punch=0.06 + max(0.0, _norm(tune.clarity)) * 0.10,
    )

    detail_t = max(0.0, min(1.0, 0.2 + accent * 0.45 + _norm(tune.detail) * 0.45))
    out = upscale_detail(out, strength=detail_t, micro_scale=1.12 + detail_t * 0.12)

    meta = {
        "analysis": analyze_summary(rgb),
        "recipe": recipe.to_dict(),
        "mode": mode,
        "strength": float(strength),
        "tune": tune.to_dict(),
        "masks": mask_meta,
    }
    return out, meta


def _norm(v: float) -> float:
    return max(-1.0, min(1.0, (float(v) - 50.0) / 50.0))
