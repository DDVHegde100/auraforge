"""Camera emulation catalog and apply tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.cameras import apply_camera, load_cameras, load_cameras_by_tag
from auraforge_engine.registry import get_look
from auraforge_engine.pipeline.stack import run_enhance_with_look


def test_load_cameras_count_20() -> None:
    cameras = load_cameras()
    assert len(cameras) >= 30
    assert all(c.kind == "camera" for c in cameras)


def test_camera_ids_present() -> None:
    ids = {c.id for c in load_cameras()}
    expected = {
        "cam_disposable",
        "cam_g7x",
        "cam_fj_color",
        "cam_vcr",
        "cam_chromatic",
        "cam_kino",
        "cam_lomo",
        "cam_extrachrome",
        "cam_mju",
        "cam_super8",
        "cam_kdk2383",
        "cam_lc_color",
        "cam_cinema",
        "cam_sepia",
        "cam_booth",
        "cam_cs500",
        "cam_superia",
    }
    assert expected.issubset(ids)


def test_load_cameras_by_tag_film() -> None:
    film = load_cameras_by_tag("film")
    assert len(film) >= 6


def test_apply_disposable_changes_image() -> None:
    look = get_look("cam_disposable")
    assert look is not None
    rgb = np.full((48, 64, 3), 0.45, dtype=np.float32)
    out = apply_camera(rgb, look)
    assert out.shape == rgb.shape
    assert not np.allclose(out, rgb)


def test_apply_vcr_changes_image() -> None:
    look = get_look("cam_vcr")
    assert look is not None
    rgb = np.random.default_rng(1).random((32, 48, 3)).astype(np.float32) * 0.6 + 0.2
    out = apply_camera(rgb, look)
    assert not np.allclose(out, rgb, atol=0.01)


def test_stack_with_camera() -> None:
    rgb = np.full((24, 32, 3), 0.4, dtype=np.float32)
    out, meta = run_enhance_with_look(
        rgb,
        strength=30.0,
        mode="natural",
        camera_id="cam_g7x",
    )
    assert "camera" in meta["stack_order"]
    assert meta["camera_id"] == "cam_g7x"
    assert out.shape == rgb.shape
