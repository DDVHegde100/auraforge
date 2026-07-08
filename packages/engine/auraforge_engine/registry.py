"""Load look JSON catalogs from data/looks."""

from __future__ import annotations

import json
from pathlib import Path

from auraforge_engine.schema import Look

ROOT = Path(__file__).resolve().parents[3]
LOOKS_DIR = ROOT / "data" / "looks"


def looks_dir() -> Path:
    return LOOKS_DIR


def load_looks(directory: Path | None = None) -> list[Look]:
    base = directory or LOOKS_DIR
    looks: list[Look] = []
    if not base.is_dir():
        return looks
    for path in sorted(base.glob("*.json")):
        if path.name.startswith("_") and path.name != "_stubs.json":
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict) or "id" not in item:
                continue
            try:
                looks.append(Look.from_dict(item))
            except (KeyError, ValueError, TypeError):
                continue
    return looks


def get_look(look_id: str, directory: Path | None = None) -> Look | None:
    for look in load_looks(directory):
        if look.id == look_id:
            return look
    return None
