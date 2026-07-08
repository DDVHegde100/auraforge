"""Optional Sony a6000 base develop bridge (local, no a6000_enhancer import)."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.metadata import ImageMetadata

KIT_LENS_VIGNETTE_STRENGTH = 0.18


def should_apply_a6000(meta: ImageMetadata, use_a6000_profile: bool) -> bool:
    if use_a6000_profile:
        return True
    return meta.is_a6000()


def _luminance(rgb: np.ndarray) -> np.ndarray:
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def apply_a6000_base(
    rgb: np.ndarray,
    *,
    exposure_stops: float = 0.12,
    shadow_lift: float = 0.06,
    highlight_recovery: float = 0.10,
    contrast: float = 0.04,
    saturation: float = 0.03,
    clarity: float = 0.05,
    lens_vignette_correction: float = KIT_LENS_VIGNETTE_STRENGTH,
) -> np.ndarray:
    out = rgb.copy()
    if exposure_stops:
        out = out * (2.0**exposure_stops)
    if shadow_lift > 0:
        lum = _luminance(out)
        shadow_mask = np.clip(1.0 - lum * 2.5, 0.0, 1.0) ** 1.5
        out = out + shadow_lift * shadow_mask[..., None] * (1.0 - out)
    if highlight_recovery > 0:
        lum = _luminance(out)
        hi_mask = np.clip((lum - 0.75) / 0.25, 0.0, 1.0) ** 2.0
        compressed = 0.75 + (np.clip(lum, 0.0, 1.0) - 0.75) * (1.0 - highlight_recovery * 0.65)
        scale = np.divide(
            compressed,
            np.maximum(lum, 1e-6),
            out=np.ones_like(lum),
            where=lum > 1e-6,
        )
        out = out * (1.0 - hi_mask[..., None] + hi_mask[..., None] * scale[..., None])
    if lens_vignette_correction > 0:
        h, w = out.shape[:2]
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        radius = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        max_r = np.sqrt(cx**2 + cy**2)
        gain = 1.0 + lens_vignette_correction * (radius / max_r) ** 2
        out = out * gain[..., None]
    if contrast:
        pivot = 0.18
        out = (out - pivot) * (1.0 + contrast) + pivot
    if saturation:
        lum = _luminance(out)[..., None]
        out = lum + (out - lum) * (1.0 + saturation)
    if clarity > 0:
        blur = cv2.GaussianBlur(out, (0, 0), sigmaX=2.5)
        out = out + (out - blur) * clarity
    return np.clip(out, 0.0, None)
