from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
    
from .downloader import download_media
from .models import DownloadRequest
import uvicorn


app = FastAPI(
    title="MediaGrab API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
    expose_headers=["Content-Disposition"],
)





@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/api/download")
def download(
    request: DownloadRequest,
    background_tasks: BackgroundTasks
):
    try:
        file_path = download_media(
            str(request.url),
            request.download_type,
            request.quality
        )

        background_tasks.add_task(
            delete_directory,
            file_path.parent
        )

        return FileResponse(
            path=file_path,
            filename=file_path.name,
            media_type="application/octet-stream"
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


import shutil

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




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)