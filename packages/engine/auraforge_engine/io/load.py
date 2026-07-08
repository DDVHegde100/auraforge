"""Load common image formats into float32 RGB [0, 1]."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import tifffile

JPEG_PNG = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG", ".webp", ".WEBP"}
HEIC = {".heic", ".HEIC", ".heif", ".HEIF"}
TIFF = {".tif", ".tiff", ".TIF", ".TIFF"}
RAW = {".arw", ".ARW", ".dng", ".DNG", ".nef", ".NEF", ".cr2", ".CR2", ".cr3", ".CR3"}


def load_jpeg_png(path: Path | str) -> np.ndarray:
    path = Path(path)
    if path.suffix not in JPEG_PNG:
        raise ValueError(f"not jpeg/png: {path.suffix}")
    bgr = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError(f"could not read {path}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return rgb.astype(np.float32) / 255.0


def load_tiff(path: Path | str) -> np.ndarray:
    path = Path(path)
    if path.suffix not in TIFF:
        raise ValueError(f"not tiff: {path.suffix}")
    arr = tifffile.imread(str(path))
    if arr.ndim == 2:
        arr = np.stack([arr, arr, arr], axis=-1)
    elif arr.ndim == 3 and arr.shape[-1] == 4:
        arr = arr[..., :3]
    if arr.dtype == np.uint16:
        return arr.astype(np.float32) / 65535.0
    if arr.dtype == np.uint8:
        return arr.astype(np.float32) / 255.0
    return np.clip(arr.astype(np.float32), 0.0, 1.0)


def load_raw(path: Path | str) -> np.ndarray:
    """optional raw decode — needs rawpy."""
    path = Path(path)
    if path.suffix not in RAW:
        raise ValueError(f"not raw: {path.suffix}")
    try:
        import rawpy
    except ImportError as exc:
        raise ImportError("rawpy required for raw files: pip install auraforge-engine[raw]") from exc
    with rawpy.imread(str(path)) as raw:
        rgb16 = raw.postprocess(
            use_camera_wb=True,
            no_auto_bright=True,
            output_bps=16,
            gamma=(1, 1),
            output_color=rawpy.ColorSpace.sRGB,
        )
    return rgb16.astype(np.float32) / 65535.0


def load_heic(path: Path | str) -> np.ndarray:
    path = Path(path)
    if path.suffix not in HEIC:
        raise ValueError(f"not heic: {path.suffix}")
    try:
        from pillow_heif import register_heif_opener

        register_heif_opener()
    except ImportError:
        pass
    from PIL import Image

    with Image.open(path) as img:
        rgb8 = np.array(img.convert("RGB"), dtype=np.uint8)
    return rgb8.astype(np.float32) / 255.0


def load_rgb(path: Path | str) -> np.ndarray:
    path = Path(path)
    if path.suffix in JPEG_PNG:
        return load_jpeg_png(path)
    if path.suffix in HEIC:
        return load_heic(path)
    if path.suffix in TIFF:
        return load_tiff(path)
    if path.suffix in RAW:
        return load_raw(path)
    raise ValueError(
        f"unsupported type: {path.suffix} — use JPEG, PNG, HEIC, TIFF, or RAW (.arw). "
        "for iPhone HEIC: pip install pillow-heif"
    )
