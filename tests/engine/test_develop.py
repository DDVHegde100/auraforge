"""Develop op tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.develop import (
    apply_clarity,
    apply_contrast,
    apply_dehaze_lite,
    apply_exposure_stops,
    apply_highlight_recovery,
    apply_mild_denoise,
    apply_vibrance_sat,
    apply_vignette,
    apply_warmth_tint,
)


def test_exposure_stops_brightens() -> None:
    rgb = np.full((8, 8, 3), 0.25, dtype=np.float32)
    out = apply_exposure_stops(rgb, 1.0)
    assert float(out.mean()) > float(rgb.mean())


def test_highlight_recovery_compresses() -> None:
    rgb = np.zeros((8, 8, 3), dtype=np.float32)
    rgb[..., :] = (0.95, 0.92, 0.88)
    out = apply_highlight_recovery(rgb, 0.5)
    assert float(out.mean()) < float(rgb.mean())


def test_contrast_midtone() -> None:
    rgb = np.full((8, 8, 3), 0.3, dtype=np.float32)
    out = apply_contrast(rgb, 0.2)
    assert float(out.mean()) > float(rgb.mean())


def test_vibrance_sat_boosts_chroma() -> None:
    rgb = np.zeros((8, 8, 3), dtype=np.float32)
    rgb[..., 0] = 0.5
    rgb[..., 1] = 0.2
    rgb[..., 2] = 0.2
    out = apply_vibrance_sat(rgb, vibrance=0.3, saturation=0.2)
    assert float(out[..., 0].mean()) > float(rgb[..., 0].mean())


def test_clarity_adds_detail() -> None:
    rgb = np.zeros((32, 32, 3), dtype=np.float32)
    rgb[8:24, 8:24] = 0.8
    rgb[12:20, 12:20] = 0.2
    out = apply_clarity(rgb, 0.4)
    assert float(out.std()) >= float(rgb.std())


def test_warmth_shifts_red() -> None:
    rgb = np.full((8, 8, 3), 0.4, dtype=np.float32)
    out = apply_warmth_tint(rgb, warmth=0.5)
    assert float(out[..., 0].mean()) > float(rgb[..., 0].mean())


def test_mild_denoise_runs() -> None:
    rng = np.random.default_rng(0)
    rgb = rng.random((16, 16, 3), dtype=np.float32) * 0.5 + 0.2
    out = apply_mild_denoise(rgb, 0.4)
    assert out.shape == rgb.shape
    assert float(out.mean()) > 0.0


def test_dehaze_lite_brightens() -> None:
    rgb = np.full((32, 32, 3), 0.35, dtype=np.float32)
    rgb[:8, :, :] = 0.55
    out = apply_dehaze_lite(rgb, 0.3)
    assert float(out.mean()) > float(rgb.mean())


def test_vignette_darkens_corners() -> None:
    rgb = np.full((64, 64, 3), 0.6, dtype=np.float32)
    out = apply_vignette(rgb, strength=0.4)
    assert float(out[0, 0].mean()) < float(rgb[0, 0].mean())
    assert float(out[32, 32].mean()) >= float(rgb[32, 32].mean()) - 0.01
