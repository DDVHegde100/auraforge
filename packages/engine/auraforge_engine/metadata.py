"""Read camera metadata from local image files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS


@dataclass
class ImageMetadata:
    camera_model: str | None = None
    iso: int | None = None

    def is_a6000(self) -> bool:
        if not self.camera_model:
            return False
        model = self.camera_model.upper()
        return "A6000" in model or "ILCE-6000" in model


def read_metadata(path: Path | str) -> ImageMetadata:
    path = Path(path)
    meta = ImageMetadata()
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            if not exif:
                return meta
            parsed = {TAGS.get(k, k): v for k, v in exif.items()}
            if "Model" in parsed:
                meta.camera_model = str(parsed["Model"])
            iso = parsed.get("ISOSpeedRatings") or parsed.get("PhotographicSensitivity")
            if iso is not None:
                meta.iso = int(iso)
    except Exception:
        pass
    return meta
