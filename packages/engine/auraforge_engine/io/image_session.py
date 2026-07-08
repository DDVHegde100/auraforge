"""In-memory image sessions — upload once, tune many times."""

from __future__ import annotations

import hashlib
import tempfile
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from auraforge_engine.io.load import load_rgb
from auraforge_engine.metadata import read_metadata
from auraforge_engine.profiles.a6000 import apply_a6000_base, should_apply_a6000


@dataclass
class ImageSession:
    session_id: str
    rgb: np.ndarray
    filename: str
    prep_meta: dict[str, Any]


class ImageSessionStore:
    def __init__(self, max_entries: int = 6) -> None:
        self.max_entries = max_entries
        self._data: OrderedDict[str, ImageSession] = OrderedDict()

    def open(
        self,
        file_bytes: bytes,
        suffix: str,
        *,
        use_a6000_profile: bool = False,
        filename: str = "upload.jpg",
    ) -> ImageSession:
        digest = hashlib.sha256(file_bytes).hexdigest()[:24]
        if digest in self._data:
            self._data.move_to_end(digest)
            return self._data[digest]

        with tempfile.NamedTemporaryFile(suffix=suffix or ".jpg", delete=True) as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            path = tmp.name
            rgb = load_rgb(path)
            prep_meta: dict[str, Any] = {}
            exif = read_metadata(path)
            prep_meta["camera_model"] = exif.camera_model
            if should_apply_a6000(exif, use_a6000_profile):
                rgb = apply_a6000_base(rgb)
                prep_meta["a6000_profile"] = True

        session = ImageSession(
            session_id=digest,
            rgb=rgb,
            filename=filename,
            prep_meta=prep_meta,
        )
        self._data[digest] = session
        while len(self._data) > self.max_entries:
            self._data.popitem(last=False)
        return session

    def get(self, session_id: str) -> ImageSession | None:
        if session_id not in self._data:
            return None
        self._data.move_to_end(session_id)
        return self._data[session_id]


IMAGE_SESSIONS = ImageSessionStore()
