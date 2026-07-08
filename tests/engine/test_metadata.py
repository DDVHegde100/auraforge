"""Metadata reader tests."""

from __future__ import annotations

from auraforge_engine.metadata import ImageMetadata, read_metadata


def test_is_a6000() -> None:
    meta = ImageMetadata(camera_model="ILCE-6000")
    assert meta.is_a6000()
    meta2 = ImageMetadata(camera_model="Canon EOS R5")
    assert not meta2.is_a6000()


def test_read_metadata_missing_file(tmp_path) -> None:
    meta = read_metadata(tmp_path / "nope.jpg")
    assert meta.camera_model is None
