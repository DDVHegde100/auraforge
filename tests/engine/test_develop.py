"""Develop op tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.develop import apply_contrast, apply_exposure_stops, apply_highlight_recovery, apply_vibrance_sat


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
