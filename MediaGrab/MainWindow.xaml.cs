using MediaGrab.Models;
using MediaGrab.Services;
using Microsoft.Win32;
using System.Diagnostics;
using System.IO;
using System.Windows;

namespace MediaGrab;

public partial class MainWindow : Window
{
    private readonly DownloadService _downloadService;

    public MainWindow()
    {
        InitializeComponent();

        _downloadService = new DownloadService();

        OutputFolderTextBox.Text = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),"Downloads");
    }

    private void BrowseButton_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new OpenFolderDialog
        {
            Title = "Select download folder",
            InitialDirectory = OutputFolderTextBox.Text
        };

        if (dialog.ShowDialog() == true)
        {
            OutputFolderTextBox.Text = dialog.FolderName;
        }
    }

    private async void DownloadButton_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            DownloadButton.IsEnabled = false;
            BrowseButton.IsEnabled = false;
            UrlTextBox.IsEnabled = false;

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

            await _downloadService.DownloadMp3Async(UrlTextBox.Text, OutputFolderTextBox.Text, progress);

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
            BrowseButton.IsEnabled = true;
            UrlTextBox.IsEnabled = true;
        }
    }


    private void OpenFolderButton_Click(object sender, RoutedEventArgs e)
    {
        var folder = OutputFolderTextBox.Text;

        if (!Directory.Exists(folder))
            return;

        Process.Start(new ProcessStartInfo
        {
            FileName = folder,
            UseShellExecute = true
        });
    }
}