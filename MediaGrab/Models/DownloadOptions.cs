namespace MediaGrab.Models;

public class DownloadOptions
{
    public required string Url { get; init; }

    public required string OutputDirectory { get; init; }

    public DownloadFormat Format { get; init; }

    public string Quality { get; init; } = "best";
}