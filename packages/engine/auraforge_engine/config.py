"""Production configuration from environment."""

from __future__ import annotations

import os


def cors_origins() -> list[str]:
    raw = os.environ.get("AURAFORGE_CORS_ORIGINS", "*")
    if raw.strip() == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


def max_upload_bytes() -> int:
    mb = float(os.environ.get("AURAFORGE_MAX_UPLOAD_MB", "40"))
    return int(mb * 1024 * 1024)


def session_dir() -> str:
    return os.environ.get("AURAFORGE_SESSION_DIR", "")


def export_dir() -> str:
    return os.environ.get("AURAFORGE_EXPORT_DIR", "")
