"""Minimal local API shell for auraforge."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from auraforge_engine import __version__
from auraforge_engine.analysis import analyze, analyze_summary
from auraforge_engine.enhance.run import run_enhance
from auraforge_engine.grades.loader import load_grades
from auraforge_engine.io import downscale, load_rgb, rgb_to_data_url
from auraforge_engine.masks.debug import render_mask_overlay
from auraforge_engine.masks.feather import feather_mask
from auraforge_engine.masks.onnx_sky import resolve_sky_mask
from auraforge_engine.masks.skin import skin_soft_mask
from auraforge_engine.masks.subject import subject_mask
from auraforge_engine.registry import load_looks

app = FastAPI(title="auraforge", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"ok": True, "engine": __version__, "name": "auraforge"}


@app.get("/looks")
def looks() -> dict:
    items = [look.to_dict() for look in load_looks()]
    return {"count": len(items), "looks": items}



@app.get("/grades")
def grades(tag: str | None = Query(default=None)) -> dict:
    items = load_grades()
    if tag:
        key = tag.lower()
        items = [g for g in items if key in [t.lower() for t in g.tags]]
    tags: set[str] = set()
    for grade in load_grades():
        tags.update(t.lower() for t in grade.tags)
    return {"count": len(items), "tags": sorted(tags), "grades": [g.to_dict() for g in items]}


@app.post("/process/preview")
async def process_preview(
    file: UploadFile = File(...),
    max_size: int = 1600,
) -> dict:
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    try:
        data = await file.read()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            rgb = load_rgb(tmp.name)
            preview = downscale(rgb, max_size=max_size)
            url = rgb_to_data_url(preview)
        h, w = preview.shape[:2]
        return {
            "ok": True,
            "width": w,
            "height": h,
            "preview": url,
            "name": file.filename,
            "analysis": analyze_summary(preview),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/process/analyze")
async def process_analyze(file: UploadFile = File(...)) -> dict[str, Any]:
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    try:
        data = await file.read()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            rgb = load_rgb(tmp.name)
            return {"ok": True, "name": file.filename, "analysis": analyze(rgb)}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/process/masks")
async def process_masks(
    file: UploadFile = File(...),
    max_size: int = Form(1600),
    use_onnx: bool = Form(False),
) -> dict[str, Any]:
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    try:
        data = await file.read()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            rgb = load_rgb(tmp.name)
            sky, sky_source = resolve_sky_mask(rgb, use_onnx=use_onnx)
            sky = feather_mask(sky, sigma=8.0)
            skin = skin_soft_mask(rgb)
            subject = subject_mask(rgb, skin)
            overlay = render_mask_overlay(rgb, sky=sky, skin=skin, subject=subject)
            preview = downscale(overlay, max_size=max_size)
            url = rgb_to_data_url(preview)
        h, w = preview.shape[:2]
        return {
            "ok": True,
            "width": w,
            "height": h,
            "preview": url,
            "name": file.filename,
            "sky_source": sky_source,
            "sky_mean": float(sky.mean()),
            "skin_mean": float(skin.mean()),
            "subject_mean": float(subject.mean()),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/process/enhance")
async def process_enhance(
    file: UploadFile = File(...),
    strength: float = Form(50.0),
    mode: str = Form("natural"),
    max_size: int = Form(1600),
    use_onnx_sky: bool = Form(False),
) -> dict[str, Any]:
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    try:
        data = await file.read()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            rgb = load_rgb(tmp.name)
            enhanced, meta = run_enhance(
                rgb,
                strength=strength,
                mode=mode,
                use_onnx_sky=use_onnx_sky,
            )
            preview = downscale(enhanced, max_size=max_size)
            url = rgb_to_data_url(preview)
        h, w = preview.shape[:2]
        return {
            "ok": True,
            "width": w,
            "height": h,
            "preview": url,
            "name": file.filename,
            **meta,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
