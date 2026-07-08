"""Apply sky + skin masking on top of develop enhance."""

from __future__ import annotations

import numpy as np

from auraforge_engine.masks.build import MaskPack, build_masks
from auraforge_engine.masks.portrait import apply_portrait_polish
from auraforge_engine.masks.skin_protect import apply_skin_protect
from auraforge_engine.masks.sky_tone import apply_sky_tone
from auraforge_engine.masks.subject import apply_subject_lightness


def apply_mask_stack(
    rgb: np.ndarray,
    enhanced: np.ndarray,
    analysis: dict,
    *,
    use_onnx_sky: bool = False,
    light_boost: float = 1.0,
    masks: MaskPack | None = None,
) -> tuple[np.ndarray, dict]:
    """Sky pop + skin protect + subject lift + portrait polish."""
    meta: dict = {"sky_applied": False, "skin_protect_applied": False, "subject_lift_applied": False}

    pack = masks if masks is not None else build_masks(rgb, use_onnx_sky=use_onnx_sky)
    meta["sky_mask_source"] = pack.sky_source

    sky_info = analysis.get("sky", {})
    if sky_info.get("sky_detected") or float(sky_info.get("sky_score", 0.0)) >= 0.16:
        strength = min(1.65, (0.82 + float(sky_info.get("sky_score", 0.0))) * light_boost)
        enhanced = apply_sky_tone(
            enhanced,
            pack.sky,
            dehaze=0.28 * strength,
            vibrance=0.24 * strength,
            warmth=-0.06 * strength,
        )
        meta["sky_applied"] = True

    skin_info = analysis.get("skin", {})
    if skin_info.get("skin_detected") or float(skin_info.get("skin_score", 0.0)) >= 0.05:
        protect = min(0.58, 0.28 + float(skin_info.get("skin_score", 0.0)))
        enhanced = apply_skin_protect(enhanced, rgb, pack.skin, strength=protect)
        meta["skin_protect_applied"] = True

    content = analysis.get("content", {}).get("content_class", "general")
    skin_score = float(skin_info.get("skin_score", 0.0))
    saliency_mean = float(analysis.get("saliency", {}).get("saliency_mean", 0.0))

    if content == "portrait" or skin_score >= 0.09:
        enhanced = apply_subject_lightness(enhanced, pack.subject, amount=0.12 * light_boost)
        enhanced = apply_portrait_polish(
            enhanced,
            rgb,
            pack.skin,
            pack.subject,
            strength=0.55 + skin_score * 0.45,
        )
        meta["subject_lift_applied"] = True
        meta["portrait_polish"] = True
    elif saliency_mean >= 0.18:
        enhanced = apply_subject_lightness(
            enhanced,
            pack.subject,
            amount=0.08 * light_boost * min(1.0, saliency_mean * 1.35),
        )
        meta["subject_lift_applied"] = True

    return enhanced, meta
