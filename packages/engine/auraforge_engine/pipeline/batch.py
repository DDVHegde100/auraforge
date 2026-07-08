"""Batch process images in a local folder (server-side paths only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from auraforge_engine.io.export import export_jpeg
from auraforge_engine.io.load import JPEG_PNG, RAW, TIFF, load_rgb
from auraforge_engine.metadata import read_metadata
from auraforge_engine.enhance.tune import TuneParams
from auraforge_engine.pipeline.stack import run_enhance_with_look
from auraforge_engine.profiles.a6000 import apply_a6000_base, should_apply_a6000

IMAGE_SUFFIXES = JPEG_PNG | TIFF | RAW


def discover_images(folder: Path, *, limit: int = 50) -> list[Path]:
    folder = Path(folder).expanduser().resolve()
    if not folder.is_dir():
        raise ValueError(f"not a directory: {folder}")
    files: list[Path] = []
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix in IMAGE_SUFFIXES:
            files.append(path)
            if len(files) >= limit:
                break
    return files


def _prepare_rgb(path: Path, *, use_a6000_profile: bool) -> tuple[Any, dict[str, Any]]:
    rgb = load_rgb(path)
    meta: dict[str, Any] = {"path": str(path), "name": path.name}
    exif = read_metadata(path)
    meta["camera_model"] = exif.camera_model
    if should_apply_a6000(exif, use_a6000_profile):
        rgb = apply_a6000_base(rgb)
        meta["a6000_profile"] = True
    return rgb, meta


def process_batch_folder(
    folder: str | Path,
    *,
    strength: float = 50.0,
    mode: str = "natural",
    grade_id: str | None = None,
    camera_id: str | None = None,
    signature_id: str | None = None,
    pro_safe: bool = True,
    use_onnx_sky: bool = False,
    use_a6000_profile: bool = False,
    tune: TuneParams | None = None,
    out_dir: str | Path | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Enhance every image in *folder*; optionally write JPEG exports."""
    root = Path(folder).expanduser().resolve()
    images = discover_images(root, limit=limit)
    if not images:
        raise ValueError(f"no images found in {root}")

    dest = Path(out_dir).expanduser().resolve() if out_dir else None
    if dest:
        dest.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for path in images:
        try:
            rgb, prep = _prepare_rgb(path, use_a6000_profile=use_a6000_profile)
            enhanced, meta = run_enhance_with_look(
                rgb,
                strength=strength,
                mode=mode,
                grade_id=grade_id,
                camera_id=camera_id,
                signature_id=signature_id,
                pro_safe=pro_safe,
                use_onnx_sky=use_onnx_sky,
                tune=tune,
            )
            entry: dict[str, Any] = {**prep, "ok": True, "stack_order": meta.get("stack_order")}
            if dest:
                out_path = dest / f"{path.stem}_auraforge.jpg"
                export_jpeg(enhanced, out_path, quality=92)
                entry["output"] = str(out_path)
            results.append(entry)
        except Exception as exc:
            results.append({"path": str(path), "name": path.name, "ok": False, "error": str(exc)})

    ok_count = sum(1 for r in results if r.get("ok"))
    return {
        "folder": str(root),
        "count": len(results),
        "ok": ok_count,
        "failed": len(results) - ok_count,
        "output_dir": str(dest) if dest else None,
        "results": results,
    }
