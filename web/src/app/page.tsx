"use client";

import { useState } from "react";

type DownloadType = "audio" | "video";

export default function Home() {
  const [url, setUrl] = useState("");
  const [downloadType, setDownloadType] =
    useState<DownloadType>("audio");

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

  const qualities =
    downloadType === "audio"
      ? audioQualities
      : videoQualities;

  function changeDownloadType(type: DownloadType) {
    setDownloadType(type);
    setQuality("best");
  }

  function handleDownload() {
    console.log({
      url,
      downloadType,
      quality,
    });
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
                    changeDownloadType(
                      event.target.value as DownloadType
                    )
                  }
                  className="h-12 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                >
                  <option value="audio">
                    Audio (MP3)
                  </option>

                  <option value="video">
                    Video (MP4)
                  </option>
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
                  onChange={(event) =>
                    setQuality(event.target.value)
                  }
                  className="h-12 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                >
                  {qualities.map((item) => (
                    <option
                      key={item.value}
                      value={item.value}
                    >
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
              className="h-12 w-full rounded-lg bg-blue-600 text-sm font-semibold text-white transition hover:bg-blue-700 active:bg-blue-800"
            >
              Download
            </button>

            {/* Status */}

            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="text-slate-700">
                  Ready
                </span>

                <span className="text-slate-500">
                  0%
                </span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  className="h-full rounded-full bg-blue-600 transition-all"
                  style={{ width: "0%" }}
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