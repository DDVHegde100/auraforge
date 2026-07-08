"""Orton glow tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.effects import orton_glow


def test_orton_glow_brightens_midtones() -> None:
    rgb = np.full((32, 32, 3), 0.35, dtype=np.float32)
    out = orton_glow(rgb, blur_sigma=12.0, opacity=0.5)
    assert float(out.mean()) > float(rgb.mean())


def test_orton_zero_opacity_is_identity() -> None:
    rgb = np.random.default_rng(1).random((16, 16, 3)).astype(np.float32)
    out = orton_glow(rgb, opacity=0.0)
    assert np.allclose(out, rgb)
