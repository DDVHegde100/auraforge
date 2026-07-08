"""Apply sky + skin masking on top of develop enhance."""

from __future__ import annotations

import numpy as np

from auraforge_engine.masks.feather import feather_mask
from auraforge_engine.masks.onnx_sky import resolve_sky_mask
from auraforge_engine.masks.skin import skin_soft_mask
from auraforge_engine.masks.skin_protect import apply_skin_protect
from auraforge_engine.masks.sky_tone import apply_sky_tone
from auraforge_engine.masks.subject import apply_subject_lightness, subject_mask


def apply_mask_stack(
    rgb: np.ndarray,
    enhanced: np.ndarray,
    analysis: dict,
    *,
    use_onnx_sky: bool = False,
) -> tuple[np.ndarray, dict]:
    """Sky pop + skin protect + gentle subject lift."""
    meta: dict = {"sky_applied": False, "skin_protect_applied": False, "subject_lift_applied": False}

    sky_info = analysis.get("sky", {})
    if sky_info.get("sky_detected") or float(sky_info.get("sky_score", 0.0)) >= 0.18:
        sky_m, source = resolve_sky_mask(rgb, use_onnx=use_onnx_sky)
        sky_m = feather_mask(sky_m, sigma=10.0)
        strength = min(1.0, 0.55 + float(sky_info.get("sky_score", 0.0)))
        enhanced = apply_sky_tone(
            enhanced,
            sky_m,
            dehaze=0.14 * strength,
            vibrance=0.10 * strength,
            warmth=-0.05 * strength,
        )
        meta["sky_applied"] = True
        meta["sky_mask_source"] = source

    skin_info = analysis.get("skin", {})
    skin_m = skin_soft_mask(rgb)
    if skin_info.get("skin_detected") or float(skin_info.get("skin_score", 0.0)) >= 0.06:
        protect = min(0.75, 0.35 + float(skin_info.get("skin_score", 0.0)))
        enhanced = apply_skin_protect(enhanced, rgb, skin_m, strength=protect)
        meta["skin_protect_applied"] = True

    content = analysis.get("content", {}).get("content_class", "general")
    if content == "portrait" or float(skin_info.get("skin_score", 0.0)) >= 0.10:
        subj = subject_mask(rgb, skin_m)
        enhanced = apply_subject_lightness(enhanced, subj, amount=0.06)
        meta["subject_lift_applied"] = True

    return enhanced, meta
