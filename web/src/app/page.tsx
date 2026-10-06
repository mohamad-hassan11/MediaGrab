"use client";

import { useState } from "react";

type DownloadType = "audio" | "video";

export default function Home() {
  const [url, setUrl] = useState("");
  const [downloadType, setDownloadType] = useState<DownloadType>("audio");

  const [isDownloading, setIsDownloading] = useState(false);

  const [status, setStatus] = useState("Ready");

  const [error, setError] = useState<string | null>(null);

  const [quality, setQuality] = useState("best");

  const audioQualities = [
    { value: "best", label: "Best quality" },
    { value: "high", label: "High quality" },
    { value: "medium", label: "Medium quality" },
  ];

  const videoQualities = [
    { value: "best", label: "Best available" },
    { value: "2160", label: "2160p (4K)" },
    { value: "1440", label: "1440p" },
    { value: "1080", label: "1080p" },
    { value: "720", label: "720p" },
    { value: "480", label: "480p" },
    { value: "360", label: "360p" },
  ];

  const qualities = downloadType === "audio" ? audioQualities : videoQualities;

  function getFilenameFromResponse(
    response: Response,
    fallback: string,
  ): string {
    const disposition = response.headers.get("Content-Disposition");

    if (!disposition) {
      return fallback;
    }

    const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i);

    if (utf8Match?.[1]) {
      return decodeURIComponent(utf8Match[1]);
    }

    const normalMatch = disposition.match(/filename="?([^"]+)"?/);

    return normalMatch?.[1] ?? fallback;
  }

  function changeDownloadType(type: DownloadType) {
    setDownloadType(type);
    setQuality("best");
  }

  async function handleDownload() {
    if (!url.trim()) {
      setError("Please enter a media URL.");
      return;
    }

    try {
      setError(null);
      setIsDownloading(true);
      setStatus("Preparing download...");

      const response = await fetch("http://localhost:8000/api/download", {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          url,
          download_type: downloadType,
          quality,
        }),
      });

      if (!response.ok) {
        const data = await response.json();

        throw new Error(data.detail || "The download failed.");
      }

      setStatus("Receiving file...");

      const filename = getFilenameFromResponse(
        response,
        downloadType === "audio" ? "download.mp3" : "download.mp4",
      );

      const blob = await response.blob();

      const objectUrl = window.URL.createObjectURL(blob);

      const anchor = document.createElement("a");

      anchor.href = objectUrl;
      debugger;
      anchor.download = filename;

      document.body.appendChild(anchor);

      anchor.click();

      anchor.remove();

      window.URL.revokeObjectURL(objectUrl);

      setStatus("Completed");
    } catch (err) {
      setStatus("Failed");

      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setIsDownloading(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-4 py-16">
      <div className="mx-auto max-w-2xl">
        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <header className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
              MediaGrab
            </h1>

            <p className="mt-2 text-sm text-slate-500">
              Download audio and video from supported media links.
            </p>
          </header>

          <div className="space-y-6">
            {/* URL */}

            <div>
              <label
                htmlFor="url"
                className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-700"
              >
                Media URL
              </label>

              <input
                id="url"
                type="url"
                value={url}
                onChange={(event) => setUrl(event.target.value)}
                placeholder="Paste a media URL..."
                className="h-12 w-full rounded-lg border border-slate-300 bg-white px-4 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>

            {/* Options */}

            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="format"
                  className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-700"
                >
                  Download as
                </label>

                <select
                  id="format"
                  value={downloadType}
                  onChange={(event) =>
                    changeDownloadType(event.target.value as DownloadType)
                  }
                  className="h-12 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                >
                  <option value="audio">Audio (MP3)</option>

                  <option value="video">Video (MP4)</option>
                </select>
              </div>

              <div>
                <label
                  htmlFor="quality"
                  className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-700"
                >
                  Quality
                </label>

                <select
                  id="quality"
                  value={quality}
                  onChange={(event) => setQuality(event.target.value)}
                  className="h-12 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                >
                  {qualities.map((item) => (
                    <option key={item.value} value={item.value}>
                      {item.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Download */}

            <button
              type="button"
              onClick={handleDownload}
              disabled={isDownloading}
              className="h-12 w-full rounded-lg bg-blue-600 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isDownloading ? "Downloading..." : "Download"}
            </button>

            {/* Status */}
            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="text-slate-700"> {status}</span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-blue-600 transition-all"
                  style={{ width: isDownloading ? "50%" : "0%" }}
                />
              </div>
            </div>
          </div>
        </div>

        <p className="mt-5 text-center text-xs text-slate-400">
          Only download media you have permission to save.
        </p>
      </div>
    </main>
  );
}
