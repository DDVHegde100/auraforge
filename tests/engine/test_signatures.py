"""Pro-safe signature clamp tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.registry import get_look
from auraforge_engine.signatures import clamp_signature_strength, load_signatures


def test_load_signatures_count_20() -> None:
    sigs = load_signatures()
    assert len(sigs) >= 20


def test_pro_safe_clamps_experimental() -> None:
    look = get_look("sig_thermal_spectrum")
    assert look is not None
    assert look.experimental
    assert clamp_signature_strength(look, 1.0, pro_safe=True) == 0.85
    assert clamp_signature_strength(look, 1.0, pro_safe=False) == 1.0


def test_pro_safe_allows_normal_signature() -> None:
    look = get_look("sig_floating_light")
    assert look is not None
    assert clamp_signature_strength(look, 0.85, pro_safe=True) == 0.85


def test_arctic_glass_applies() -> None:
    look = get_look("sig_arctic_glass")
    assert look is not None
    rgb = np.full((24, 24, 3), 0.45, dtype=np.float32)
    from auraforge_engine.signatures import apply_signature

    out = apply_signature(rgb, look)
    assert not np.allclose(out, rgb)
