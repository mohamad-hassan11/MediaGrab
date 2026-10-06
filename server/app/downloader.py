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

# yt-dlp needs an external JS runtime (plus the yt-dlp-ejs scripts, see
# requirements.txt) to solve YouTube's JS challenges. Deno is yt-dlp's
# default runtime, but we don't install it; Node is already available in
# the container, so enable it explicitly. Without this, "JS runtimes:
# none" leaves YouTube unable to verify the client, which contributes to
# bot/sign-in check failures. https://github.com/yt-dlp/yt-dlp/wiki/EJS
JS_RUNTIMES = {"node": {}} if shutil.which("node") else None

# YouTube may reject requests from datacenter IPs (e.g. cloud hosting
# providers like Render) with "Sign in to confirm you're not a bot".
# The documented fix is to pass cookies from a logged-in session. See:
# https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp
#
# - YTDLP_COOKIES_FILE: path to a Netscape-format cookies.txt file.
#   Defaults to "<server>/cookies.txt" if present.
# - YTDLP_COOKIES_FROM_BROWSER: a browser name (e.g. "chrome", "firefox")
#   to read cookies directly from, for local/dev use where a browser is
#   installed on the same machine as the server.
COOKIES_FILE = os.environ.get(
    "YTDLP_COOKIES_FILE",
    str(BASE_DIR / "cookies.txt"),
)

COOKIES_FROM_BROWSER = os.environ.get(
    "YTDLP_COOKIES_FROM_BROWSER"
)


RENDER_COOKIE_FILE = Path(
    "/etc/secrets/cookies.txt"
)


def apply_cookie_options(options: dict) -> None:
    if COOKIES_FROM_BROWSER:
        options["cookiesfrombrowser"] = (COOKIES_FROM_BROWSER,)
    elif Path(COOKIES_FILE).is_file():
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

    cookie_file = get_cookie_file()

    if cookie_file:
        options["cookiefile"] = cookie_file

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

    if JS_RUNTIMES:
        options["js_runtimes"] = JS_RUNTIMES

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


def get_cookie_file() -> str | None:
    configured_path = os.getenv(
        "YTDLP_COOKIE_FILE"
    )

    if configured_path:
        path = Path(
            configured_path
        )

        if path.exists():
            return str(path)

    if RENDER_COOKIE_FILE.exists():
        return str(
            RENDER_COOKIE_FILE
        )

    if COOKIES_FILE.exists():
        return str(
            COOKIES_FILE
        )

    return None