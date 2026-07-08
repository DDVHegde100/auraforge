#!/usr/bin/env python3
"""Generate before/after showcase tiles from local sample images."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "engine"))

from auraforge_engine.io.export import export_jpeg
from auraforge_engine.io.load import load_rgb
from auraforge_engine.pipeline.stack import run_enhance_with_look

TILES = [
    {
        "id": "portrait_natural",
        "title": "portrait · natural enhance",
        "sample": "samples/portrait_cat.jpg",
        "grade_id": "grade_portrait_warm_honey",
        "signature_id": "sig_velvet_depth",
        "strength": 55,
        "mode": "portrait",
    },
    {
        "id": "landscape_sky",
        "title": "landscape · sky pop",
        "sample": "samples/landscape_sunset.jpg",
        "grade_id": "grade_land_vivid_sky",
        "signature_id": "sig_soft_godray",
        "strength": 60,
        "mode": "land",
    },
]


def main() -> int:
    out_dir = ROOT / "data" / "showcase" / "tiles"
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_tiles = []

    for spec in TILES:
        sample = ROOT / spec["sample"]
        if not sample.is_file():
            print(f"skip {spec['id']} — missing {sample}")
            continue
        rgb = load_rgb(sample)
        before_path = out_dir / f"{spec['id']}_before.jpg"
        export_jpeg(rgb, before_path, quality=90)
        enhanced, _meta = run_enhance_with_look(
            rgb,
            strength=spec["strength"],
            mode=spec["mode"],
            grade_id=spec.get("grade_id"),
            signature_id=spec.get("signature_id"),
        )
        after_path = out_dir / f"{spec['id']}_after.jpg"
        export_jpeg(enhanced, after_path, quality=90)
        manifest_tiles.append(
            {
                "id": spec["id"],
                "title": spec["title"],
                "grade": spec.get("grade_id"),
                "signature": spec.get("signature_id"),
                "before": f"/data/showcase/tiles/{before_path.name}",
                "after": f"/data/showcase/tiles/{after_path.name}",
            }
        )
        print(f"ok  {spec['id']}")

    manifest = {"tiles": manifest_tiles}
    manifest_path = ROOT / "data" / "showcase" / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {manifest_path} ({len(manifest_tiles)} tiles)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
