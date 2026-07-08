"""Minimal local API shell for auraforge."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from auraforge_engine import __version__
from auraforge_engine.analysis import analyze, analyze_summary
from auraforge_engine.grades.loader import load_grades
from auraforge_engine.io import downscale
from auraforge_engine.io.preview_cache import PREVIEW_CACHE, load_rgb, rgb_to_data_url, rgb_to_jpeg_bytes, rgb_to_tiff16_bytes
from auraforge_engine.masks.debug import render_mask_overlay
from auraforge_engine.masks.feather import feather_mask
from auraforge_engine.masks.onnx_sky import resolve_sky_mask
from auraforge_engine.masks.skin import skin_soft_mask
from auraforge_engine.masks.subject import subject_mask
from auraforge_engine.pipeline.batch import process_batch_folder
from auraforge_engine.pipeline.stack import run_enhance_with_look
from auraforge_engine.registry import load_looks
from auraforge_engine.signatures.loader import load_signatures

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


@app.get("/cache/stats")
def cache_stats() -> dict:
    return {"ok": True, **PREVIEW_CACHE.stats.to_dict()}


@app.get("/looks")
def looks() -> dict:
    items = [look.to_dict() for look in load_looks()]
    return {"count": len(items), "looks": items}


@app.get("/grades")
def grades(tag: str | None = Query(default=None)) -> dict[str, Any]:
    items = load_grades()
    if tag:
        key = tag.lower()
        items = [g for g in items if key in [t.lower() for t in g.tags]]
    return {"count": len(items), "tags": _grade_tags(), "grades": [g.to_dict() for g in items]}


@app.get("/signatures")
def signatures() -> dict[str, Any]:
    items = load_signatures()
    return {"count": len(items), "signatures": [s.to_dict() for s in items]}


def _grade_tags() -> list[str]:
    tags: set[str] = set()
    for grade in load_grades():
        tags.update(t.lower() for t in grade.tags)
    return sorted(tags)


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
    grade_id: str = Form(""),
    signature_id: str = Form(""),
    max_size: int = Form(1600),
    use_onnx_sky: bool = Form(False),
    pro_safe: bool = Form(True),
) -> dict[str, Any]:
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    try:
        data = await file.read()
        cache_key = PREVIEW_CACHE.make_key(
            data,
            strength=strength,
            mode=mode,
            grade_id=grade_id,
            signature_id=signature_id,
            max_size=max_size,
            use_onnx_sky=use_onnx_sky,
            pro_safe=pro_safe,
        )
        cached = PREVIEW_CACHE.get(cache_key)
        if cached is not None:
            return {**cached, "cached": True}

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            rgb = load_rgb(tmp.name)
            enhanced, meta = run_enhance_with_look(
                rgb,
                strength=strength,
                mode=mode,
                grade_id=grade_id or None,
                signature_id=signature_id or None,
                use_onnx_sky=use_onnx_sky,
                pro_safe=pro_safe,
            )
            preview = downscale(enhanced, max_size=max_size)
            url = rgb_to_data_url(preview)
        h, w = preview.shape[:2]
        payload = {
            "ok": True,
            "width": w,
            "height": h,
            "preview": url,
            "name": file.filename,
            "cached": False,
            **meta,
        }
        PREVIEW_CACHE.set(cache_key, payload)
        return payload
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc




@app.post("/process/batch")
async def process_batch(
    folder: str = Form(...),
    strength: float = Form(50.0),
    mode: str = Form("natural"),
    grade_id: str = Form(""),
    signature_id: str = Form(""),
    out_dir: str = Form(""),
    limit: int = Form(50),
    pro_safe: bool = Form(True),
    use_onnx_sky: bool = Form(False),
) -> dict[str, Any]:
    try:
        result = process_batch_folder(
            folder,
            strength=strength,
            mode=mode,
            grade_id=grade_id or None,
            signature_id=signature_id or None,
            out_dir=out_dir or None,
            limit=limit,
            pro_safe=pro_safe,
            use_onnx_sky=use_onnx_sky,
        )
        return {"ok": True, **result}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/process/export")
async def process_export(
    file: UploadFile = File(...),
    strength: float = Form(50.0),
    mode: str = Form("natural"),
    grade_id: str = Form(""),
    signature_id: str = Form(""),
    fmt: str = Form("jpeg"),
    use_onnx_sky: bool = Form(False),
    pro_safe: bool = Form(True),
) -> Response:
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    try:
        data = await file.read()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            rgb = load_rgb(tmp.name)
            enhanced, _meta = run_enhance_with_look(
                rgb,
                strength=strength,
                mode=mode,
                grade_id=grade_id or None,
                signature_id=signature_id or None,
                use_onnx_sky=use_onnx_sky,
                pro_safe=pro_safe,
            )
        if fmt.lower() in ("tiff", "tif", "tiff16"):
            body = rgb_to_tiff16_bytes(enhanced)
            return Response(
                content=body,
                media_type="image/tiff",
                headers={"Content-Disposition": 'attachment; filename="auraforge.tif"'},
            )
        body = rgb_to_jpeg_bytes(enhanced, quality=92)
        return Response(
            content=body,
            media_type="image/jpeg",
            headers={"Content-Disposition": 'attachment; filename="auraforge.jpg"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
