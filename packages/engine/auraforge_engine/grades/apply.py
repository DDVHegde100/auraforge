"""Apply grade look stacks."""

from __future__ import annotations

import numpy as np

from auraforge_engine.looks.stack_apply import apply_look_stack
from auraforge_engine.schema import Look


def apply_grade(rgb: np.ndarray, look: Look, *, strength: float = 1.0) -> np.ndarray:
    if look.kind != "grade":
        raise ValueError(f"expected grade look, got {look.kind}")
    return apply_look_stack(rgb, look, strength=strength)
