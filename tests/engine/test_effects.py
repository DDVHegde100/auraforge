"""Creative effects tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.effects import (
    channel_offset_fringe,
    false_color_thermal,
    film_grain,
    floating_light_gradient,
    highlight_bloom,
    multiscale_detail,
    orton_glow,
    rim_light,
    soft_haze,
    split_tone,
)


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


def test_soft_haze_lifts_and_desaturates() -> None:
    rgb = np.zeros((16, 16, 3), dtype=np.float32)
    rgb[..., 0] = 0.8
    rgb[..., 1] = 0.2
    out = soft_haze(rgb, lift=0.05, desaturate=0.3)
    assert float(out.mean()) > float(rgb.mean())
    assert float(out[..., 0].std()) < float(rgb[..., 0].std())


def test_floating_light_gradient_adds_glow() -> None:
    rgb = np.full((48, 64, 3), 0.25, dtype=np.float32)
    out = floating_light_gradient(rgb, intensity=0.3)
    assert float(out.mean()) > float(rgb.mean())


def test_rim_light_adds_edge_glow() -> None:
    rgb = np.zeros((32, 32, 3), dtype=np.float32)
    rgb[8:24, 8:24] = 0.55
    out = rim_light(rgb, intensity=0.35)
    assert float(out.max()) > float(rgb.max())


def test_multiscale_detail_increases_variance() -> None:
    rgb = np.zeros((32, 32, 3), dtype=np.float32)
    rgb[8:24, 8:24] = 0.7
    rgb[12:20, 12:20] = 0.25
    out = multiscale_detail(rgb, strength=0.25)
    assert float(out.std()) >= float(rgb.std())


def test_film_grain_changes_pixels() -> None:
    rgb = np.full((24, 24, 3), 0.5, dtype=np.float32)
    out = film_grain(rgb, amount=0.12, seed=7)
    assert not np.allclose(out, rgb)


def test_split_tone_shifts_shadows() -> None:
    rgb = np.zeros((16, 16, 3), dtype=np.float32)
    rgb[..., 2] = 0.15
    out = split_tone(rgb, strength=0.5)
    assert float(out[..., 2].mean()) != float(rgb[..., 2].mean())


def test_false_color_thermal_remaps_luma() -> None:
    rgb = np.zeros((16, 32, 3), dtype=np.float32)
    rgb[:, :8] = 0.1
    rgb[:, 8:16] = 0.4
    rgb[:, 16:24] = 0.7
    rgb[:, 24:] = 0.95
    out = false_color_thermal(rgb, strength=1.0)
    assert float(out[:, 0, 2].mean()) > float(out[:, 24, 2].mean())
    assert float(out[:, 24, 0].mean()) > float(out[:, 0, 0].mean())


def test_channel_offset_fringe_shifts_channels() -> None:
    rgb = np.zeros((24, 24, 3), dtype=np.float32)
    rgb[8:16, 8:16, 0] = 0.9
    rgb[8:16, 8:16, 2] = 0.9
    out = channel_offset_fringe(rgb, strength=0.5, red_offset=(2, 0), blue_offset=(-2, 0))
    assert not np.allclose(out, rgb)
