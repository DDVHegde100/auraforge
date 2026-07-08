"""Enhance finish pass tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis import analyze
from auraforge_engine.enhance.finish import adaptive_finish
from auraforge_engine.enhance.run import run_enhance


def test_adaptive_finish_changes_image() -> None:
    rgb = np.full((48, 64, 3), 0.32, dtype=np.float32)
    rgb[:, :20, 0] = 0.08
    rgb[:, -20:, 0] = 0.92
    analysis = analyze(rgb)
    out = adaptive_finish(rgb, analysis, strength=0.7)
    assert out.shape == rgb.shape
    assert float(out.mean()) != float(rgb.mean())


def test_run_enhance_lifts_dark_scene() -> None:
    rgb = np.zeros((32, 48, 3), dtype=np.float32)
    rgb[..., 1] = 0.12
    rgb[..., 2] = 0.18
    out, meta = run_enhance(rgb, strength=65.0, mode="natural")
    assert float(out.mean()) > float(rgb.mean()) * 1.12
    assert meta["engine"] == "pro_develop_v2"
