using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Media;

using Cvte.EasiNote;
using Cvte.Paint.Framework;
using Cvte.Paint.Features.Elements;
using Cvte.Paint.Features.Elements.Texts;
using Cvte.Paint.Features.Elements.Shapes;
using Cvte.Paint.Features.Elements.Images;
using Cvte.Windows.TextEditorPlus.Api;
using Cvte.Windows.TextEditorPlus.Storage;

namespace MrePlugin;

/// <summary>
/// MRE lesson.json 处理结果。
/// </summary>
public readonly struct MreProcessResult
{
    public bool Success { get; init; }
    public int SlideCount { get; init; }
    public int ElementCount { get; init; }
    public string? ErrorMessage { get; init; }

    public static MreProcessResult Ok(int slides, int elements) =>
        new() { Success = true, SlideCount = slides, ElementCount = elements };

    public static MreProcessResult Fail(string msg) =>
        new() { Success = false, ErrorMessage = msg };
}

/// <summary>
/// MRE lesson.json → 希沃白板课件转换处理器。
///
/// 已验证的 EasiNote API（来源：EasiNote5_5.2.4.9801 反射）：
///   - Slide: new Slide() / new Slide(string id)
///   - Slide.Add(Element) / Slide.Add(IEnumerable&lt;Element&gt;)
///   - Board.Insert(Slide) / Board.InsertAt(Slide, int)
///   - TextElement: new TextElement() / new TextElement(bool isEditable)
///   - TextElement.TextEditor.SetRichText(RichTextSaveInfo, bool)
///   - RichTextSaveInfo: Text, Paragraphs, SizeToContent
///   - ShapeElement: new ShapeElement(ShapeType)
///   - ShapeType: 枚举（Rectangle, Ellipse, Line 等）
/// </summary>
public static class MreProcessor
{
    /// <summary>
    /// 处理 lesson.json，在当前课件中创建对应页面和元素。
    /// </summary>
    public static async Task<MreProcessResult> ProcessLessonJsonAsync(string filePath)
    {
        // 1. 读取并解析 JSON
        string jsonContent;
        try { jsonContent = await File.ReadAllTextAsync(filePath); }
        catch (Exception ex) { return MreProcessResult.Fail($"无法读取文件：{ex.Message}"); }

        LessonDocument? lesson;
        try
        {
            lesson = JsonSerializer.Deserialize<LessonDocument>(jsonContent,
                new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
        }
        catch (JsonException ex) { return MreProcessResult.Fail($"JSON 解析失败：{ex.Message}"); }

        if (lesson?.Slides is null || lesson.Slides.Count == 0)
            return MreProcessResult.Fail("lesson.json 中没有 slides 或为空。");

        // 2. 获取希沃备课编辑白板服务和 asset 基础路径
        var editingBoard = EN.EditingBoardApi;
        if (editingBoard is null || !editingBoard.IsLoaded)
            return MreProcessResult.Fail("无法获取备课编辑白板。请先打开或新建一个课件，并进入备课编辑页面。");

        var assetBaseDir = Path.GetDirectoryName(filePath) ?? "";
        var assetsDir = Path.Combine(assetBaseDir, "assets");

        int totalElements = 0;
        for (int i = 0; i < lesson.Slides.Count; i++)
        {
            var slideData = lesson.Slides[i];
            if (slideData.Elements is null) continue;

            try
            {
                Slide slide;
                bool reuseCurrent = false;

                // 第一页：尝试复用当前空白页，避免导入后首页为空
                if (i == 0)
                {
                    try
                    {
                        var current = editingBoard.CurrentSlide;
                        if (current != null)
                        {
                            slide = current;
                            reuseCurrent = true;
                            Log("复用当前首页，避免空白第一页");
                        }
                        else
                        {
                            slide = new Slide(slideData.Id ?? $"mre_{i}");
                        }
                    }
                    catch
                    {
                        slide = new Slide(slideData.Id ?? $"mre_{i}");
                    }
                }
                else
                {
                    slide = new Slide(slideData.Id ?? $"mre_{i}");
                }

                foreach (var elemData in slideData.Elements)
                {
                    try
                    {
                        CreateElement(slide, elemData, assetsDir);
                        totalElements++;
                    }
                    catch (Exception ex)
                    {
                        Log($"元素创建失败: slide={slideData.Id}, id={elemData.Id}, type={elemData.Type}, error={ex}");
                    }
                }

                if (!reuseCurrent)
                    editingBoard.InsertSlide(slide);
            }
            catch (Exception ex)
            {
                return MreProcessResult.Fail($"处理第 {i + 1} 个页面时出错：{ex.Message}");
            }
        }

        return MreProcessResult.Ok(lesson.Slides.Count, totalElements);
    }

    // ═══════════════════════════════════════════════════
    // 元素创建
    // ═══════════════════════════════════════════════════

    private static void CreateElement(Slide slide, ElementData data, string assetsDir)
    {
        switch (data.Type?.ToLowerInvariant())
        {
            case "text":
                CreateTextElement(slide, data);
                break;
            case "image":
            case "formula":
                CreateImageElement(slide, data, assetsDir);
                break;
            case "shape":
                CreateShapeElement(slide, data);
                break;
        }
    }

    /// <summary>
    /// 创建文本框元素。
    /// 已验证 API: TextElement(bool isEditable), TextEditor.SetRichText(RichTextSaveInfo, bool)
    /// </summary>
    private static void CreateTextElement(Slide slide, ElementData data)
    {
        var textElement = new TextElement(isEditable: true);

        double x = data.X.GetValueOrDefault(100);
        double y = data.Y.GetValueOrDefault(50);
        double w = data.Width.GetValueOrDefault(800);
        double h = data.Height.GetValueOrDefault(60);

        textElement.Bounds = new Rect(x, y, w, h);
        textElement.Width = w;
        textElement.Height = h;
        textElement.Background = Brushes.Transparent;
        textElement.BorderThickness = 0;
        textElement.IsEditable = true;

        var editor = textElement.TextEditor;
        editor.Text = data.Text ?? string.Empty;
        editor.Width = w;
        editor.Height = h;
        editor.FontSize = data.FontSize.GetValueOrDefault(20);
        editor.Foreground = ParseBrush(data.Color) ?? Brushes.Black;
        editor.FontWeight = data.Bold == true ? FontWeights.Bold : FontWeights.Normal;
        editor.FontStyle = data.Italic == true ? FontStyles.Italic : FontStyles.Normal;
        if (!string.IsNullOrWhiteSpace(data.FontFamily))
        {
            try { editor.FontName = new FontName(data.FontFamily); }
            catch { /* 字体不可用时忽略 */ }
        }
        editor.TextWrapping = TextWrapping.Wrap;
        editor.IsEditable = true;

        slide.Add(textElement);
    }

    /// <summary>
    /// 创建图片元素。
    /// 已验证 API: Picture(string fileName), Bounds/Width/Height。
    /// </summary>
    private static void CreateImageElement(Slide slide, ElementData data, string assetsDir)
    {
        if (string.IsNullOrWhiteSpace(data.Src)) return;

        var imagePath = ResolveAssetPath(assetsDir, data.Src);
        if (!File.Exists(imagePath))
        {
            Log($"图片文件不存在: {imagePath}");
            return;
        }

        try
        {
            var fileName = TryAddResource(imagePath) ?? imagePath;
            double x = data.X.GetValueOrDefault(100);
            double y = data.Y.GetValueOrDefault(100);
            double w = data.Width.GetValueOrDefault(400);
            double h = data.Height.GetValueOrDefault(260);

            var picture = new Picture(fileName)
            {
                Bounds = new Rect(x, y, w, h),
                Width = w,
                Height = h
            };

            slide.Add(picture);
            Log($"图片插入成功: id={data.Id}, src={data.Src}, file={fileName}, bounds=({x},{y},{w},{h})");
        }
        catch (Exception ex)
        {
            Log($"图片插入失败: id={data.Id}, src={data.Src}, path={imagePath}, error={ex}");
        }
    }

    /// <summary>
    /// 创建形状元素。
    /// 已验证 API: ShapeElement(ShapeType)
    /// </summary>
    private static void CreateShapeElement(Slide slide, ElementData data)
    {
        var shapeType = ParseShapeType(data.ShapeType);
        var shapeElement = new ShapeElement(shapeType);

        double x = data.X.GetValueOrDefault(100);
        double y = data.Y.GetValueOrDefault(100);
        double w = data.Width.GetValueOrDefault(200);
        double h = data.Height.GetValueOrDefault(100);
        shapeElement.Bounds = new Rect(x, y, w, h);

        // 填充和边框（具体属性名需运行时验证）
        // if (!string.IsNullOrEmpty(data.Fill)) shapeElement.Fill = ParseBrush(data.Fill);
        // if (!string.IsNullOrEmpty(data.Stroke)) shapeElement.Stroke = ParseBrush(data.Stroke);

        slide.Add(shapeElement);
    }

    // ═══════════════════════════════════════════════════
    // 辅助方法
    // ═══════════════════════════════════════════════════

    /// <summary>
    /// 获取当前 Board（画板）对象。
    /// Board 是 Slide 的容器，负责页面的增删和导航。
    /// 通过 EN.EditingBoardApi.Board 获取。
    /// </summary>
    private static Board? GetBoard()
    {
        try
        {
            // 从 EN.EditingBoardApi 实例获取 Board 属性
            var api = EN.EditingBoardApi;
            if (api is null) return null;

            var boardProp = api.GetType().GetProperty("Board");
            if (boardProp is null) return null;

            return boardProp.GetValue(api) as Board;
        }
        catch
        {
            return null;
        }
    }

    private static string ResolveAssetPath(string assetsDir, string src)
    {
        if (Path.IsPathRooted(src)) return src;

        // 去掉 src 中已有的 assets/ 前缀，避免 assets/assets/ 重复
        var normalizedSrc = src.Replace('/', Path.DirectorySeparatorChar).Replace('\\', Path.DirectorySeparatorChar);
        if (normalizedSrc.StartsWith("assets", StringComparison.OrdinalIgnoreCase))
            normalizedSrc = normalizedSrc["assets".Length..].TrimStart(Path.DirectorySeparatorChar);

        return Path.GetFullPath(Path.Combine(assetsDir, normalizedSrc));
    }

    private static string? TryAddResource(string imagePath)
    {
        try
        {
            var resourcePath = EN.EditingBoardApi?.AddResource(imagePath);
            if (!string.IsNullOrWhiteSpace(resourcePath) && resourcePath != imagePath)
            {
                Log($"图片资源已加入课件: source={imagePath}, resource={resourcePath}");
                return resourcePath;
            }
        }
        catch (Exception ex)
        {
            Log($"AddResource 失败，直接用原始路径: {ex.Message}");
        }

        return null;
    }

    private static ShapeType ParseShapeType(string? type)
    {
        return type?.ToLowerInvariant() switch
        {
            "rectangle" => ShapeType.Rectangle,
            "line" => ShapeType.Line,
            _ => ShapeType.Rectangle,
        };
    }

    private static Brush? ParseBrush(string? color)
    {
        if (string.IsNullOrWhiteSpace(color)) return null;
        try
        {
            return (Brush)new BrushConverter().ConvertFromString(color)!;
        }
        catch
        {
            return null;
        }
    }

    private static void Log(string message)
    {
        try
        {
            var logPath = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "MrePlugin.log");
            File.AppendAllText(logPath, $"{DateTime.Now:HH:mm:ss.fff} [MreProcessor] {message}{Environment.NewLine}");
        }
        catch
        {
            // ignored
        }
    }
}
