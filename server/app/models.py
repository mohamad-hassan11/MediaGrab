from typing import Literal

from pydantic import BaseModel, HttpUrl


class DownloadRequest(BaseModel):
    url: HttpUrl
    download_type: Literal["audio", "video"]
    quality: str = "best"


class CreateJobResponse(BaseModel):
    job_id: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal[
        "queued",
        "downloading",
        "processing",
        "completed",
        "failed",
    ]

    progress: float = 0
    speed: str | None = None
    eta: str | None = None
    error: str | None = None