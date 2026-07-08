"""Pro develop pipeline tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.analysis import analyze
from auraforge_engine.develop.pro_pipeline import apply_pro_develop
from auraforge_engine.develop.sharpen_capture import apply_capture_sharpen
from auraforge_engine.develop.tone import apply_parametric_tone
from auraforge_engine.enhance.recipe import DevelopRecipe, recipe_from_analysis
from auraforge_engine.enhance.run import run_enhance


def test_parametric_tone_lifts_shadows() -> None:
    rgb = np.full((32, 48, 3), 0.12, dtype=np.float32)
    out = apply_parametric_tone(rgb, shadows=0.22)
    assert float(out.mean()) > float(rgb.mean()) * 1.15


def test_capture_sharpen_preserves_shape() -> None:
    rgb = np.random.default_rng(3).random((40, 40, 3)).astype(np.float32) * 0.5 + 0.2
    out = apply_capture_sharpen(rgb, 0.12)
    assert out.shape == rgb.shape


def test_pro_develop_from_analysis() -> None:
    rgb = np.zeros((36, 48, 3), dtype=np.float32)
    rgb[..., 1] = 0.14
    rgb[..., 2] = 0.20
    analysis = analyze(rgb)
    recipe = recipe_from_analysis(analysis)
    out = apply_pro_develop(rgb, recipe, analysis)
    assert float(out.mean()) > float(rgb.mean())
    assert recipe.sharpen > 0.0
    assert recipe.hsl_selective > 0.0


def test_run_enhance_pro_engine() -> None:
    rgb = np.full((24, 32, 3), 0.35, dtype=np.float32)
    out, meta = run_enhance(rgb, strength=70.0, mode="natural")
    assert meta["engine"] == "pro_develop_v2"
    assert out.shape == rgb.shape
