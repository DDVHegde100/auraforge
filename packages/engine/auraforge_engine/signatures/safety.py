"""Pro-safe clamping for experimental signatures."""

from __future__ import annotations

from auraforge_engine.schema import Look

PRO_SAFE_MAX = 0.60


def clamp_signature_strength(look: Look, strength: float, *, pro_safe: bool = True) -> float:
    t = max(0.0, min(1.0, strength))
    if pro_safe and look.experimental:
        return min(t, PRO_SAFE_MAX)
    return t
