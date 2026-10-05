using System.Diagnostics;
using System.IO;
using MediaGrab.Models;

namespace MediaGrab.Services;

public class DownloadService
{
    private readonly string _ytDlpPath;
    private readonly string _ffmpegPath;

    public DownloadService()
    {
        var toolsDirectory = Path.Combine(
            AppContext.BaseDirectory,
            "Tools");

        _ytDlpPath = Path.Combine(
            toolsDirectory,
            "yt-dlp.exe");

        _ffmpegPath = toolsDirectory;
    }


    public async Task DownloadMp3Async(
        string url,
        IProgress<DownloadProgress>? progress = null)
    {
        if (string.IsNullOrWhiteSpace(url))
            throw new ArgumentException("URL cannot be empty.");

        if (!File.Exists(_ytDlpPath))
            throw new FileNotFoundException("yt-dlp.exe could not be found.", _ytDlpPath);

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

        startInfo.ArgumentList.Add("--newline");

        // set strickt progress template
        startInfo.ArgumentList.Add("--progress-template");
        startInfo.ArgumentList.Add("download:PROGRESS|%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s");

        // output format
        startInfo.ArgumentList.Add("-o");
        startInfo.ArgumentList.Add(outputTemplate);

        startInfo.ArgumentList.Add(url);


        // Start process and execute
        using var process = new Process
        {
            StartInfo = startInfo
        };

        process.OutputDataReceived += (_, e) =>
        {
            if (string.IsNullOrWhiteSpace(e.Data))
                return;

            Debug.WriteLine(e.Data);

            if (!e.Data.StartsWith("PROGRESS|"))
                return;

            var parts = e.Data.Split('|');

            if (parts.Length < 4)
                return;

            var percentageText = parts[1]
                .Replace("%", string.Empty)
                .Trim();

            if (!double.TryParse(
                    percentageText,
                    System.Globalization.NumberStyles.Any,
                    System.Globalization.CultureInfo.InvariantCulture,
                    out var percentage))
            {
                return;
            }

            progress?.Report(new DownloadProgress
            {
                Percentage = percentage,
                Status = "Downloading",
                Speed = parts[2].Trim(),
                Eta = parts[3].Trim()
            });
        };


        process.ErrorDataReceived += (_, e) =>
        {
            if (!string.IsNullOrWhiteSpace(e.Data))
            {
                Debug.WriteLine(e.Data);
            }
        };


        process.Start();

        process.BeginOutputReadLine();
        process.BeginErrorReadLine();

        await process.WaitForExitAsync();

        if (process.ExitCode != 0)
        {
            throw new Exception(
                $"yt-dlp failed with exit code {process.ExitCode}.");
        }
    }

}