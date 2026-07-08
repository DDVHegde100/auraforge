"""a6000 profile bridge tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.metadata import ImageMetadata
from auraforge_engine.profiles.a6000 import apply_a6000_base, should_apply_a6000


def test_should_apply_a6000_explicit() -> None:
    meta = ImageMetadata(camera_model="Canon")
    assert should_apply_a6000(meta, use_a6000_profile=True)


def test_should_apply_a6000_exif() -> None:
    meta = ImageMetadata(camera_model="ILCE-6000")
    assert should_apply_a6000(meta, use_a6000_profile=False)


def test_apply_a6000_changes_image() -> None:
    rgb = np.full((24, 32, 3), 0.2, dtype=np.float32)
    out = apply_a6000_base(rgb)
    assert out.shape == rgb.shape
    assert float(out.mean()) > float(rgb.mean())
