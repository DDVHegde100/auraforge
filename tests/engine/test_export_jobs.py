"""Export job queue tests."""

from __future__ import annotations

import time

import numpy as np

from auraforge_engine.jobs.export_job import EXPORT_JOBS, JobStatus
from auraforge_engine.io.preview import rgb_to_jpeg_bytes


def test_export_job_lifecycle() -> None:
    job = EXPORT_JOBS.create(filename="test.jpg", media_type="image/jpeg")
    done = {"flag": False}

    def work(j) -> None:
        rgb = np.full((8, 8, 3), 0.5, dtype=np.float32)
        path = EXPORT_JOBS.output_file(j.job_id, ".jpg")
        path.write_bytes(rgb_to_jpeg_bytes(rgb))
        j.output_path = path

    EXPORT_JOBS.run_async(job.job_id, work)
    for _ in range(50):
        j = EXPORT_JOBS.get(job.job_id)
        if j and j.status == JobStatus.DONE:
            done["flag"] = True
            break
        time.sleep(0.05)
    assert done["flag"]
    assert job.output_path is not None
    assert job.output_path.is_file()
