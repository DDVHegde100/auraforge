"""Load camera emulation looks from catalog."""

from __future__ import annotations

from auraforge_engine.registry import load_looks
from auraforge_engine.schema import Look


def load_cameras(directory=None) -> list[Look]:
    return [look for look in load_looks(directory) if look.kind == "camera"]


def load_cameras_by_tag(tag: str, directory=None) -> list[Look]:
    tag = tag.lower()
    return [c for c in load_cameras(directory) if tag in [t.lower() for t in c.tags]]
