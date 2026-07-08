"""Shared look stack application for grades, signatures, and cameras."""

from __future__ import annotations

from typing import Any, Callable

import numpy as np

from auraforge_engine.develop import apply_vignette
from auraforge_engine.cameras.film_stock import apply_film_stock
from auraforge_engine.effects.grain_pro import grain_pro
from auraforge_engine.effects.halation import film_halation
from auraforge_engine.effects.lens_profile import lens_profile
from auraforge_engine.effects import (
    barrel_distort,
    channel_offset_fringe,
    chromatic_aberration,
    color_matrix,
    false_color_thermal,
    film_grain,
    floating_light_gradient,
    highlight_bloom,
    light_remap,
    multiscale_detail,
    orton_glow,
    rim_light,
    sepia_tone,
    soft_haze,
    split_tone,
    vcr_tape,
)
from auraforge_engine.enhance.pipeline import apply_recipe
from auraforge_engine.enhance.recipe import DevelopRecipe
from auraforge_engine.schema import Look

# Grades/cameras/signatures were authored conservatively — boost so Filter Strength feels like Luminar.
LOOK_GAIN = 1.75

_APPLY_ORDER = (
    "barrel_distort",
    "lens_profile",
    "film_stock",
    "develop",
    "color_matrix",
    "split_tone",
    "sepia_tone",
    "soft_haze",
    "highlight_bloom",
    "floating_light_gradient",
    "orton_glow",
    "rim_light",
    "multiscale_detail",
    "vignette",
    "grain_pro",
    "film_grain",
    "film_halation",
    "vcr_tape",
    "light_remap",
    "false_color_thermal",
    "chromatic_aberration",
    "channel_offset_fringe",
)


def _handlers() -> dict[str, Callable[[np.ndarray, dict[str, Any]], np.ndarray]]:
    return {
        "barrel_distort": lambda rgb, cfg: barrel_distort(rgb, **cfg),
        "lens_profile": lambda rgb, cfg: lens_profile(rgb, **cfg),
        "film_stock": lambda rgb, cfg: apply_film_stock(
            rgb, stock=str(cfg.get("stock", "portra_400")), strength=float(cfg.get("strength", 1.0))
        ),
        "develop": lambda rgb, cfg: apply_recipe(rgb, DevelopRecipe(**cfg)),
        "color_matrix": lambda rgb, cfg: color_matrix(rgb, **cfg),
        "split_tone": lambda rgb, cfg: split_tone(rgb, **cfg),
        "sepia_tone": lambda rgb, cfg: sepia_tone(rgb, **cfg),
        "soft_haze": lambda rgb, cfg: soft_haze(rgb, **cfg),
        "highlight_bloom": lambda rgb, cfg: highlight_bloom(rgb, **cfg),
        "floating_light_gradient": lambda rgb, cfg: floating_light_gradient(rgb, **cfg),
        "orton_glow": lambda rgb, cfg: orton_glow(rgb, **cfg),
        "rim_light": lambda rgb, cfg: rim_light(rgb, **cfg),
        "multiscale_detail": lambda rgb, cfg: multiscale_detail(rgb, **cfg),
        "vignette": lambda rgb, cfg: apply_vignette(rgb, **cfg),
        "film_grain": lambda rgb, cfg: film_grain(rgb, **cfg),
        "grain_pro": lambda rgb, cfg: grain_pro(rgb, **cfg),
        "film_halation": lambda rgb, cfg: film_halation(rgb, **cfg),
        "vcr_tape": lambda rgb, cfg: vcr_tape(rgb, **cfg),
        "light_remap": lambda rgb, cfg: light_remap(rgb, **cfg),
        "false_color_thermal": lambda rgb, cfg: false_color_thermal(rgb, **cfg),
        "chromatic_aberration": lambda rgb, cfg: chromatic_aberration(rgb, **cfg),
        "channel_offset_fringe": lambda rgb, cfg: channel_offset_fringe(rgb, **cfg),
    }


def _scale_cfg(key: str, cfg: dict[str, Any], t: float) -> dict[str, Any]:
    if t >= 1.0 and LOOK_GAIN <= 1.0:
        return cfg
    eff = t * LOOK_GAIN
    if key == "develop":
        return {k: float(v) * eff for k, v in cfg.items() if isinstance(v, (int, float))}
    if key == "film_stock":
        scaled = dict(cfg)
        scaled["strength"] = float(scaled.get("strength", 1.0)) * eff
        return scaled
    if key == "lens_profile":
        scaled = dict(cfg)
        for field in ("softness", "vignette", "ca_strength"):
            if field in scaled:
                scaled[field] = float(scaled[field]) * eff
        return scaled
    if key == "color_matrix":
        scaled = dict(cfg)
        base = float(scaled.get("strength", 1.0))
        scaled["strength"] = base * eff
        return scaled
    scaled = dict(cfg)
    hit = False
    for field in ("strength", "amount", "intensity", "opacity"):
        if field in scaled:
            scaled[field] = float(scaled[field]) * eff
            hit = True
    if not hit:
        for field in ("lift", "desaturate", "warmth", "vibrance", "contrast"):
            if field in scaled and isinstance(scaled[field], (int, float)):
                scaled[field] = float(scaled[field]) * eff
                hit = True
    return scaled if hit else cfg


def apply_look_stack(rgb: np.ndarray, look: Look, *, strength: float = 1.0) -> np.ndarray:
    stack = look.stack
    if not stack or stack.get("status") == "stub":
        return rgb
    t = max(0.0, min(1.0, strength))
    out = rgb.astype(np.float32, copy=True)
    handlers = _handlers()
    for key in _APPLY_ORDER:
        cfg = stack.get(key)
        if not cfg or not isinstance(cfg, dict):
            continue
        out = handlers[key](out, _scale_cfg(key, cfg, t))
    return np.clip(out, 0.0, None)
