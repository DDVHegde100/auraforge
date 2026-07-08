"""Professional develop pipeline — Lightroom-class order, quality-safe."""

from __future__ import annotations

from typing import Any

import numpy as np

from auraforge_engine.develop.clarity import apply_clarity
from auraforge_engine.develop.dehaze import apply_dehaze_lite
from auraforge_engine.develop.denoise_pro import apply_denoise_pro
from auraforge_engine.develop.exposure import apply_exposure_stops
from auraforge_engine.develop.hsl_selective import apply_hsl_selective
from auraforge_engine.develop.sharpen_capture import apply_capture_sharpen
from auraforge_engine.develop.texture import apply_texture
from auraforge_engine.develop.tone import apply_parametric_tone
from auraforge_engine.develop.vibrance import apply_vibrance_sat
from auraforge_engine.develop.vignette import apply_vignette
from auraforge_engine.develop.wb_pro import apply_wb_pro
from auraforge_engine.enhance.recipe import DevelopRecipe
from auraforge_engine.masks.build import MaskPack


def apply_pro_develop(
    rgb: np.ndarray,
    recipe: DevelopRecipe,
    analysis: dict[str, Any] | None = None,
    masks: MaskPack | None = None,
) -> np.ndarray:
    """Lightroom-style develop: WB → exposure → tone → denoise → color → detail."""
    out = rgb.astype(np.float32, copy=True)

    out = apply_wb_pro(out, warmth=recipe.warmth, tint=recipe.tint, analysis=analysis)
    out = apply_exposure_stops(out, recipe.exposure_stops)
    out = apply_parametric_tone(
        out,
        blacks=recipe.blacks,
        shadows=recipe.shadow_lift,
        highlights=recipe.highlight_recovery,
        whites=recipe.whites,
        contrast=recipe.contrast,
    )
    out = apply_denoise_pro(out, luma=recipe.denoise, color=recipe.denoise * 0.55)
    out = apply_dehaze_lite(out, recipe.dehaze)
    out = apply_vibrance_sat(out, vibrance=recipe.vibrance, saturation=recipe.saturation)

    if analysis is not None and recipe.hsl_selective > 0.0:
        out = apply_hsl_selective(out, analysis, strength=recipe.hsl_selective, masks=masks)

    out = apply_texture(out, recipe.texture)
    out = apply_clarity(out, recipe.clarity)

    protect = masks.skin if masks is not None else None
    out = apply_capture_sharpen(
        out,
        recipe.sharpen,
        masking=0.68 + recipe.denoise * 0.2,
        protect_mask=protect,
    )
    out = apply_vignette(out, strength=recipe.vignette)
    return np.clip(out, 0.0, None)
