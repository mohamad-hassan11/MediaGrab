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

    private async void DownloadButton_Click( object sender, RoutedEventArgs e)
    {
        try
        {
            DownloadButton.IsEnabled = false;

            await _downloadService.DownloadMp3Async(
                UrlTextBox.Text);

            MessageBox.Show(
                "Download completed!",
                "MediaGrab",
                MessageBoxButton.OK,
                MessageBoxImage.Information);
        }
        catch (Exception ex)
        {
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