using System;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;

using Cvte.EasiNote;
using Cvte.Paint.Features.Elements;
using Cvte.Paint.Features.Elements.Texts;
using Cvte.Windows.Input;

using dotnetCampus.EasiPlugins;

using Microsoft.Win32;

namespace MrePlugin;

/// <summary>
/// 希沃白板顶部工具栏"MRE导入"按钮。
/// 用户点击后选择 lesson.json，在当前课件后创建页面并插入元素。
/// </summary>
public class MreImportMenuItem : HeadToolBarItem
{
    public MreImportMenuItem()
    {
        Key = "MrePlugin.ImportMenuItem";
        Type = UIItemTypes.Subject;

        // 排序位置（越小越靠前）
        SortHint = 500;

        // 图标（使用内置几何图形占位）
        ImageSourceKey = Key;
        ImageWidth = 20;
        ImageHeight = 20;

        SetValue(TextProperty, "MRE导入");

        // 仅在备课模式下可用（Shell 端非授课模式）
        Predicate = _ => !EN.CommandOptions.IsCloud;

        Command = new DelegateCommand(OnImportClicked);

        // 注册图标资源
        ResourceHelper.TryAddResource(ImageSourceKey, CreateIconGeometry());
    }

    /// <summary>
    /// 用户点击"MRE导入"按钮时触发。
    /// 1. 弹出文件选择对话框，让用户选择 lesson.json
    /// 2. 解析 JSON
    /// 3. 调用 MreProcessor 创建页面和元素
    /// </summary>
    private async void OnImportClicked()
    {
        var dialog = new OpenFileDialog
        {
            Title = "选择 MRE lesson.json",
            Filter = "JSON 文件|*.json|所有文件|*.*",
            DefaultExt = ".json",
        };

        if (dialog.ShowDialog() != true)
        {
            return; // 用户取消
        }

        var filePath = dialog.FileName;

        // 上报埋点
        SafeEN.Collection.ReportEvent(EventId.MreImportClicked, filePath);

        // 带 Loading 框执行耗时操作
        await EN.Notification.DoWithLoadingAsync(async () =>
        {
            try
            {
                var result = await MreProcessor.ProcessLessonJsonAsync(filePath);
                if (result.Success)
                {
                    MessageBox.Show(
                        $"成功导入 {result.SlideCount} 个页面，共 {result.ElementCount} 个元素。",
                        "MRE 导入完成",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information);
                }
                else
                {
                    MessageBox.Show(
                        $"导入失败：{result.ErrorMessage}",
                        "MRE 导入失败",
                        MessageBoxButton.OK,
                        MessageBoxImage.Error);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(
                    $"发生异常：{ex.Message}",
                    "MRE 导入异常",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error);
            }
        }, "正在导入 MRE 课件...", new CancellationTokenSource());
    }

    /// <summary>
    /// 创建工具栏图标几何图形（简约 M 字母图形）。
    /// </summary>
    private static DrawingImage CreateIconGeometry()
    {
        return new DrawingImage
        {
            Drawing = new GeometryDrawing(
                brush: System.Windows.Media.Brushes.Black,
                pen: null,
                geometry: Geometry.Parse(
                    // 简约 "M" 字母几何路径
                    "M4,20 L4,6 L10,16 L16,6 L16,20 L14,20 L14,10 L10,18 L6,10 L6,20 Z"))
        };
    }
}

/// <summary>
/// 资源辅助类：安全地向 Application 全局资源添加资源。
/// </summary>
public static class ResourceHelper
{
    public static bool TryAddResource(string key, object resource)
    {
        if (Application.Current.Resources[key] is null)
        {
            Application.Current.Resources[key] = resource;
            return true;
        }
        return false;
    }
}
