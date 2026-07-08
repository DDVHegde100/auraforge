"""Export endpoint tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.io import rgb_to_jpeg_bytes, rgb_to_tiff16_bytes


def test_rgb_to_jpeg_bytes() -> None:
    rgb = np.full((8, 8, 3), 0.5, dtype=np.float32)
    data = rgb_to_jpeg_bytes(rgb)
    assert data[:2] == b"\xff\xd8"


def test_rgb_to_tiff16_bytes() -> None:
    rgb = np.full((8, 8, 3), 0.5, dtype=np.float32)
    data = rgb_to_tiff16_bytes(rgb)
    assert len(data) > 100
