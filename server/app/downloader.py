from pathlib import Path
from .jobs import update_job
import os
import yt_dlp
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOCAL_FFMPEG = BASE_DIR / "tools"

if (
    (LOCAL_FFMPEG / "ffmpeg.exe").exists()
):
    FFMPEG_PATH = str(LOCAL_FFMPEG)
else:
    FFMPEG_PATH = shutil.which(
        "ffmpeg"
    )
TEMP_DIR = BASE_DIR / "temp"

TEMP_DIR.mkdir(exist_ok=True)

if not FFMPEG_PATH:
    raise RuntimeError(
        "FFmpeg could not be found."
    )

# YouTube may reject requests from datacenter IPs (e.g. cloud hosting
# providers like Render) with "Sign in to confirm you're not a bot".
# Primary fix: the bgutil-ytdlp-pot-provider plugin, which fetches a
# proof-of-origin token from a local HTTP server (started alongside this
# app, see entrypoint.sh) without requiring any logged-in cookies.
# https://github.com/Brainicism/bgutil-ytdlp-pot-provider
# https://github.com/yt-dlp/yt-dlp/wiki/PO-Token-Guide
#
# - BGUTIL_POT_BASE_URL: override the PO Token provider server's URL.
#   Only needed if it isn't reachable at the plugin's default of
#   http://127.0.0.1:4416 (e.g. a different port or a separate host).
# - YTDLP_PLAYER_CLIENTS: comma-separated list of YouTube player clients
#   to try (e.g. "mweb,tv,web_safari"). Some clients need a PO token less
#   often than others; use this if tokens are generated but the "Sign in
#   to confirm you're not a bot" error still occurs for the default client.
POT_BASE_URL = os.environ.get("BGUTIL_POT_BASE_URL")

PLAYER_CLIENTS = os.environ.get("YTDLP_PLAYER_CLIENTS")


def apply_pot_options(options: dict) -> None:
    extractor_args = options.setdefault("extractor_args", {})

    if POT_BASE_URL:
        extractor_args.setdefault("youtubepot-bgutilhttp", {})[
            "base_url"
        ] = [POT_BASE_URL]

    if PLAYER_CLIENTS:
        clients = [
            client.strip()
            for client in PLAYER_CLIENTS.split(",")
            if client.strip()
        ]

        if clients:
            extractor_args.setdefault("youtube", {})[
                "player_client"
            ] = clients


# Optional, supplementary fallback: cookies from a logged-in session.
# Not used unless YTDLP_COOKIES_FILE/YTDLP_COOKIES_FROM_BROWSER is set,
# since a PO token alone does not bypass IP-based bot checks in all
# cases. See https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp
COOKIES_FILE = os.environ.get("YTDLP_COOKIES_FILE")

COOKIES_FROM_BROWSER = os.environ.get(
    "YTDLP_COOKIES_FROM_BROWSER"
)


def apply_cookie_options(options: dict) -> None:
    if COOKIES_FROM_BROWSER:
        options["cookiesfrombrowser"] = (COOKIES_FROM_BROWSER,)
    elif COOKIES_FILE and Path(COOKIES_FILE).is_file():
        options["cookiefile"] = COOKIES_FILE


def download_media(
    job_id: str,
    url: str,
    download_type: str,
    quality: str
) -> Path:



    job_directory = TEMP_DIR / job_id
    job_directory.mkdir(parents=True, exist_ok=True)

    output_template = str(
        job_directory / "%(title)s.%(ext)s"
    )

    options = {
    "outtmpl": output_template,

    "ffmpeg_location":
        FFMPEG_PATH,

    "noplaylist": True,

    "quiet": False,

    "progress_hooks": [
        create_progress_hook(
            job_id
        )
    ],
}

    apply_pot_options(options)
    apply_cookie_options(options)

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



def create_progress_hook(
    job_id: str
):
    def progress_hook(data: dict):
        status = data.get("status")

        if status == "downloading":
            downloaded_bytes = (
                data.get("downloaded_bytes")
                or 0
            )

            total_bytes = (
                data.get("total_bytes")
                or data.get(
                    "total_bytes_estimate"
                )
                or 0
            )

            percentage = 0.0

            if total_bytes > 0:
                percentage = (
                    downloaded_bytes
                    / total_bytes
                    * 100
                )

            speed_value = data.get("speed")

            if speed_value:
                speed = format_speed(
                    speed_value
                )
            else:
                speed = None

            eta_value = data.get("eta")

            if eta_value is not None:
                eta = format_eta(
                    int(eta_value)
                )
            else:
                eta = None

            update_job(
                job_id,
                status="downloading",
                progress=percentage,
                speed=speed,
                eta=eta,
            )

        elif status == "finished":
            update_job(
                job_id,
                status="processing",
                progress=100,
                speed=None,
                eta=None,
            )

    return progress_hook



def format_speed(
    bytes_per_second: float
) -> str:

    megabytes = (
        bytes_per_second
        / 1024
        / 1024
    )

    return f"{megabytes:.1f} MB/s"



def format_eta(
    seconds: int
) -> str:

    minutes, seconds = divmod(
        seconds,
        60
    )

    hours, minutes = divmod(
        minutes,
        60
    )

    if hours > 0:
        return (
            f"{hours:02d}:"
            f"{minutes:02d}:"
            f"{seconds:02d}"
        )

    return (
        f"{minutes:02d}:"
        f"{seconds:02d}"
    )