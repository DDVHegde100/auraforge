"""Stacking order tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.pipeline.stack import run_enhance_with_look
from auraforge_engine.registry import get_look


def test_enhance_then_grade_order() -> None:
    rgb = np.full((32, 32, 3), 0.42, dtype=np.float32)
    look = get_look("grade_portrait_natural")
    assert look is not None
    out, meta = run_enhance_with_look(
        rgb,
        strength=40.0,
        mode="natural",
        grade_id="grade_portrait_natural",
    )
    assert meta["stack_order"] == ["enhance", "grade"]
    assert meta["grade_id"] == "grade_portrait_natural"
    assert not np.allclose(out, rgb)


def test_signature_pro_safe_clamp_in_stack() -> None:
    rgb = np.full((16, 16, 3), 0.4, dtype=np.float32)
    _out, meta = run_enhance_with_look(
        rgb,
        strength=50.0,
        mode="natural",
        signature_id="sig_thermal_spectrum",
        signature_strength=1.0,
        pro_safe=True,
    )
    assert meta.get("signature_clamped") is True
    assert meta["signature_strength"] == 0.60


def test_enhance_only_when_no_grade() -> None:
    rgb = np.full((24, 24, 3), 0.35, dtype=np.float32)
    out, meta = run_enhance_with_look(rgb, strength=30.0, mode="natural")
    assert meta["stack_order"] == ["enhance"]
    assert "grade_id" not in meta
    assert out.shape == rgb.shape
