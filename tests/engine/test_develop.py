"""Develop op tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.develop import apply_exposure_stops


def test_exposure_stops_brightens() -> None:
    rgb = np.full((8, 8, 3), 0.25, dtype=np.float32)
    out = apply_exposure_stops(rgb, 1.0)
    assert float(out.mean()) > float(rgb.mean())
