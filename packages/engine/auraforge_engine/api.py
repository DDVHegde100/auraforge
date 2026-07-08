"""Minimal local API shell for auraforge."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from auraforge_engine import __version__
from auraforge_engine.analysis import analyze
from auraforge_engine.io import downscale, load_rgb, rgb_to_data_url
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
