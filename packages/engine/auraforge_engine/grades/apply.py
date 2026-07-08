"""Apply grade stack to rgb."""

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
        "multiscale_detail": lambda rgb, cfg: multiscale_detail(rgb, **cfg),
        "vignette": lambda rgb, cfg: apply_vignette(rgb, **cfg),
        "film_grain": lambda rgb, cfg: film_grain(rgb, **cfg),
        "false_color_thermal": lambda rgb, cfg: false_color_thermal(rgb, **cfg),
        "channel_offset_fringe": lambda rgb, cfg: channel_offset_fringe(rgb, **cfg),
    }


def apply_grade(rgb: np.ndarray, look: Look, *, strength: float = 1.0) -> np.ndarray:
    if look.kind != "grade":
        raise ValueError(f"expected grade look, got {look.kind}")
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
        if t < 1.0 and key == "develop":
            cfg = {k: float(v) * t for k, v in cfg.items() if isinstance(v, (int, float))}
        elif t < 1.0 and "strength" in cfg:
            cfg = {**cfg, "strength": float(cfg["strength"]) * t}
        elif t < 1.0 and "amount" in cfg:
            cfg = {**cfg, "amount": float(cfg["amount"]) * t}
        elif t < 1.0 and "intensity" in cfg:
            cfg = {**cfg, "intensity": float(cfg["intensity"]) * t}
        out = handlers[key](out, cfg)
    return np.clip(out, 0.0, None)
