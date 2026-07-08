"""Load and filter grade looks from catalog."""

from __future__ import annotations

from auraforge_engine.registry import load_looks
from auraforge_engine.schema import Look


def load_grades(directory=None) -> list[Look]:
    return [look for look in load_looks(directory) if look.kind == "grade"]


def load_grades_by_tag(tag: str, directory=None) -> list[Look]:
    tag = tag.lower()
    return [g for g in load_grades(directory) if tag in [t.lower() for t in g.tags]]
