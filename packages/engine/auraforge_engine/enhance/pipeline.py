"""Run develop recipe on rgb."""

from __future__ import annotations

from typing import Any

import numpy as np

from auraforge_engine.develop.pro_pipeline import apply_pro_develop
from auraforge_engine.enhance.recipe import DevelopRecipe
from auraforge_engine.masks.build import MaskPack


def apply_recipe(
    rgb: np.ndarray,
    recipe: DevelopRecipe,
    analysis: dict[str, Any] | None = None,
    masks: MaskPack | None = None,
) -> np.ndarray:
    return apply_pro_develop(rgb, recipe, analysis, masks=masks)
