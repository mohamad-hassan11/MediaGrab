using MediaGrab.Models;
using MediaGrab.Services;
using Microsoft.Win32;
using System.Diagnostics;
using System.IO;
using System.Windows;
using System.Windows.Controls;

namespace MediaGrab;

public partial class MainWindow : Window
{
    private readonly DownloadService _downloadService;

    public MainWindow()
    {
        InitializeComponent();

        _downloadService = new DownloadService();

        OutputFolderTextBox.Text = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Downloads");
        FormatComboBox.SelectedIndex = 0;

        LoadQualityOptions(); 
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

    private void LoadQualityOptions()
    {
        QualityComboBox.Items.Clear();

        var selectedFormat =
            (FormatComboBox.SelectedItem as ComboBoxItem)?.Tag?.ToString();

        if (selectedFormat == "video")
        {
            QualityComboBox.Items.Add(
                new ComboBoxItem
                {
                    Content = "Best available",
                    Tag = "best"
                });

            QualityComboBox.Items.Add(
                new ComboBoxItem
                {
                    Content = "2160p (4K)",
                    Tag = "2160"
                });

            QualityComboBox.Items.Add(
                new ComboBoxItem
                {
                    Content = "1440p",
                    Tag = "1440"
                });

            QualityComboBox.Items.Add(
                new ComboBoxItem
                {
                    Content = "1080p",
                    Tag = "1080"
                });

            QualityComboBox.Items.Add(
                new ComboBoxItem
                {
                    Content = "720p",
                    Tag = "720"
                });

            QualityComboBox.Items.Add(
                new ComboBoxItem
                {
                    Content = "480p",
                    Tag = "480"
                });

            QualityComboBox.Items.Add(
                new ComboBoxItem
                {
                    Content = "360p",
                    Tag = "360"
                });
        }
        else
        {
            QualityComboBox.Items.Add(
                new ComboBoxItem
                {
                    Content = "Best quality",
                    Tag = "0"
                });

            QualityComboBox.Items.Add(
                new ComboBoxItem
                {
                    Content = "High quality",
                    Tag = "2"
                });

            QualityComboBox.Items.Add(
                new ComboBoxItem
                {
                    Content = "Medium quality",
                    Tag = "5"
                });
        }

        QualityComboBox.SelectedIndex = 0;
    }
    private void FormatComboBox_SelectionChanged(
        object sender,
        SelectionChangedEventArgs e)
    {
        if (QualityComboBox == null)
            return;

        LoadQualityOptions();
    }

}