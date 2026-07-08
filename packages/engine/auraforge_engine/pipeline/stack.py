"""Enhance then optional grade — neo-like stacking order."""

from __future__ import annotations

from typing import Any

import numpy as np

from auraforge_engine.cameras.apply import apply_camera
from auraforge_engine.enhance.run import run_enhance
from auraforge_engine.enhance.tune import TuneParams
from auraforge_engine.grades.apply import apply_grade
from auraforge_engine.registry import get_look
from auraforge_engine.signatures.apply import apply_signature
from auraforge_engine.signatures.safety import PRO_SAFE_MAX, clamp_signature_strength


def run_enhance_with_look(
    rgb: np.ndarray,
    *,
    strength: float = 50.0,
    mode: str = "natural",
    grade_id: str | None = None,
    camera_id: str | None = None,
    signature_id: str | None = None,
    grade_strength: float = 1.0,
    camera_strength: float = 1.0,
    signature_strength: float = 1.0,
    pro_safe: bool = True,
    use_onnx_sky: bool = False,
    tune: TuneParams | None = None,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Order: AI enhance → grade → camera → signature."""
    tune = tune or TuneParams()
    look_t = max(0.0, min(1.0, tune.look_amount / 100.0))
    out, meta = run_enhance(
        rgb,
        strength=strength,
        mode=mode,
        use_onnx_sky=use_onnx_sky,
        tune=tune,
    )
    meta["stack_order"] = ["enhance"]

    if grade_id:
        look = get_look(grade_id)
        if look is None or look.kind != "grade":
            raise ValueError(f"unknown grade '{grade_id}'")
        out = apply_grade(out, look, strength=grade_strength * look_t)
        meta["grade_id"] = grade_id
        meta["stack_order"].append("grade")

    if camera_id:
        look = get_look(camera_id)
        if look is None or look.kind != "camera":
            raise ValueError(f"unknown camera '{camera_id}'")
        out = apply_camera(out, look, strength=camera_strength * look_t)
        meta["camera_id"] = camera_id
        meta["stack_order"].append("camera")

    if signature_id:
        look = get_look(signature_id)
        if look is None or look.kind != "signature":
            raise ValueError(f"unknown signature '{signature_id}'")
        sig_strength = clamp_signature_strength(look, signature_strength * look_t, pro_safe=pro_safe)
        out = apply_signature(out, look, strength=sig_strength)
        meta["signature_id"] = signature_id
        meta["signature_strength"] = sig_strength
        meta["pro_safe"] = pro_safe
        if look.experimental and pro_safe and signature_strength > PRO_SAFE_MAX:
            meta["signature_clamped"] = True
        meta["stack_order"].append("signature")

    meta["tune"] = tune.to_dict()
    return out, meta
