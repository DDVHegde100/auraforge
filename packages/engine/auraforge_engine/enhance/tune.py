"""User tune sliders (0–100, 50 = neutral for tone axes)."""

from __future__ import annotations

from dataclasses import asdict, dataclass

from auraforge_engine.enhance.recipe import DevelopRecipe


@dataclass
class TuneParams:
    clarity: float = 50.0
    detail: float = 50.0
    light: float = 50.0
    shadows: float = 50.0
    highlights: float = 50.0
    warmth: float = 50.0
    look_amount: float = 100.0

    def to_dict(self) -> dict[str, float]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> TuneParams:
        return cls(
            clarity=float(data.get("clarity", 50.0)),
            detail=float(data.get("detail", 50.0)),
            light=float(data.get("light", 50.0)),
            shadows=float(data.get("shadows", 50.0)),
            highlights=float(data.get("highlights", 50.0)),
            warmth=float(data.get("warmth", 50.0)),
            look_amount=float(data.get("look_amount", 100.0)),
        )


def _norm(v: float) -> float:
    return max(-1.0, min(1.0, (float(v) - 50.0) / 50.0))


def merge_tune_into_recipe(recipe: DevelopRecipe, tune: TuneParams) -> DevelopRecipe:
    data = recipe.to_dict()
    data["shadow_lift"] = float(data.get("shadow_lift", 0.0)) + _norm(tune.shadows) * 0.16
    data["highlight_recovery"] = float(data.get("highlight_recovery", 0.0)) + _norm(tune.highlights) * 0.18
    data["warmth"] = float(data.get("warmth", 0.0)) + _norm(tune.warmth) * 0.28
    data["clarity"] = float(data.get("clarity", 0.0)) + _norm(tune.clarity) * 0.14
    data["contrast"] = float(data.get("contrast", 0.0)) + _norm(tune.clarity) * 0.06
    data["vibrance"] = float(data.get("vibrance", 0.0)) + _norm(tune.light) * 0.08
    return DevelopRecipe(**data)
