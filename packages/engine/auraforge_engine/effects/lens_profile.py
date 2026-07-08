"""Lens optical character — MTF falloff, vignette, subtle CA."""

from __future__ import annotations

import cv2
import numpy as np

from auraforge_engine.effects.chromatic_aberration import chromatic_aberration
from auraforge_engine.develop import apply_vignette


def lens_profile(
    rgb: np.ndarray,
    *,
    character: str = "standard",
    softness: float = 0.0,
    vignette: float = 0.0,
    ca_strength: float = 0.0,
    center_sharp: bool = True,
) -> np.ndarray:
    out = rgb.astype(np.float32, copy=True)
    h, w = out.shape[:2]

    if softness > 0.0:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        cx, cy = w * 0.5, h * 0.5
        r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max(cx, cy)
        if center_sharp:
            falloff = np.clip(r ** 1.8, 0.0, 1.0)
        else:
            falloff = np.clip(1.0 - r ** 1.2, 0.0, 1.0)
        blur = cv2.GaussianBlur(out, (0, 0), sigmaX=softness * 2.5 + 0.5)
        out = out * (1.0 - falloff[..., None] * softness) + blur * falloff[..., None] * softness

    if character == "zeiss":
        out = apply_vignette(out, strength=vignette * 0.85, feather=0.72)
        if ca_strength > 0:
            out = chromatic_aberration(out, strength=ca_strength * 0.6, radial_power=1.2, max_shift=2.5)
    elif character == "summicron":
        out = apply_vignette(out, strength=vignette * 1.05, feather=0.68)
        if ca_strength > 0:
            out = chromatic_aberration(out, strength=ca_strength * 0.45, radial_power=1.35, max_shift=2.0)
    elif character == "toy":
        out = apply_vignette(out, strength=max(vignette, 0.15), feather=0.42)
        if ca_strength > 0:
            out = chromatic_aberration(out, strength=ca_strength * 1.2, radial_power=1.6, max_shift=5.0)
    elif character == "cinema":
        out = apply_vignette(out, strength=vignette * 0.7, feather=0.82)
    else:
        if vignette > 0:
            out = apply_vignette(out, strength=vignette, feather=0.65)
        if ca_strength > 0:
            out = chromatic_aberration(out, strength=ca_strength, radial_power=1.4, max_shift=3.0)

    return np.clip(out, 0.0, None)
