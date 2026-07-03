using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Threading;

using Cvte.Composition;
using Cvte.EasiNote;
using Cvte.Windows.Localization;

using dotnetCampus.EasiPlugins;

namespace MrePlugin;

internal class Program : EasiPlugin
{
    private static readonly string LogPath =
        Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "MrePlugin.log");

    protected override Task OnRunningAsync()
    {
        Log("OnRunningAsync entered. IsCloud=" + EN.CommandOptions.IsCloud);

        if (EN.CommandOptions.IsCloud)
        {
            Log("Cloud mode - skipping");
            return Task.CompletedTask;
        }

        Log("Shell mode - waiting for App.Ready. IsReady=" + EN.App.IsReady);

        if (EN.App.IsReady)
        {
            Log("App already ready");
            RunSafe();
        }
        else
        {
            Log("Subscribing to App.Ready");
            EN.App.Ready += App_Ready;
        }

        return Task.CompletedTask;
    }

    private void App_Ready(object? sender, EventArgs e)
    {
        Log("App_Ready fired");
        EN.App.Ready -= App_Ready;
        RunSafe();
    }

    private async void RunSafe()
    {
        try
        {
            Log("RunSafe started, delaying 3s...");
            await Task.Delay(TimeSpan.FromSeconds(3));
            Log("Delay done, dispatching ExportUIItems");

            Application.Current.Dispatcher.Invoke(() =>
            {
                try
                {
                    ExportUIItems();
                    Log("ExportUIItems completed successfully");
                }
                catch (Exception ex)
                {
                    Log($"ExportUIItems failed: {ex}");
                }
            });
        }
        catch (Exception ex)
        {
            Log($"RunSafe failed: {ex}");
        }
    }

    private void ExportUIItems()
    {
        Log($"Getting IUIItemManager. Container ready? {Container.Current != null}");

        var manager = Container.Current.Get<IUIItemManager>();
        Log($"Got manager: {manager != null}");

        manager.Append(
            c => new MreImportMenuItem(),
            new UIItemAttribute(UIItemPurposes.HeadToolBar));

        manager.Append(
            c => new MreImportBoardMenuItem(),
            new UIItemAttribute(UIItemPurposes.BoardEditMenu));

        Log("Append done. Adding languages...");

        Application.Current.Dispatcher.InvokeAsync(() =>
        {
            Lang.Sources.Add(new DictionaryLanguageSource
            {
                [new CultureInfo("zh-CHS")] = new Dictionary<string, string>
                {
                    { "Lang.HeadToolBar.MreImport", "MRE导入" },
                    { "Lang.BoardEditContextMenu.MreImportBoard", "MRE导入" },
                },
            });
        }, DispatcherPriority.Send);

        Log("ExportUIItems finished");
    }

    private static void Log(string msg)
    {
        try
        {
            File.AppendAllText(LogPath,
                $"{DateTime.Now:HH:mm:ss.fff} [{System.Threading.Thread.CurrentThread.ManagedThreadId}] {msg}\n");
        }
        catch { }
    }
}
