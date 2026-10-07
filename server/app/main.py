import os
import shutil
from pathlib import Path
from uuid import uuid4

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .downloader import TEMP_DIR, download_media
from .jobs import create_job, delete_job, get_job, update_job
from .models import (
    CreateJobResponse,
    DownloadRequest,
    JobStatusResponse,
)

app = FastAPI(
    title="MediaGrab API",
    version="0.1.0",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    swagger_ui_oauth2_redirect_url="/api/docs/oauth2-redirect",
)

# ALLOWED_ORIGINS is a comma-separated list of extra origins to allow
# alongside the defaults below (e.g. a staging/preview deployment domain).
_extra_origins = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://media-grab-sigma.vercel.app",
        *_extra_origins,
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["Content-Type"],
    expose_headers=["Content-Disposition"],
)



@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }

@app.post(
    "/api/jobs",
    response_model=CreateJobResponse
)
def start_download(
    request: DownloadRequest,
    background_tasks: BackgroundTasks
):
    job_id = uuid4().hex

    create_job(job_id)

    background_tasks.add_task(
        process_download,
        job_id,
        request,
    )

    return CreateJobResponse(
        job_id=job_id
    )


@app.get(
    "/api/jobs/{job_id}",
    response_model=JobStatusResponse
)
def job_status(
    job_id: str
):
    job = get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        speed=job.speed,
        eta=job.eta,
        error=job.error,
    )


@app.get(
    "/api/jobs/{job_id}/file"
)
def download_file(
    job_id: str,
    background_tasks: BackgroundTasks
):
    job = get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found."
        )

    if job.status != "completed":
        raise HTTPException(
            status_code=409,
            detail="The download is not completed."
        )

    if (
        job.file_path is None
        or not job.file_path.exists()
    ):
        raise HTTPException(
            status_code=404,
            detail="Download file not found."
        )

    file_path = job.file_path

    background_tasks.add_task(
        delete_directory,
        file_path.parent
    )
    background_tasks.add_task(
        delete_job,
        job_id
    )

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream",
    )


def delete_directory(
    directory: Path
) -> None:
    try:
        shutil.rmtree(
            directory,
            ignore_errors=True
        )
    except OSError:
        pass


def process_download(
    job_id: str,
    request: DownloadRequest
) -> None:

    try:
        file_path = download_media(
            job_id,
            str(request.url),
            request.download_type,
            request.quality,
        )

        update_job(
            job_id,
            status="completed",
            progress=100,
            speed=None,
            eta=None,
            file_path=file_path,
        )

    except Exception as exc:
        update_job(
            job_id,
            status="failed",
            error=str(exc),
            speed=None,
            eta=None,
        )

        # Clean up any partial files left behind by the failed download,
        # since no /file request will ever arrive to trigger cleanup.
        delete_directory(TEMP_DIR / job_id)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)