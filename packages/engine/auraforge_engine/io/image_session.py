"""Disk-backed image sessions — survive API restarts on Railway/Fly."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from auraforge_engine.io.load import load_rgb
from auraforge_engine.metadata import read_metadata
from auraforge_engine.profiles.a6000 import apply_a6000_base, should_apply_a6000

SESSION_TTL_SEC = 3600 * 6  # 6 hours
DEFAULT_SESSION_DIR = os.environ.get("AURAFORGE_SESSION_DIR", "")


@dataclass
class ImageSession:
    session_id: str
    rgb: np.ndarray
    filename: str
    prep_meta: dict[str, Any]


class ImageSessionStore:
    def __init__(self, max_entries: int = 12, session_dir: str | None = None) -> None:
        self.max_entries = max_entries
        self._memory: OrderedDict[str, ImageSession] = OrderedDict()
        base = session_dir if session_dir is not None else DEFAULT_SESSION_DIR
        self._dir = Path(base) if base else None
        if self._dir:
            self._dir.mkdir(parents=True, exist_ok=True)

    def _disk_path(self, session_id: str) -> Path | None:
        if not self._dir:
            return None
        return self._dir / f"{session_id}.npz"

    def _meta_path(self, session_id: str) -> Path | None:
        if not self._dir:
            return None
        return self._dir / f"{session_id}.json"

    def _save_disk(self, session: ImageSession) -> None:
        path = self._disk_path(session.session_id)
        meta_path = self._meta_path(session.session_id)
        if path is None or meta_path is None:
            return
        np.savez_compressed(path, rgb=session.rgb.astype(np.float32))
        meta_path.write_text(
            json.dumps(
                {
                    "session_id": session.session_id,
                    "filename": session.filename,
                    "prep_meta": session.prep_meta,
                    "created_at": time.time(),
                }
            ),
            encoding="utf-8",
        )

    def _load_disk(self, session_id: str) -> ImageSession | None:
        path = self._disk_path(session_id)
        meta_path = self._meta_path(session_id)
        if path is None or meta_path is None or not path.is_file() or not meta_path.is_file():
            return None
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            created = float(meta.get("created_at", 0))
            if time.time() - created > SESSION_TTL_SEC:
                path.unlink(missing_ok=True)
                meta_path.unlink(missing_ok=True)
                return None
            data = np.load(path)
            rgb = data["rgb"].astype(np.float32)
            return ImageSession(
                session_id=session_id,
                rgb=rgb,
                filename=str(meta.get("filename", "upload.jpg")),
                prep_meta=dict(meta.get("prep_meta", {})),
            )
        except (OSError, json.JSONDecodeError, KeyError, ValueError):
            return None

    def _evict_old(self) -> None:
        while len(self._memory) > self.max_entries:
            old_id, _ = self._memory.popitem(last=False)
            if self._dir:
                self._disk_path(old_id).unlink(missing_ok=True) if self._disk_path(old_id) else None
                self._meta_path(old_id).unlink(missing_ok=True) if self._meta_path(old_id) else None

    def open(
        self,
        file_bytes: bytes,
        suffix: str,
        *,
        use_a6000_profile: bool = False,
        filename: str = "upload.jpg",
    ) -> ImageSession:
        digest = hashlib.sha256(file_bytes).hexdigest()[:24]
        if digest in self._memory:
            self._memory.move_to_end(digest)
            return self._memory[digest]

        cached = self._load_disk(digest)
        if cached is not None:
            self._memory[digest] = cached
            self._memory.move_to_end(digest)
            return cached

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
        self._memory[digest] = session
        self._save_disk(session)
        self._evict_old()
        return session

    def get(self, session_id: str) -> ImageSession | None:
        if session_id in self._memory:
            self._memory.move_to_end(session_id)
            return self._memory[session_id]
        loaded = self._load_disk(session_id)
        if loaded is not None:
            self._memory[session_id] = loaded
            self._memory.move_to_end(session_id)
            self._evict_old()
        return loaded


IMAGE_SESSIONS = ImageSessionStore()
