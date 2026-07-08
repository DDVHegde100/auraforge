"""Shared look schema for auraforge catalogs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


LOOK_KINDS = ("signature", "grade", "enhance")


@dataclass
class Look:
    id: str
    name: str
    kind: str
    tags: list[str] = field(default_factory=list)
    experimental: bool = False
    skin_protect: bool = True
    stack: dict[str, Any] = field(default_factory=dict)
    notes: str = ""

    def __post_init__(self) -> None:
        if self.kind not in LOOK_KINDS:
            raise ValueError(f"invalid kind '{self.kind}' — expected one of {LOOK_KINDS}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Look:
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            kind=str(data["kind"]),
            tags=list(data.get("tags") or []),
            experimental=bool(data.get("experimental", False)),
            skin_protect=bool(data.get("skin_protect", True)),
            stack=dict(data.get("stack") or {}),
            notes=str(data.get("notes") or ""),
        )
