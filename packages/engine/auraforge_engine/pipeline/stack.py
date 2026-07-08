"""Enhance then optional grade — neo-like stacking order."""

from __future__ import annotations

from typing import Any

import numpy as np

from auraforge_engine.enhance.run import run_enhance
from auraforge_engine.grades.apply import apply_grade
from auraforge_engine.registry import get_look
from auraforge_engine.signatures.apply import apply_signature


def run_enhance_with_look(
    rgb: np.ndarray,
    *,
    strength: float = 50.0,
    mode: str = "natural",
    grade_id: str | None = None,
    signature_id: str | None = None,
    grade_strength: float = 1.0,
    signature_strength: float = 1.0,
    use_onnx_sky: bool = False,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Order: AI enhance → grade → signature."""
    out, meta = run_enhance(rgb, strength=strength, mode=mode, use_onnx_sky=use_onnx_sky)
    meta["stack_order"] = ["enhance"]

    if grade_id:
        look = get_look(grade_id)
        if look is None or look.kind != "grade":
            raise ValueError(f"unknown grade '{grade_id}'")
        out = apply_grade(out, look, strength=grade_strength)
        meta["grade_id"] = grade_id
        meta["stack_order"].append("grade")

    if signature_id:
        look = get_look(signature_id)
        if look is None or look.kind != "signature":
            raise ValueError(f"unknown signature '{signature_id}'")
        out = apply_signature(out, look, strength=signature_strength)
        meta["signature_id"] = signature_id
        meta["stack_order"].append("signature")

    return out, meta
