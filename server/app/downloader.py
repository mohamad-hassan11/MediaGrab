from pathlib import Path
from uuid import uuid4

import yt_dlp

BASE_DIR = Path(__file__).resolve().parent.parent

FFMPEG_PATH = BASE_DIR / "tools"

TEMP_DIR = BASE_DIR / "temp"

TEMP_DIR.mkdir(exist_ok=True)


def download_media(
    url: str,
    download_type: str,
    quality: str
) -> Path:

    job_id = uuid4().hex

    job_directory = TEMP_DIR / job_id
    job_directory.mkdir(parents=True, exist_ok=True)

    output_template = str(
        job_directory / "%(title)s.%(ext)s"
    )
    options = {
        "outtmpl": output_template,
        "ffmpeg_location": str(FFMPEG_PATH),
        "noplaylist": True,
        "quiet": False,
    }

    if download_type == "audio":
        configure_audio(
            options,
            quality
        )

    elif download_type == "video":
        configure_video(
            options,
            quality
        )

    else:
        raise ValueError(
            f"Unsupported download type: {download_type}"
        )

    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([url])

    media_extensions = {
        ".mp3",
        ".mp4",
        ".mkv",
        ".webm",
        ".m4a"
    }

    files = [
        file
        for file in job_directory.iterdir()
        if file.is_file()
        and file.suffix.lower() in media_extensions
    ]

    if not files:
        raise RuntimeError(
            "The media file could not be created."
        )

    return files[0]



def configure_video(
    options: dict,
    quality: str
) -> None:

    if quality == "best":
        format_selector = "bv*+ba/b"
    else:
        format_selector = (
            f"bv*[height<={quality}]"
            f"+ba/"
            f"b[height<={quality}]"
        )

    options.update({
        "format": format_selector,
        "merge_output_format": "mp4",

        "postprocessors": [
            {
                "key": "FFmpegMetadata",
            }
        ],
    })

def configure_audio(
    options: dict,
    quality: str
) -> None:

    quality_map = {
        "best": "0",
        "high": "2",
        "medium": "5",
    }

    audio_quality = quality_map.get(
        quality,
        "0"
    )

    options.update({
        "format": "bestaudio/best",

        "writethumbnail": True,

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": audio_quality,
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
            # Force the thumbnail to JPEG before embedding. Without this,
            # webp/png thumbnails are embedded as PNG, which many players
            # (Explorer, WMP, car stereos, phones) fail to render as cover art.
            {
                "key": "FFmpegThumbnailsConvertor",
                "format": "jpg",
            },
            {
                "key": "EmbedThumbnail",
                "already_have_thumbnail": False,
            },
        ],
    })