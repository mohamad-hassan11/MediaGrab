using MediaGrab.Models;
using System.Diagnostics;
using System.IO;
using System.Text;

namespace MediaGrab.Services;

public class DownloadService
{
    private readonly string _ytDlpPath;
    private readonly string _ffmpegPath;
    private readonly string _denoPath;

    public DownloadService()
    {
        var toolsDirectory = Path.Combine(
            AppContext.BaseDirectory,
            "Tools");

        _ytDlpPath = Path.Combine(
            toolsDirectory,
            "yt-dlp.exe");

        _denoPath = Path.Combine(
            toolsDirectory,
            "deno.exe");

        _ffmpegPath = toolsDirectory;

    }


    public async Task DownloadMp3Async(
        string url,
        IProgress<DownloadProgress>? progress = null)
    {
        if (string.IsNullOrWhiteSpace(url))
            throw new ArgumentException("URL cannot be empty.");
        
        if (!Uri.TryCreate(url, UriKind.Absolute, out var uri) || (uri.Scheme != Uri.UriSchemeHttp && uri.Scheme != Uri.UriSchemeHttps))
            throw new ArgumentException("Please enter a valid URL.");

        if (!File.Exists(_ytDlpPath))
            throw new FileNotFoundException("yt-dlp.exe could not be found.", _ytDlpPath);

        var ffmpegExecutable = Path.Combine(_ffmpegPath, "ffmpeg.exe");

        if (!File.Exists(ffmpegExecutable))
            throw new FileNotFoundException("ffmpeg.exe could not be found.", ffmpegExecutable);

        if (!File.Exists(_denoPath))
        {
            throw new FileNotFoundException(
                "deno.exe could not be found.",
                _denoPath);
        }


        var downloadsDirectory = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Downloads");
        var outputTemplate = Path.Combine( downloadsDirectory, "%(title)s.%(ext)s");

        var startInfo = new ProcessStartInfo
        {
            FileName = _ytDlpPath,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true
        };

        // fromat 
        startInfo.ArgumentList.Add("-x");
        startInfo.ArgumentList.Add("--audio-format");
        startInfo.ArgumentList.Add("mp3");

        // quality
        startInfo.ArgumentList.Add("--audio-quality");
        startInfo.ArgumentList.Add("0"); // best quality

        // metadata (title, cover image, thumbnail, Artist ...) 
        startInfo.ArgumentList.Add("--embed-metadata");
        startInfo.ArgumentList.Add("--embed-thumbnail");

        // target download dir
        startInfo.ArgumentList.Add("--ffmpeg-location");
        startInfo.ArgumentList.Add(_ffmpegPath);


        // add js runttime
        startInfo.ArgumentList.Add("--js-runtimes");
        startInfo.ArgumentList.Add($"deno:{_denoPath}");

        startInfo.ArgumentList.Add("--newline");

        // set strickt progress template
        startInfo.ArgumentList.Add("--progress-template");
        startInfo.ArgumentList.Add("download:PROGRESS|%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s");

        // output format
        startInfo.ArgumentList.Add("-o");
        startInfo.ArgumentList.Add(outputTemplate);

        startInfo.ArgumentList.Add(url);


        // initilize, track and execute process 
        var errorOutput = new StringBuilder();
        using var process = new Process
        {
            StartInfo = startInfo
        };


        process.OutputDataReceived += (_, e) =>
        {
            if (string.IsNullOrWhiteSpace(e.Data))
                return;

            var line = e.Data;

            Debug.WriteLine(line);

            // Download progress
            if (line.StartsWith("PROGRESS|"))
            {
                var parts = line.Split('|');

                if (parts.Length < 4)
                    return;

                var percentageText = parts[1]
                    .Replace("%", string.Empty)
                    .Trim();

                if (double.TryParse(
                        percentageText,
                        System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture,
                        out var percentage))
                {
                    progress?.Report(new DownloadProgress
                    {
                        Percentage = percentage,
                        Status = "Downloading",
                        Speed = parts[2].Trim(),
                        Eta = parts[3].Trim()
                    });
                }

                return;
            }

            // yt-dlp is retrieving information
            if (line.Contains("[youtube]"))
            {
                progress?.Report(new DownloadProgress
                {
                    Percentage = 0,
                    Status = "Fetching media information..."
                });

                return;
            }

            // FFmpeg/audio extraction
            if (line.Contains("[ExtractAudio]"))
            {
                progress?.Report(new DownloadProgress
                {
                    Percentage = 100,
                    Status = "Converting to MP3..."
                });

                return;
            }

            // Metadata
            if (line.Contains("[Metadata]"))
            {
                progress?.Report(new DownloadProgress
                {
                    Percentage = 100,
                    Status = "Embedding metadata..."
                });

                return;
            }

            // Thumbnail processing
            if (line.Contains("[EmbedThumbnail]"))
            {
                progress?.Report(new DownloadProgress
                {
                    Percentage = 100,
                    Status = "Embedding thumbnail..."
                });
            }
        };

        process.ErrorDataReceived += (_, e) =>
        {
            if (string.IsNullOrWhiteSpace(e.Data))
                return;

            Debug.WriteLine(e.Data);
            errorOutput.AppendLine(e.Data);
        };


        process.Start();

        process.BeginOutputReadLine();
        process.BeginErrorReadLine();

        await process.WaitForExitAsync();

        if (process.ExitCode != 0)
        {
            var errorMessage = errorOutput.ToString().Trim();

            if (string.IsNullOrWhiteSpace(errorMessage))
            {
                errorMessage =
                    $"The download failed with exit code {process.ExitCode}.";
            }

            throw new InvalidOperationException(errorMessage);
        }
    }

}