"""Batch folder processing tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from auraforge_engine.io.export import export_jpeg
from auraforge_engine.pipeline.batch import discover_images, process_batch_folder


def _write_test_jpeg(path: Path) -> None:
    rgb = np.zeros((32, 48, 3), dtype=np.float32)
    rgb[..., 0] = 0.4
    rgb[..., 1] = 0.3
    rgb[..., 2] = 0.5
    export_jpeg(rgb, path)


def test_discover_images(tmp_path: Path) -> None:
    _write_test_jpeg(tmp_path / "a.jpg")
    _write_test_jpeg(tmp_path / "b.png")
    (tmp_path / "notes.txt").write_text("skip")
    found = discover_images(tmp_path)
    assert len(found) == 2


def test_process_batch_folder(tmp_path: Path) -> None:
    _write_test_jpeg(tmp_path / "one.jpg")
    out = tmp_path / "out"
    result = process_batch_folder(tmp_path, strength=40.0, mode="natural", out_dir=out)
    assert result["ok"] == 1
    assert result["count"] == 1
    assert (out / "one_auraforge.jpg").is_file()


def test_process_batch_empty_raises(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no images"):
        process_batch_folder(tmp_path)
