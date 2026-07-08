"""Camera emulation tests — film stock color science."""

from __future__ import annotations

import numpy as np

from auraforge_engine.cameras.film_stock import apply_film_stock, list_stocks
from auraforge_engine.registry import get_look
from auraforge_engine.cameras import apply_camera


def test_list_stocks() -> None:
    stocks = list_stocks()
    assert "portra_400" in stocks
    assert len(stocks) >= 10


def test_portra_differs_from_ektar() -> None:
    rgb = np.linspace(0.05, 0.95, 48 * 64 * 3, dtype=np.float32).reshape(48, 64, 3)
    portra = apply_film_stock(rgb, stock="portra_400", strength=1.0)
    ektar = apply_film_stock(rgb, stock="ektar_100", strength=1.0)
    assert not np.allclose(portra, ektar, atol=0.01)


def test_cinestill_halation_camera() -> None:
    look = get_look("cam_cinestill_800t")
    assert look is not None
    rgb = np.full((32, 48, 3), 0.35, dtype=np.float32)
    rgb[10:14, 20:28, :] = 0.95
    out = apply_camera(rgb, look)
    assert out.shape == rgb.shape
    assert float(out[..., 0].mean()) > float(rgb[..., 0].mean())


def test_leica_m6_applies() -> None:
    look = get_look("cam_leica_m6")
    assert look is not None
    assert look.meta.get("lens")
    rgb = np.random.default_rng(4).random((24, 32, 3)).astype(np.float32) * 0.5 + 0.2
    out = apply_camera(rgb, look)
    assert not np.allclose(out, rgb, atol=0.005)
