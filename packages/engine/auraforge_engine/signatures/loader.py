"""Load signature looks."""

from __future__ import annotations

from auraforge_engine.registry import load_looks
from auraforge_engine.schema import Look


def load_signatures(directory=None) -> list[Look]:
    return [look for look in load_looks(directory) if look.kind == "signature"]
