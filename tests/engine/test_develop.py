"""Develop op tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.develop import apply_exposure_stops, apply_highlight_recovery


def test_exposure_stops_brightens() -> None:
    rgb = np.full((8, 8, 3), 0.25, dtype=np.float32)
    out = apply_exposure_stops(rgb, 1.0)
    assert float(out.mean()) > float(rgb.mean())


def test_highlight_recovery_compresses() -> None:
    rgb = np.zeros((8, 8, 3), dtype=np.float32)
    rgb[..., :] = (0.95, 0.92, 0.88)
    out = apply_highlight_recovery(rgb, 0.5)
    assert float(out.mean()) < float(rgb.mean())
