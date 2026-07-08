"""Roundtrip io fixtures — jpeg/tiff load ↔ export."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from auraforge_engine.io import downscale, export_jpeg, export_tiff16, load_rgb


@pytest.fixture
def sample_rgb() -> np.ndarray:
    h, w = 48, 64
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    r = x / w
    g = y / h
    b = 1.0 - (x + y) / (w + h)
    return np.stack([r, g, b], axis=-1)


def test_jpeg_roundtrip(tmp_path: Path, sample_rgb: np.ndarray) -> None:
    path = tmp_path / "sample.jpg"
    export_jpeg(sample_rgb, path, quality=95)
    loaded = load_rgb(path)
    assert loaded.shape == sample_rgb.shape
    assert loaded.dtype == np.float32
    assert 0.0 <= float(loaded.min()) <= float(loaded.max()) <= 1.0
    # lossy — stay roughly close
    assert float(np.mean(np.abs(loaded - sample_rgb))) < 0.12


def test_tiff16_roundtrip(tmp_path: Path, sample_rgb: np.ndarray) -> None:
    path = tmp_path / "sample.tif"
    export_tiff16(sample_rgb, path)
    loaded = load_rgb(path)
    assert loaded.shape == sample_rgb.shape
    assert float(np.max(np.abs(loaded - sample_rgb))) < 1e-3


def test_downscale_caps_long_edge(sample_rgb: np.ndarray) -> None:
    big = np.zeros((1200, 1800, 3), dtype=np.float32)
    out = downscale(big, max_size=400)
    assert max(out.shape[0], out.shape[1]) <= 400
