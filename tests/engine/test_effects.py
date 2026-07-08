"""Creative effects tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.effects import highlight_bloom, orton_glow


def test_orton_glow_brightens_midtones() -> None:
    rgb = np.full((32, 32, 3), 0.35, dtype=np.float32)
    out = orton_glow(rgb, blur_sigma=12.0, opacity=0.5)
    assert float(out.mean()) > float(rgb.mean())


def test_orton_zero_opacity_is_identity() -> None:
    rgb = np.random.default_rng(1).random((16, 16, 3)).astype(np.float32)
    out = orton_glow(rgb, opacity=0.0)
    assert np.allclose(out, rgb)


def test_highlight_bloom_lifts_bright_areas() -> None:
    rgb = np.zeros((32, 32, 3), dtype=np.float32)
    rgb[10:20, 10:20] = 0.95
    out = highlight_bloom(rgb, intensity=0.4)
    assert float(out[15, 15].mean()) > float(rgb[15, 15].mean())


from auraforge_engine.effects import soft_haze


def test_soft_haze_lifts_and_desaturates() -> None:
    rgb = np.zeros((16, 16, 3), dtype=np.float32)
    rgb[..., 0] = 0.8
    rgb[..., 1] = 0.2
    out = soft_haze(rgb, lift=0.05, desaturate=0.3)
    assert float(out.mean()) > float(rgb.mean())
    assert float(out[..., 0].std()) < float(rgb[..., 0].std())
