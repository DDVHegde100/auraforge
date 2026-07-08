"""Scene analysis golden tests on synthetic images."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis import (
    analyze,
    analyze_summary,
    classify_exposure,
    guess_content,
    sky_score,
    skin_score,
)


def _gradient_rgb(h: int = 64, w: int = 96) -> np.ndarray:
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    r = x / w
    g = y / h
    b = 1.0 - (x + y) / (w + h)
    return np.stack([r, g, b], axis=-1)


def test_exposure_under() -> None:
    dark = _gradient_rgb() * 0.15
    out = classify_exposure(dark)
    assert out["exposure_class"] in ("under", "flat")


def test_exposure_over() -> None:
    bright = np.clip(_gradient_rgb() * 0.5 + 0.55, 0.0, 1.0)
    out = classify_exposure(bright)
    assert out["exposure_class"] in ("over", "contrasty", "balanced")


def test_sky_on_blue_top() -> None:
    rgb = np.zeros((80, 120, 3), dtype=np.float32)
    rgb[:30, :, 2] = 0.85
    rgb[:30, :, 1] = 0.55
    rgb[:30, :, 0] = 0.25
    rgb[30:, :, :] = 0.2
    out = sky_score(rgb)
    assert out["sky_score"] > 0.15


def test_skin_on_peach_center() -> None:
    rgb = np.full((80, 80, 3), 0.15, dtype=np.float32)
    rgb[20:60, 20:60, 0] = 0.82
    rgb[20:60, 20:60, 1] = 0.55
    rgb[20:60, 20:60, 2] = 0.42
    out = skin_score(rgb)
    assert out["skin_score"] > 0.05


def test_analyze_summary_keys() -> None:
    summary = analyze_summary(_gradient_rgb())
    for key in ("exposure_class", "content_class", "sky_score", "skin_score", "mean_luma"):
        assert key in summary


def test_analyze_full_structure() -> None:
    full = analyze(_gradient_rgb())
    assert "histogram" in full and "sky" in full and "content" in full


def test_content_not_empty() -> None:
    out = guess_content(_gradient_rgb())
    assert out["content_class"] in ("portrait", "landscape", "food", "general")
