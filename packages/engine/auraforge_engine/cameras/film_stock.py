"""Film stock color science — H&D curves, crossover, saturation by luminance."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from auraforge_engine.analysis.histogram import luminance


@dataclass(frozen=True)
class FilmStockProfile:
    name: str
    # Toe / shoulder — controls contrast rolloff
    toe: float
    shoulder: float
    gamma: float
    # Shadow / mid / highlight color crossover (3x3 matrices)
    shadow_matrix: tuple[tuple[float, ...], ...]
    mid_matrix: tuple[tuple[float, ...], ...]
    highlight_matrix: tuple[tuple[float, ...], ...]
    shadow_w: float
    highlight_w: float
    # Saturation vs luminance (shadows less, mids peak)
    sat_shadow: float
    sat_mid: float
    sat_highlight: float
    warmth: float
    tint: float


# Calibrated profiles inspired by published spectral / print characteristics.
STOCKS: dict[str, FilmStockProfile] = {
    "portra_400": FilmStockProfile(
        name="Kodak Portra 400",
        toe=0.18,
        shoulder=0.82,
        gamma=0.92,
        shadow_matrix=((1.02, 0.02, 0.0), (0.0, 1.0, 0.02), (0.0, 0.04, 0.98)),
        mid_matrix=((1.04, -0.01, 0.0), (-0.01, 1.02, 0.01), (0.0, 0.02, 0.98)),
        highlight_matrix=((1.06, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.02, 0.96)),
        shadow_w=0.22,
        highlight_w=0.28,
        sat_shadow=0.88,
        sat_mid=1.08,
        sat_highlight=0.94,
        warmth=0.06,
        tint=0.02,
    ),
    "ektar_100": FilmStockProfile(
        name="Kodak Ektar 100",
        toe=0.12,
        shoulder=0.88,
        gamma=0.96,
        shadow_matrix=((1.0, 0.0, 0.02), (0.0, 1.02, 0.04), (0.02, 0.0, 1.0)),
        mid_matrix=((1.08, -0.02, 0.0), (-0.02, 1.06, 0.0), (0.0, 0.0, 1.04)),
        highlight_matrix=((1.1, 0.0, 0.0), (0.0, 1.04, 0.0), (0.0, 0.0, 1.02)),
        shadow_w=0.18,
        highlight_w=0.32,
        sat_shadow=0.92,
        sat_mid=1.18,
        sat_highlight=1.02,
        warmth=-0.02,
        tint=-0.04,
    ),
    "gold_200": FilmStockProfile(
        name="Kodak Gold 200",
        toe=0.20,
        shoulder=0.78,
        gamma=0.90,
        shadow_matrix=((1.04, 0.04, 0.0), (0.02, 1.0, 0.0), (0.0, 0.0, 0.96)),
        mid_matrix=((1.06, 0.02, 0.0), (0.0, 1.02, 0.0), (0.0, 0.02, 0.96)),
        highlight_matrix=((1.08, 0.02, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.94)),
        shadow_w=0.24,
        highlight_w=0.26,
        sat_shadow=0.95,
        sat_mid=1.12,
        sat_highlight=0.98,
        warmth=0.14,
        tint=0.06,
    ),
    "superia_400": FilmStockProfile(
        name="Fuji Superia 400",
        toe=0.16,
        shoulder=0.80,
        gamma=0.91,
        shadow_matrix=((0.98, 0.0, 0.04), (0.0, 1.02, 0.06), (0.04, 0.06, 0.96)),
        mid_matrix=((1.0, -0.02, 0.04), (-0.02, 1.04, 0.04), (0.02, 0.04, 0.98)),
        highlight_matrix=((1.02, 0.0, 0.0), (0.0, 1.0, 0.02), (0.0, 0.04, 0.96)),
        shadow_w=0.26,
        highlight_w=0.24,
        sat_shadow=0.90,
        sat_mid=1.10,
        sat_highlight=0.92,
        warmth=-0.04,
        tint=-0.08,
    ),
    "pro400h": FilmStockProfile(
        name="Fuji Pro 400H",
        toe=0.14,
        shoulder=0.84,
        gamma=0.93,
        shadow_matrix=((0.98, 0.0, 0.06), (0.0, 1.02, 0.08), (0.06, 0.08, 0.94)),
        mid_matrix=((1.02, -0.02, 0.02), (-0.02, 1.04, 0.04), (0.02, 0.04, 0.98)),
        highlight_matrix=((1.04, 0.0, 0.0), (0.0, 1.0, 0.02), (0.0, 0.06, 0.96)),
        shadow_w=0.28,
        highlight_w=0.22,
        sat_shadow=0.86,
        sat_mid=1.06,
        sat_highlight=0.90,
        warmth=-0.06,
        tint=-0.10,
    ),
    "cinestill_800t": FilmStockProfile(
        name="CineStill 800T",
        toe=0.22,
        shoulder=0.76,
        gamma=0.88,
        shadow_matrix=((1.0, 0.0, 0.08), (0.0, 0.98, 0.10), (0.08, 0.10, 0.92)),
        mid_matrix=((1.02, 0.0, 0.04), (0.0, 0.98, 0.06), (0.04, 0.06, 0.94)),
        highlight_matrix=((1.04, 0.02, 0.0), (0.02, 0.96, 0.0), (0.0, 0.0, 0.92)),
        shadow_w=0.30,
        highlight_w=0.20,
        sat_shadow=0.92,
        sat_mid=1.04,
        sat_highlight=0.88,
        warmth=-0.08,
        tint=-0.14,
    ),
    "vision3_500t": FilmStockProfile(
        name="Kodak Vision3 500T",
        toe=0.20,
        shoulder=0.80,
        gamma=0.89,
        shadow_matrix=((1.0, 0.0, 0.06), (0.0, 1.0, 0.08), (0.04, 0.08, 0.94)),
        mid_matrix=((1.04, -0.01, 0.02), (-0.01, 1.02, 0.02), (0.0, 0.02, 0.98)),
        highlight_matrix=((1.06, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.02, 0.96)),
        shadow_w=0.24,
        highlight_w=0.30,
        sat_shadow=0.94,
        sat_mid=1.08,
        sat_highlight=0.96,
        warmth=0.02,
        tint=-0.06,
    ),
    "tri_x_400": FilmStockProfile(
        name="Kodak Tri-X 400",
        toe=0.24,
        shoulder=0.72,
        gamma=0.85,
        shadow_matrix=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        mid_matrix=((1.02, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.98)),
        highlight_matrix=((1.04, 0.0, 0.0), (0.0, 0.98, 0.0), (0.0, 0.0, 0.96)),
        shadow_w=0.32,
        highlight_w=0.18,
        sat_shadow=0.0,
        sat_mid=0.0,
        sat_highlight=0.0,
        warmth=0.04,
        tint=0.0,
    ),
    "hp5_plus": FilmStockProfile(
        name="Ilford HP5 Plus",
        toe=0.26,
        shoulder=0.70,
        gamma=0.84,
        shadow_matrix=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
        mid_matrix=((1.01, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.99)),
        highlight_matrix=((1.02, 0.0, 0.0), (0.0, 0.99, 0.0), (0.0, 0.0, 0.98)),
        shadow_w=0.34,
        highlight_w=0.16,
        sat_shadow=0.0,
        sat_mid=0.0,
        sat_highlight=0.0,
        warmth=0.0,
        tint=0.0,
    ),
    "velvia_50": FilmStockProfile(
        name="Fuji Velvia 50",
        toe=0.10,
        shoulder=0.90,
        gamma=0.98,
        shadow_matrix=((1.0, 0.0, 0.04), (0.0, 1.02, 0.06), (0.04, 0.04, 0.96)),
        mid_matrix=((1.06, -0.04, 0.02), (-0.04, 1.08, 0.02), (0.02, 0.0, 1.06)),
        highlight_matrix=((1.08, 0.0, 0.0), (0.0, 1.04, 0.0), (0.0, 0.0, 1.02)),
        shadow_w=0.16,
        highlight_w=0.36,
        sat_shadow=1.05,
        sat_mid=1.28,
        sat_highlight=1.08,
        warmth=-0.04,
        tint=-0.06,
    ),
}


def _hd_curve(x: np.ndarray, toe: float, shoulder: float, gamma: float) -> np.ndarray:
    """Soft knee film characteristic curve on luminance."""
    x = np.clip(x, 0.0, 1.0)
    toe_mask = x < toe
    shoulder_mask = x > shoulder
    mid = ~(toe_mask | shoulder_mask)
    out = np.empty_like(x)
    out[toe_mask] = (x[toe_mask] / max(toe, 1e-4)) ** 1.35 * toe
    out[mid] = toe + (x[mid] - toe) / max(shoulder - toe, 1e-4) * (shoulder - toe)
    out[shoulder_mask] = shoulder + (1.0 - shoulder) * (
        1.0 - (1.0 - (x[shoulder_mask] - shoulder) / max(1.0 - shoulder, 1e-4)) ** 0.65
    )
    return np.clip(out ** gamma, 0.0, 1.0)


def _apply_matrix(rgb: np.ndarray, matrix: tuple[tuple[float, ...], ...]) -> np.ndarray:
    m = np.array(matrix, dtype=np.float32)
    flat = rgb.reshape(-1, 3)
    return (flat @ m.T).reshape(rgb.shape)


def _luminance_sat(rgb: np.ndarray, sat_map: np.ndarray) -> np.ndarray:
    lum = luminance(rgb)[..., None]
    gray = np.repeat(lum, 3, axis=2)
    sat = sat_map[..., None] if sat_map.ndim == 2 else sat_map
    return np.clip(gray + (rgb - gray) * sat, 0.0, None)


def apply_film_stock(
    rgb: np.ndarray,
    *,
    stock: str = "portra_400",
    strength: float = 1.0,
) -> np.ndarray:
    """Apply film stock color science with luminance-dependent crossover."""
    t = max(0.0, min(1.5, strength))
    if t <= 0.0:
        return rgb
    profile = STOCKS.get(stock.lower().replace("-", "_").replace(" ", "_"))
    if profile is None:
        profile = STOCKS.get(stock, STOCKS["portra_400"])

    work = rgb.astype(np.float32, copy=True)
    lum = luminance(work)

    # H&D curve on luminance, preserve chroma ratio
    curved_lum = _hd_curve(lum, profile.toe, profile.shoulder, profile.gamma)
    scale = np.divide(curved_lum, np.maximum(lum, 1e-4))[..., None]
    work = np.clip(work * scale, 0.0, None)

    # Luminance-zone color crossover
    shadow_w = np.clip(1.0 - lum / max(profile.shadow_w, 1e-4), 0.0, 1.0)[..., None]
    highlight_w = np.clip((lum - (1.0 - profile.highlight_w)) / max(profile.highlight_w, 1e-4), 0.0, 1.0)[
        ..., None
    ]
    mid_w = np.clip(1.0 - shadow_w - highlight_w, 0.0, 1.0)

    sh = _apply_matrix(work, profile.shadow_matrix)
    md = _apply_matrix(work, profile.mid_matrix)
    hi = _apply_matrix(work, profile.highlight_matrix)
    work = work * (1.0 - t) + (sh * shadow_w + md * mid_w + hi * highlight_w) * t

    # Saturation rolloff by zone
    sat_map = (
        profile.sat_shadow * shadow_w[..., 0]
        + profile.sat_mid * mid_w[..., 0]
        + profile.sat_highlight * highlight_w[..., 0]
    )
    sat_map = 1.0 + (sat_map - 1.0) * t
    work = _luminance_sat(work, sat_map)

    # Global warmth / tint in Lab-ish adjustment
    if profile.warmth != 0.0 or profile.tint != 0.0:
        work[..., 0] = np.clip(work[..., 0] + profile.warmth * t * 0.08, 0.0, None)
        work[..., 1] = np.clip(work[..., 1] + profile.tint * t * 0.06, 0.0, None)
        work[..., 2] = np.clip(work[..., 2] - profile.tint * t * 0.04, 0.0, None)

    return np.clip(work, 0.0, None)


def list_stocks() -> list[str]:
    return sorted(STOCKS.keys())
