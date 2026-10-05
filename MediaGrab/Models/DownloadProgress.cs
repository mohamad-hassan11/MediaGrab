namespace MediaGrab.Models;

public class DownloadProgress
{
    public double Percentage { get; init; }

    public string Status { get; init; } = string.Empty;

    public string? Speed { get; init; }

    public string? Eta { get; init; }
}