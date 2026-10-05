using System.Diagnostics;
using System.IO;

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

    public async Task DownloadMp3Async(string url)
    {
        if (string.IsNullOrWhiteSpace(url))
        {
            throw new ArgumentException("URL cannot be empty.");
        }

        if (!File.Exists(_ytDlpPath))
        {
            throw new FileNotFoundException(
                "yt-dlp.exe could not be found.",
                _ytDlpPath);
        }

        var downloadsDirectory = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
            "Downloads");

        var outputTemplate = Path.Combine(
            downloadsDirectory,
            "%(title)s.%(ext)s");

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
        startInfo.ArgumentList.Add("0");

        // metadata (title, cover image, thumbnail, Artist ...) 
        startInfo.ArgumentList.Add("--embed-metadata");
        startInfo.ArgumentList.Add("--embed-thumbnail");

        // target download dir
        startInfo.ArgumentList.Add("--ffmpeg-location");
        startInfo.ArgumentList.Add(_ffmpegPath);

        // output format
        startInfo.ArgumentList.Add("-o");
        startInfo.ArgumentList.Add(outputTemplate);

        startInfo.ArgumentList.Add(url);

        using var process = new Process
        {
            StartInfo = startInfo
        };

        process.OutputDataReceived += (_, e) =>
        {
            if (!string.IsNullOrWhiteSpace(e.Data))
            {
                Debug.WriteLine(e.Data);
            }
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