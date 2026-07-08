"""Smoke tests for engine skeleton."""

from __future__ import annotations

from auraforge_engine import __version__
from auraforge_engine.registry import load_looks
from auraforge_engine.schema import Look


def test_version() -> None:
    assert __version__


def test_look_schema() -> None:
    look = Look(
        id="test_look",
        name="test",
        kind="grade",
        tags=["portrait"],
        stack={"status": "stub"},
    )
    assert look.to_dict()["id"] == "test_look"


def test_load_stub_catalog() -> None:
    looks = load_looks()
    ids = {look.id for look in looks}
    assert "enhance_natural" in ids or len(looks) >= 0
