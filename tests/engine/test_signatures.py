"""Signature look tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.registry import get_look
from auraforge_engine.signatures import apply_signature, load_signatures


def test_load_signatures() -> None:
    sigs = load_signatures()
    assert len(sigs) >= 12
    assert all(s.kind == "signature" for s in sigs)


def test_apply_floating_light() -> None:
    look = get_look("sig_floating_light")
    assert look is not None
    rgb = np.full((32, 32, 3), 0.40, dtype=np.float32)
    rgb[10:22, 10:22] = 0.85
    out = apply_signature(rgb, look)
    assert float(out.mean()) > float(rgb.mean())


def test_apply_thermal() -> None:
    look = get_look("sig_thermal_spectrum")
    assert look is not None
    rgb = np.linspace(0.1, 0.9, 32, dtype=np.float32)
    rgb = np.stack([rgb, rgb, rgb], axis=-1)
    out = apply_signature(rgb, look)
    assert not np.allclose(out, rgb)


def test_arctic_glass_exists() -> None:
    from auraforge_engine.registry import get_look
    assert get_look("sig_arctic_glass") is not None
    assert get_look("sig_paper_print") is not None


def test_batch_6_signatures() -> None:
    from auraforge_engine.registry import get_look
    assert get_look("sig_hyper_clarity") is not None
    assert get_look("sig_spectrum_split") is not None
