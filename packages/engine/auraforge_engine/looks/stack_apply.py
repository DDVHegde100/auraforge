"""Shared look stack application for grades and signatures."""

from __future__ import annotations

from typing import Any, Callable

import numpy as np

from auraforge_engine.develop import apply_vignette
from auraforge_engine.effects import (
    channel_offset_fringe,
    false_color_thermal,
    film_grain,
    floating_light_gradient,
    highlight_bloom,
    multiscale_detail,
    orton_glow,
    rim_light,
    soft_haze,
    split_tone,
)
from auraforge_engine.enhance.pipeline import apply_recipe
from auraforge_engine.enhance.recipe import DevelopRecipe
from auraforge_engine.schema import Look

_APPLY_ORDER = (
    "develop",
    "split_tone",
    "soft_haze",
    "highlight_bloom",
    "floating_light_gradient",
    "orton_glow",
    "rim_light",
    "multiscale_detail",
    "vignette",
    "film_grain",
    "false_color_thermal",
    "channel_offset_fringe",
)


def _handlers() -> dict[str, Callable[[np.ndarray, dict[str, Any]], np.ndarray]]:
    return {
        "develop": lambda rgb, cfg: apply_recipe(rgb, DevelopRecipe(**cfg)),
        "split_tone": lambda rgb, cfg: split_tone(rgb, **cfg),
        "soft_haze": lambda rgb, cfg: soft_haze(rgb, **cfg),
        "highlight_bloom": lambda rgb, cfg: highlight_bloom(rgb, **cfg),
        "floating_light_gradient": lambda rgb, cfg: floating_light_gradient(rgb, **cfg),
        "orton_glow": lambda rgb, cfg: orton_glow(rgb, **cfg),
        "rim_light": lambda rgb, cfg: rim_light(rgb, **cfg),
        "multiscale_detail": lambda rgb, cfg: multiscale_detail(rgb, **cfg),
        "vignette": lambda rgb, cfg: apply_vignette(rgb, **cfg),
        "film_grain": lambda rgb, cfg: film_grain(rgb, **cfg),
        "false_color_thermal": lambda rgb, cfg: false_color_thermal(rgb, **cfg),
        "channel_offset_fringe": lambda rgb, cfg: channel_offset_fringe(rgb, **cfg),
    }


def _scale_cfg(key: str, cfg: dict[str, Any], t: float) -> dict[str, Any]:
    if t >= 1.0:
        return cfg
    if key == "develop":
        return {k: float(v) * t for k, v in cfg.items() if isinstance(v, (int, float))}
    for field in ("strength", "amount", "intensity", "opacity"):
        if field in cfg:
            return {**cfg, field: float(cfg[field]) * t}
    return cfg


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
