"""Tune slider tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.effects.light_remap import light_remap
from auraforge_engine.effects.upscale_detail import upscale_detail
from auraforge_engine.enhance.run import run_enhance
from auraforge_engine.enhance.tune import TuneParams, merge_tune_into_recipe
from auraforge_engine.enhance.recipe import DevelopRecipe


def test_merge_tune_boosts_clarity() -> None:
    base = DevelopRecipe()
    tuned = merge_tune_into_recipe(base, TuneParams(clarity=80))
    assert tuned.clarity > base.clarity


def test_light_remap_changes_image() -> None:
    rgb = np.full((32, 32, 3), 0.45, dtype=np.float32)
    out = light_remap(rgb, strength=0.6)
    assert not np.allclose(out, rgb)


def test_upscale_detail_sharpens() -> None:
    rgb = np.random.default_rng(2).random((48, 64, 3)).astype(np.float32) * 0.5 + 0.2
    out = upscale_detail(rgb, strength=0.7)
    assert out.shape == rgb.shape
    assert not np.allclose(out, rgb, atol=0.001)


def test_run_enhance_with_tune_detail() -> None:
    rgb = np.random.default_rng(9).random((48, 64, 3)).astype(np.float32) * 0.45 + 0.2
    out_lo, meta_lo = run_enhance(rgb, strength=70, tune=TuneParams(detail=20))
    out_hi, meta_hi = run_enhance(rgb, strength=70, tune=TuneParams(detail=90))
    assert "tune" in meta_hi
    assert meta_hi["recipe"]["sharpen"] > meta_lo["recipe"]["sharpen"]
    assert not np.allclose(out_hi, out_lo, atol=0.002)
