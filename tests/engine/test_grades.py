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


from auraforge_engine.grades import load_grades_by_tag
from auraforge_engine.registry import get_look


def test_portrait_grades_1_5() -> None:
    assert get_look("grade_portrait_natural") is not None
    assert get_look("grade_portrait_matte_film") is not None
    assert len(load_grades_by_tag("portrait")) >= 5


def test_portrait_grades_6_10() -> None:
    assert get_look("grade_portrait_bw_ink") is not None
    assert get_look("grade_portrait_moody_rembrandt") is not None
    assert len(load_grades_by_tag("portrait")) >= 10


def test_food_grades() -> None:
    assert get_look("grade_food_appetite") is not None
    assert get_look("grade_food_street_night") is not None


def test_landscape_grades() -> None:
    assert get_look("grade_land_vivid_sky") is not None
    assert get_look("grade_land_pastel_travel") is not None
