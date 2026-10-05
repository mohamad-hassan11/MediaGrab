using MediaGrab.Models;
using MediaGrab.Services;
using System.Windows;

namespace MediaGrab;

public partial class MainWindow : Window
{
    private readonly DownloadService _downloadService;

    public MainWindow()
    {
        InitializeComponent();

        _downloadService = new DownloadService();
    }

    private async void DownloadButton_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            DownloadButton.IsEnabled = false;

            DownloadProgressBar.Value = 0;
            StatusTextBlock.Text = "Starting...";
            ProgressDetailsTextBlock.Text = string.Empty;

            var progress = new Progress<DownloadProgress>(p =>
            {
                DownloadProgressBar.Value = p.Percentage;

                if (p.Status == "Downloading")
                {
                    StatusTextBlock.Text =
                        $"Downloading - {p.Percentage:0.0}%";

                    ProgressDetailsTextBlock.Text =
                        $"{p.Speed} • {p.Eta} remaining";
                }
                else
                {
                    StatusTextBlock.Text = p.Status;
                    ProgressDetailsTextBlock.Text = string.Empty;
                }
            });

            await _downloadService.DownloadMp3Async(UrlTextBox.Text, progress);

            DownloadProgressBar.Value = 100;
            StatusTextBlock.Text = "Completed";
            ProgressDetailsTextBlock.Text = string.Empty;

            MessageBox.Show(
                "Download completed!",
                "MediaGrab",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
        }
        catch (Exception ex)
        {
            StatusTextBlock.Text = "Failed";

            MessageBox.Show(
                ex.Message,
                "Download failed",
                MessageBoxButton.OK,
                MessageBoxImage.Error);
        }
        finally
        {
            DownloadButton.IsEnabled = true;
        }
    }
}