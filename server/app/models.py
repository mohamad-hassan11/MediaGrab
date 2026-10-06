from typing import Literal

from pydantic import BaseModel, HttpUrl

class DownloadRequest(BaseModel):
    url: HttpUrl
    download_type: Literal["audio", "video"]
    quality: str = "best"