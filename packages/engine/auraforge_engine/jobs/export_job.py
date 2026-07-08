"""Background export jobs — stable full-res downloads for large images."""

from __future__ import annotations

import json
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

DEFAULT_EXPORT_DIR = os.environ.get("AURAFORGE_EXPORT_DIR", "")
JOB_TTL_SEC = 3600


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


@dataclass
class ExportJob:
    job_id: str
    status: JobStatus = JobStatus.QUEUED
    progress: float = 0.0
    message: str = "queued"
    filename: str = "auraforge.jpg"
    media_type: str = "image/jpeg"
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    output_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "progress": round(self.progress, 3),
            "message": self.message,
            "filename": self.filename,
            "media_type": self.media_type,
            "error": self.error,
            "created_at": self.created_at,
            "finished_at": self.finished_at,
            "download_url": f"/jobs/{self.job_id}/download" if self.status == JobStatus.DONE else None,
        }


class ExportJobStore:
    def __init__(self, export_dir: str | None = None, max_jobs: int = 24) -> None:
        self._jobs: dict[str, ExportJob] = {}
        self._lock = threading.Lock()
        self.max_jobs = max_jobs
        base = export_dir if export_dir is not None else DEFAULT_EXPORT_DIR
        self._dir = Path(base) if base else Path(tempfile_subdir())
        self._dir.mkdir(parents=True, exist_ok=True)

    def create(self, filename: str, media_type: str) -> ExportJob:
        job_id = uuid.uuid4().hex[:16]
        job = ExportJob(job_id=job_id, filename=filename, media_type=media_type)
        with self._lock:
            self._jobs[job_id] = job
            self._prune()
        return job

    def get(self, job_id: str) -> ExportJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def run_async(self, job_id: str, fn: Callable[[ExportJob], None]) -> None:
        def worker() -> None:
            job = self.get(job_id)
            if job is None:
                return
            job.status = JobStatus.RUNNING
            job.message = "processing"
            job.progress = 0.05
            try:
                fn(job)
                job.status = JobStatus.DONE
                job.progress = 1.0
                job.message = "ready"
                job.finished_at = time.time()
            except Exception as exc:
                job.status = JobStatus.ERROR
                job.error = str(exc)
                job.message = "failed"
                job.finished_at = time.time()

        threading.Thread(target=worker, daemon=True).start()

    def output_file(self, job_id: str, ext: str) -> Path:
        return self._dir / f"{job_id}{ext}"

    def _prune(self) -> None:
        if len(self._jobs) <= self.max_jobs:
            return
        now = time.time()
        stale = [
            jid
            for jid, j in self._jobs.items()
            if j.finished_at and now - j.finished_at > JOB_TTL_SEC
        ]
        for jid in stale:
            job = self._jobs.pop(jid, None)
            if job and job.output_path and job.output_path.is_file():
                job.output_path.unlink(missing_ok=True)


def tempfile_subdir() -> str:
    import tempfile

    p = Path(tempfile.gettempdir()) / "auraforge-exports"
    p.mkdir(parents=True, exist_ok=True)
    return str(p)


EXPORT_JOBS = ExportJobStore()
