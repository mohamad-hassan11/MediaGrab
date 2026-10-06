from dataclasses import dataclass
from pathlib import Path
from threading import Lock


@dataclass
class DownloadJob:
    job_id: str

    status: str = "queued"

    progress: float = 0

    speed: str | None = None

    eta: str | None = None

    error: str | None = None

    file_path: Path | None = None


_jobs: dict[str, DownloadJob] = {}

_lock = Lock()


def create_job(
    job_id: str
) -> DownloadJob:

    job = DownloadJob(
        job_id=job_id
    )

    with _lock:
        _jobs[job_id] = job

    return job



def get_job(
    job_id: str
) -> DownloadJob | None:

    with _lock:
        return _jobs.get(job_id)



def update_job(
    job_id: str,
    **changes
) -> None:

    with _lock:
        job = _jobs.get(job_id)

        if job is None:
            return

        for key, value in changes.items():
            setattr(job, key, value)



def delete_job(
    job_id: str
) -> None:

    with _lock:
        _jobs.pop(job_id, None)