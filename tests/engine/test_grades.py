"""Grade catalog and apply tests."""

from __future__ import annotations

import numpy as np

from auraforge_engine.grades import apply_grade
from auraforge_engine.schema import Look


def test_apply_grade_with_inline_look() -> None:
    look = Look(
        id="test_grade",
        name="test",
        kind="grade",
        stack={"develop": {"contrast": 0.12, "vibrance": 0.08}},
    )
    rgb = np.full((16, 16, 3), 0.4, dtype=np.float32)
    out = apply_grade(rgb, look)
    assert out.shape == rgb.shape
    assert not np.allclose(out, rgb)
